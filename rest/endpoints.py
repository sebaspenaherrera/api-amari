# DEPENDENCIES
# ------------------------------------------------------------------------------
from fastapi import FastAPI, Query, Path, Body, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, Response
from typing import Union, Annotated
from starlette.responses import RedirectResponse
from utils.network import NetworkTools as net
from utils import utils
from utils.cli import Cli as cli
from auth.auth import fake_users_db, User, UserInDB, get_current_active_user, authenticate_user, create_access_token, Token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
import os
import pandas as pd
import subprocess
import asyncio


from utils.parser import Parser
from .models import * 

#from Stats import Stats
#from utils import *
#from sample_generator import SyntheticSample as synthetic

# OBJECTS
# ------------------------------------------------------------------------------
#stats = Stats(n_samples=n_samples)
description = """
Service API that exposes some functionalities. It has been designed in a modular manner, so you can add extra elements using the schema 🚀

## Generic

You can **send generic** Remote API commands (Syntaxis is the same as the established in AMARISOFT documentation) 
For more information, please refer to: [eNB/gNB remote API](https://tech-academy.amarisoft.com/lteenb.doc#Remote-API-1) and [Remote API](https://tech-academy.amarisoft.com/RemoteAPI.html)

## AMARI management
You will be able to:
* **Reset**, **Stop**, **Start** and get the **status** of the AMARI service.

## gNB

* **Modify** the cell gain, noise level, inactivity timer, PRB allocation, MCS, and get the stats of a gNB.
* Get the **configuration** of a gNB.
* Get the **channel** stats of a gNB (e.g. PDSCH, PUSCH, ...).
* **Reset** the logs of a gNB.
* Get the **stats** of a gNB.

## UE

* Get the stats of an specific UE connected to a gNB/eNB

## Network core
* Get the **configuration** of the **core** network (MME).
* Get the **stats** of the core network.
* Get the **gNBs attached** to the core network (MME).
* Get the **stats** of the **UEs** connected to the network core (MME).


## TODO
* **CPU Monitoring** (_not implemented_).
* **Services** (_not implemented_).
* **Core** (_not implemented_).
"""
app = FastAPI(title="Network-in-a-box API", version="1.0.0", summary="MobileNet API for Network-in-a-box service management", description=description)


#*************************************************************************************************************************************
#************************************************** DATASET CREATION *****************************************************************
#*************************************************************************************************************************************

@app.post("/start_recording_in_file", tags=["Dataset creation"])
async def start_recording_in_file(  current_user: Annotated[User, Depends(get_current_active_user)],
                           filename: Annotated[TestFileName, Body()]):
    '''**Starts** recording a data of an experiment in a file.

    The recording will be saved according to the parameters defined in the `filename` object.

    The recording will include /enb/get_stats, /enb/get_channel_stats, /core/get_stats and /ue/get_stats every `metrics_periodicity` seconds for a total duration of `duration` seconds.
    If duration is '-1', the recording will continue until the user stops it manually.

    Parameters:
    - filename: The name of the file to save the recording.
    - file_extension: The extension of the file to save the recording.
    - metrics_periodicity: The periodicity of the metrics collection.
    - duration: The duration of the recording.

    Returns:
    - A message indicating the success or failure of the recording start.
    '''

    config = filename.model_dump(by_alias=True)


    async def recording_task(filename: str, file_activation_path: str, metrics_periodicity: int, duration: int):
        if duration < 0:
            duration = None
        utils.write_file_raw(path=filename, content="[\n", mode='w')
        first = True
        while utils.check_file(file_activation_path):
            output_config = await get_eNB_config(current_user)
            #await asyncio.sleep(0.5)
            output_stats = await get_stats(current_user, ConfigStats())
            #await asyncio.sleep(0.5)
            output_channel_stats = await get_channel_stats(current_user, ConfigLogParser(channels=["PDSCH", "PUSCH"], layers={"PHY": {"level": "debug", "max_size": 1, "payload": False}}, max=1, min=1, short=True, allow_empty=True, discard_si=True))
            #await asyncio.sleep(0.5)
            output_core_stats = await get_core_stats(current_user)
            #await asyncio.sleep(0.5)
            output_ue_stats = await get_ue_stats(current_user, UeStats(stats=True))
            record = {
                "timestamp": str(utils.get_time()),
                "enb_config": output_config,
                "enb_stats": output_stats,
                "enb_channel_stats": output_channel_stats,
                "core_stats": output_core_stats,
                "ue_stats": output_ue_stats
            }
            print(f"Recording data to {filename} at {record['timestamp']}")
            print(record)
            # Append the record to the file
            
            if not first:
                utils.write_file_raw(path=filename, content=",\n", mode='a')
            else:
                first = False

            utils.write_file(path=filename, content=record, mode='a')
            await asyncio.sleep(metrics_periodicity)
            if duration:
                duration -= metrics_periodicity
                if duration <= 0:
                    os.remove(file_activation_path)
                    break

        # Remove the last comma and close the JSON array

        utils.write_file_raw(path=filename, content="\n]", mode='a')

    try:
        time_str = str(utils.get_time()).strip().replace(":","-")
        print(time_str)
        path_base = utils.get_local_data_path()
        utils.check_local_data_path(path_base)
        filename_full = f"{path_base}/{config['filename']}_{time_str}.{config['file_extension']}"
        file_activation_path = f"{path_base}/.recording_active"
        filename_json = f"{{'filename': '{filename_full}'}}"
        utils.write_file(path=file_activation_path, content=filename_json, mode='w')

        await recording_task(filename=filename_full, file_activation_path=file_activation_path, metrics_periodicity=config['metrics_periodicity'], duration=config['duration'])

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.get("/stop_recording_in_file", tags=["Dataset creation"])
async def stop_recording_in_file(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''**Stops** recording a data of an experiment in a file.

    Returns:
    - A message indicating the success or failure of the recording stop.
    '''

    try:
        path_base = utils.get_local_data_path()
        file_activation_path = f"{path_base}/.recording_active"
        utils.delete_file(file_activation_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop recording: {e}")


#*************************************************************************************************************************************
#*************************************************** AUTHORIZATION *******************************************************************
#*************************************************************************************************************************************

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """Login for access token.
    Parameters:
    - form_data: The form data containing the username and password.
    
    Returns:
    - Token: The access token and token type.
    Raises:
    - HTTPException: If the username or password is incorrect.
    """

    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

#*************************************************************************************************************************************
#******************************************** Internal ENDPOINTS (non-visible) *******************************************************
#*************************************************************************************************************************************

# DEFAULT ROUTE (Redirect home page)
@app.get("/", tags=["Default"], include_in_schema=False)
async def redirect_docs():
    """Redirect to the documentation page"""
    return RedirectResponse(url="/docs/")

# Favicon
favicon_path = os.path.join("./rest/static", "Mobilenet_sin-fondo-negro.svg")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    response = FileResponse(favicon_path, media_type="image/svg+xml")
    response.headers["Cache-Control"] = "public, max-age=86400"  # Cache for 1 day
    return response


#*************************************************************************************************************************************
#*************************************************** Generic ENDPOINTS ***************************************************************
#*************************************************************************************************************************************

@app.get("/get_help", tags=["Generic"])
async def get_help(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''**Provides** a list of **available messages** that can be sent to the AMARISOFT Remote API through the **generic request endpoint**.
    
    For more information, please refer to: [eNB/gNB remote API](https://tech-academy.amarisoft.com/lteenb.doc#Remote-API-1) and [Remote API](https://tech-academy.amarisoft.com/RemoteAPI.html)
    '''
    try:
        output = await cli.execute_command(entity="enb", message={"message": "help"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/{entity}", tags=['Generic'])
async def generic_request(  current_user: Annotated[User, Depends(get_current_active_user)],
                            entity: Annotated[str, Path] = "enb",
                            message: Annotated[dict, Body] = None):
    '''This generic endpoint serves a gateway for any **messages** described in the **[Remote API](https://tech-academy.amarisoft.com/RemoteAPI.html) documentation**
    
    Note that **only** API messages are accepted. This is not a CLI and should be used **only for experimental** purposes.

    Input parameters:
    * **entity**: The network element API (e.g. `enb`).
    * **message**: A json-like dictionary containing the message to be sent to the API (e.g. `{"message": "config-get", ...}`).

    If the command is executed successfully, the response's status value will be `True` and the **message** field will be the command sent.
    

    '''
    try:
        output = await cli.execute_command(entity=entity, message=message)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

# ********************************************************************************************************************************************
# ************************************************** NETWORK MANAGEMENT ENDPOINTS ************************************************************
# ********************************************************************************************************************************************

@app.get("/network/service_reset", tags=["Amari management"])
async def reset_service(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''**Reset** the AMARI service'''

    try:
        output = await cli.execute_cli_command(command=["service", "lte", "restart"])
        if output["status"] == 200:
            return {"status": True, "message": "Service reset successfully"}
        else:
            return {"status": False, "message": "Failed to reset service", "error": output["error"]}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.get("/network/service_status", tags=["Amari management"])
async def get_service_status(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''**Get** the **status** of AMARI service'''

    try:
        output = await cli.execute_cli_command(command=["service", "lte", "status"])
        if output["status"] == 200:
            return {"status": True, "message": "Service is running", "info": output["response"]}
        else:
            return {"status": False, "message": "Service is not running", "error": output["error"], "info": output["response"]}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.get("/network/service_stop", tags=["Amari management"])
async def stop_service(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''**Stops** the AMARI service'''

    try:
        output = await cli.execute_cli_command(command=["service", "lte", "stop"])
        if output["status"] == 200:
            return {"status": True, "message": "Service stopped successfully"}
        else:
            return {"status": False, "message": "Failed to stop service", "error": output["error"]}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.get("/network/service_start", tags=["Amari management"])
async def start_service(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''**Starts** the AMARI service'''

    try:
        output = await cli.execute_cli_command(command=["service", "lte", "start"])
        if output["status"] == 200:
            return {"status": True, "message": "Service started successfully"}
        else:
            return {"status": False, "message": "Failed to start service", "error": output["error"]}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

#*************************************************************************************************************************************
#*************************************************** gNB ENDPOINTS *******************************************************************
#*************************************************************************************************************************************

@app.get("/enb/get_config", tags=["gNB"])
async def get_eNB_config(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''Sends a **gNB configuration** get message to the Websocket AMARI API'''

    try:
        output = await cli.execute_command(entity="enb", message={"message": "config_get"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.post("/enb/set_gain", tags=["gNB"])
async def set_cell_gain(current_user: Annotated[User, Depends(get_current_active_user)],
                        ConfigGain: Annotated[ConfigGain, Body()]):
    '''Set the cell DL RF signal gain. The gain value is set in dB.
    
    The value of the key should be a dictionary containing the following fields:
    * **gain**: The gain value in dB (Theoretical range -200 to 0. API constrained `-30` to `0`).
    * **cell_id**: The cell ID (e.g., `1`, `2`).
    
    If the configuration is set, the **status** field of the response will be `True` and the **message** field will be `cell_gain`.'''
    
    configuration = ConfigGain.model_dump()
    configuration["message"] = "cell_gain"
    
    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/enb/set_noise_level", tags=["gNB"])
async def set_noise_level(current_user: Annotated[User, Depends(get_current_active_user)],
                          ConfigGain: Annotated[ConfigNoise, Body()]):
    '''Set the noise level (relative to the CRS --Cell Reference Signal-- level, i.e., -SNR) of a cell in the gNB. This functionality only works if **channel simulator*** is '**enabled**.
    
    The value of the key should be a dictionary containing the following fields:
    * **noise_level**: The noise level in dB (Negative value. API constrained `-30` to `0`).
    * **channel**: The channel ID (e.g., `0`, `1`) associated with the cell (Not equal than Cell ID).
    
    If the configuration is set, the **status** field of the response will be `True` and the **message** field will be `noise_level`.'''
    
    configuration = ConfigGain.model_dump()
    configuration["message"] = "noise_level"

    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:  
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.post("/enb/set_inactivity_timer", tags=["gNB"])
async def set_inactivity_timer(current_user: Annotated[User, Depends(get_current_active_user)],
                               configuration: Annotated[ConfigCellTimer, Body()]):
    '''Set the inactivity timer of the gNB. It is mandatory to specify the **cell ID** as the key (e.g., `"1"`, `"2"`) of the configuration dictionary.
    
    The value of the key should be a dictionary containing the following fields:
    * **inactivity_timer**: The inactivity timer in milliseconds (API constrained `0` to `900000`).
    
    If the configuration is set, the **status** field of the response will be `True` and the **message** field will be `config_set`.
    
    Note: The inactivity timer is used to determine when a UE is considered inactive and can be removed from the gNB.
    '''

    configuration = configuration.model_dump(by_alias=True)
    configuration["message"] = "config_set"
    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/enb/set_prb_alloc", tags=["gNB"])
async def set_prb_allocation(current_user: Annotated[User, Depends(get_current_active_user)],
                             prb_allocation: Annotated[ConfigCellAlloc, Body(openapi_examples=examples_config_cell_alloc,)]):
    '''Set the **Physical Resource Block (PRB)** allocation of the gNB. It is mandatory to specify the **cell ID** as the key (e.g., `"1"`, `"2"`) of the configuration dictionary.
    The value of the key should be a dictionary containing the following fields:
    * **pdsch_fixed_l_crb**: The number of PRBs allocated for PDSCH (DL).
    * **pdsch_fixed_rb_alloc**: A boolean indicating whether the PRB allocation is fixed or not.
    * **pdsch_fixed_rb_start**: The starting PRB for PDSCH (DL).
    * **pusch_fixed_l_crb**: The number of PRBs allocated for PUSCH (UL).
    * **pusch_fixed_rb_alloc**: A boolean indicating whether the PRB allocation is fixed or not.
    * **pusch_fixed_rb_start**: The starting PRB for PUSCH (UL).

    If the configuration is set, the **status** field of the response will be `True` and the **message** field will be `config_set`.

    Note: Both DL and UL PRB allocation can be set at the same time.
    '''


    configuration = prb_allocation.model_dump(by_alias=True)
    configuration["message"] = "config_set"

    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.post("/enb/set_mcs", tags=["gNB"])
async def set_mcs(current_user: Annotated[User, Depends(get_current_active_user)],
                  mcs: Annotated[ConfigCellMCS, Body(openapi_examples=examples_config_cell_mcs)]):
    '''Set the **Modulation and Coding Scheme (MCS)** of the gNB/eNB. It is mandatory to specify the **cell ID** as the key (e.g., `"1"`, `"2"`) of the configuration dictionary.
    The value of the key should be a dictionary containing the following fields:
    * **pdsch_mcs**: The MCS value for PDSCH (DL).
    * **pusch_mcs**: The MCS value for PUSCH (UL).
    
    If the configuration is set, the **status** field of the response will be `True` and the **message** field will be `config_set`.
    Note: Both DL and UL MCS can be set at the same time.
    '''

    configuration = mcs.model_dump(by_alias=True)
    configuration["message"] = "config_set"

    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/enb/get_stats", tags=["gNB"])
async def get_stats(current_user: Annotated[User, Depends(get_current_active_user)],
                    stats: Annotated[ConfigStats, Body()]):
    '''Get the **stats** of the **gNB**. 
    
    The value of the key should be a dictionary containing the following fields:
    * **samples**: The number of samples to be collected, if possible.
    * **rf**: A boolean indicating whether to collect RF stats or not.
    * **Initial_delay**: The initial delay in seconds before collecting the stats, by default 0.4 seconds.

    If the configuration is set, the **status** field of the response will be `True` and the **message** field will be `stats`.
    '''

    configuration = stats.model_dump(by_alias=True)
    configuration["message"] = "stats"

    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/enb/get_channel_stats", tags=["gNB"])
async def get_channel_stats(current_user: Annotated[User, Depends(get_current_active_user)],
                            log_stats: Annotated[ConfigLogParser, Body(openapi_examples=examples_log_parser)]):
    '''Get the gNB **channel stats** and information. It returns the parsed log messages stored in the gNB. It can be used to fetch the channel allocation.
    
    The value of the key should be a dictionary containing the following fields:
    * **layers**: The layers to be collected (e.g., `{"PHY": {"level": "debug", "max_size": 1, "payload": False}}`).
    * **max**: The maximum number of samples to be collected, if possible.
    * **min**: The minimum number of samples to be collected, if possible.
    * **short**: A boolean indicating whether to collect short stats or verbose (parsing not implemented yet).
    * **allow_empty**: A boolean indicating whether to allow empty stats or not.

    The following are optional:
    * **channels**: The channels to be collected (e.g., `["PDSCH", "PUSCH"]`. By default, PDSCH will be fetched ).
    * **discard_si**: A boolean indicating whether to discard SI (System Information) stats or not.
    * **samples**: The number of samples to be collected, if possible.
    * **Initial_delay**: The initial delay in seconds before collecting the stats, by default 0.7 seconds.
    * **timeout**: The timeout in seconds for collecting the stats.
    * **start_timestamp**: The start timestamp for collecting the stats.
    * **end_timestamp**: The end timestamp for collecting the stats.
    * **ue_id**: The ID of the UE (e.g., `1`, `2`). If UE not found, it will return an empty list.
    * **rnti**: The RNTI (Radio Network Temporary Identifier) of the UE (e.g., `1`, `2`). If UE not found, it will return an empty list.
    
    If the configuration is set, the **status** field of the response will be `True` and the **message** field will be `log_get`.
    '''

    configuration = log_stats.model_dump(by_alias=True, exclude_unset=True)
    configuration["message"] = "log_get"

    if configuration["discard_si"]:
        configuration.pop("discard_si")
        discard_si = True
    else:
        discard_si = False

    if configuration["channels"]:
        channels = configuration["channels"]
        configuration.pop("channels")

    try:
        output = await cli.execute_command(entity="enb", message=configuration)

        if output:
            pdsch_messages = Parser.extract_channel_log_messages(log_data=output, discard_si=discard_si, channel=channels)
            return {"status": True, "message": "log_get", "response": pdsch_messages}
        return {"status": False, "message": "log_get", "response": "No logs found"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.get("/enb/reset_log", tags=["gNB"])
async def reset_log_amari(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''**Resets** the **logs** of the gNB. This will clear all the logs stored in the gNB.'''

    try:
        output = await cli.execute_command(entity="enb", message={"message": "log_reset"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/ue/get_stats", tags=["UE"])
async def get_ue_stats(current_user: Annotated[User, Depends(get_current_active_user)],
                       stats: Annotated[UeStats, Body()]):
    '''**Get** the **stats** of an **UE** connected to a eNB/gNB
    The value of the key may be a dictionary containing the following fields:
    * **ue_id**: The ID of the UE (e.g., `1`, `2`).
    * **stats**: A boolean indicating whether to collect stats or not.
    
    If the configuration is set, the **status** field of the response will be `True` and the **message** field will be `ue_get`.
    
    Note: The field `ue_id` is optional. If not specified, the stats of all UEs will be collected.'''

    configuration = stats.model_dump(by_alias=True, exclude_unset=True)
    configuration["message"] = "ue_get"

    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

# **************************************************************************************************************************************
# ************************************************** NETWORK CORE ENDPOINTS ************************************************************
# ************************************************************************************************************************************** 

@app.get("/core/get_config", tags=["Network core"])
async def get_core_config(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''Get the configuration of the core network (MME)'''

    try:
        output = await cli.execute_command(entity="mme", message={"message": "config_get"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.get("/core/get_stats", tags=["Network core"])
async def get_core_stats(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''Get the stats of the core network (MME)'''

    try:
        output = await cli.execute_command(entity="mme", message={"message": "stats"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.get("/core/get_attached_gnb", tags=["Network core"])
async def get_attached_gnb(current_user: Annotated[User, Depends(get_current_active_user)]):
    '''Get the gNBs attached to the core network (MME)'''

    try:
        output = await cli.execute_command(entity="mme", message={"message": "ng_ran"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    
    
@app.post("/core/get_ue", tags=["Network core"])
async def get_ue(current_user: Annotated[User, Depends(get_current_active_user)],
                 ue: Annotated[UeCore, Body()]):
    '''Get the stats of the UEs connected to the network core (MME). It is possible to filter by **IMSI (field "imsi")** or **IMEI (i.e., "imei")**. 
    If UE not found, it will return an empty list.'''

    configuration = ue.model_dump(by_alias=True, exclude_unset=True)
    configuration["message"] = "ue_get"

    try:
        output = await cli.execute_command(entity="mme", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    


    


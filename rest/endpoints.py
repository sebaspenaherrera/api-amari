# DEPENDENCIES
# ------------------------------------------------------------------------------
from fastapi import FastAPI, Query, Path, Body, HTTPException
from fastapi.responses import FileResponse, Response
from typing import Union, Annotated
from starlette.responses import RedirectResponse
from utils.network import NetworkTools as net
from utils.cli import Cli as cli
import os
import pandas as pd
import subprocess

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
async def get_help():
    '''**Provides** a list of **available messages** that can be sent to the AMARISOFT Remote API through the **generic request endpoint**.
    
    For more information, please refer to: [eNB/gNB remote API](https://tech-academy.amarisoft.com/lteenb.doc#Remote-API-1) and [Remote API](https://tech-academy.amarisoft.com/RemoteAPI.html)
    '''
    try:
        output = await cli.execute_command(entity="enb", message={"message": "help"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/{entity}", tags=['Generic'])
async def generic_request(
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
async def reset_service():
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
async def get_service_status():
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
async def stop_service():
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
async def start_service():
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
async def get_eNB_config():
    '''Sends a **gNB configuration** get message to the Websocket AMARI API'''

    try:
        output = await cli.execute_command(entity="enb", message={"message": "config_get"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.post("/enb/set_gain", tags=["gNB"])
async def set_cell_gain(ConfigGain: Annotated[ConfigGain, Body()]):
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
async def set_noise_level(ConfigGain: Annotated[ConfigNoise, Body()]):
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
async def set_inactivity_timer(configuration: Annotated[ConfigCellTimer, Body()]):
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
async def set_prb_allocation(prb_allocation: Annotated[ConfigCellAlloc, Body(openapi_examples=examples_config_cell_alloc,)]):
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
async def set_mcs(mcs: Annotated[ConfigCellMCS, Body(openapi_examples=examples_config_cell_mcs)]):
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
async def get_stats(stats: Annotated[ConfigStats, Body()]):
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
async def get_channel_stats(log_stats: Annotated[ConfigLogParser, Body(openapi_examples=examples_log_parser)]):
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
async def reset_log_amari():
    '''**Resets** the **logs** of the gNB. This will clear all the logs stored in the gNB.'''

    try:
        output = await cli.execute_command(entity="enb", message={"message": "log_reset"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/ue/get_stats", tags=["UE"])
async def get_ue_stats(stats: Annotated[UeStats, Body()]):
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
async def get_core_config():
    '''Get the configuration of the core network (MME)'''

    try:
        output = await cli.execute_command(entity="mme", message={"message": "config_get"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.get("/core/get_stats", tags=["Network core"])
async def get_core_stats():
    '''Get the stats of the core network (MME)'''

    try:
        output = await cli.execute_command(entity="mme", message={"message": "stats"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.get("/core/get_attached_gnb", tags=["Network core"])
async def get_attached_gnb():
    '''Get the gNBs attached to the core network (MME)'''

    try:
        output = await cli.execute_command(entity="mme", message={"message": "ng_ran"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    
    
@app.post("/core/get_ue", tags=["Network core"])
async def get_ue(ue: Annotated[UeCore, Body()]):
    '''Get the stats of the UEs connected to the network core (MME). It is possible to filter by **IMSI (field "imsi")** or **IMEI (i.e., "imei")**. 
    If UE not found, it will return an empty list.'''

    configuration = ue.model_dump(by_alias=True, exclude_unset=True)
    configuration["message"] = "ue_get"

    try:
        output = await cli.execute_command(entity="mme", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    


    


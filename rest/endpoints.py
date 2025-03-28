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
app = FastAPI()


# ***************************************************** REST API ENDPOINTS ************************************************************

# DEFAULT ENDPOINT ***************************************************************
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
# ***********************************************************************************

@app.post("/{entity}", tags=['Generic'])
async def generic_request(
                            entity: Annotated[str, Path] = "enb",
                            message: Annotated[dict, Body] = None):
    '''Sends a message to Websocket AMARI API'''
    try:
        output = await cli.execute_command(entity=entity, message=message)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


# Get configuration eNB
@app.get("/enb/get_config", tags=["eNB"])
async def get_eNB_config():
    '''Execute CLI command to get configuration from Websocket AMARI API'''
    try:
        output = await cli.execute_command(entity="enb", message={"message": "config_get"})
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.post("/enb/set_gain", tags=["eNB"])
async def set_cell_gain(ConfigGain: Annotated[ConfigGain, Body()]):
    '''Set the gain of a cell in the eNB'''
    
    configuration = ConfigGain.model_dump()
    configuration["message"] = "cell_gain"
    
    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/enb/set_noise_level", tags=["eNB"])
async def set_noise_level(ConfigGain: Annotated[ConfigNoise, Body()]):
    '''Set the noise level of a cell in the eNB. This functionality only works if CHANNEL SIMULATOR is ENABLED'''
    
    configuration = ConfigGain.model_dump()
    configuration["message"] = "noise_level"

    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:  
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.post("/enb/set_inactivity_timer", tags=["eNB"])
async def set_inactivity_timer(configuration: Annotated[ConfigCellTimer, Body()]):
    '''Set the inactivity timer of the eNB'''

    configuration = configuration.model_dump(by_alias=True)
    configuration["message"] = "config_set"
    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/enb/set_dl_prb", tags=["eNB"])
async def set_prb_allocation(prb_allocation: Annotated[ConfigCellPRB, Body()]):
    '''Set the PRB allocation of the eNB'''

    configuration = prb_allocation.model_dump(by_alias=True)
    configuration["message"] = "config_set"

    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/enb/set_dl_mcs", tags=["eNB"])
async def set_dl_mcs(dl_mcs: Annotated[ConfigCellDLMCS, Body()]):
    '''Set the DL MCS of the eNB'''

    configuration = dl_mcs.model_dump(by_alias=True)
    configuration["message"] = "config_set"

    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.post("/enb/set_ul_mcs", tags=["eNB"])
async def set_ul_mcs(ul_mcs: Annotated[ConfigCellULMCS, Body()]):
    '''Set the UL MCS of the eNB'''

    configuration = ul_mcs.model_dump(by_alias=True)
    configuration["message"] = "config_set"

    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")


@app.post("/enb/get_stats", tags=["eNB"])
async def get_stats(stats: Annotated[ConfigStats, Body()]):
    '''Get the stats of the eNB'''

    configuration = stats.model_dump(by_alias=True)
    configuration["message"] = "stats"

    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    


@app.post("/enb/get_pdsch_stats", tags=["eNB"])
async def get_pdsch_stats(pdsch_stats: Annotated[ConfigPdschLog, Body()]):
    '''Get the PDSCH resource allocation stats of the eNB'''

    configuration = pdsch_stats.model_dump(by_alias=True, exclude_unset=True)
    configuration["message"] = "log_get"

    if configuration["discard_si"]:
        configuration.pop("discard_si")
        discard_si = True
    else:
        discard_si = False

    try:
        output = await cli.execute_command(entity="enb", message=configuration)

        if output:
            pdsch_messages = Parser.extract_pdsch_messages(output, discard_si)
            return pdsch_messages
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
    

@app.post("/ue/get_stats", tags=["UE"])
async def get_ue_stats(stats: Annotated[UeStats, Body()]):
    '''Get the stats of a UE connected to a eNB/gNB'''

    configuration = stats.model_dump(by_alias=True, exclude_unset=True)
    configuration["message"] = "ue_get"

    try:
        output = await cli.execute_command(entity="enb", message=configuration)
        return output
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e}")
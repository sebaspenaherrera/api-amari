# DEPENDENCIES
# ------------------------------------------------------------------------------
from fastapi import FastAPI, Query, Path, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response
from typing import Union, Annotated
from utils.network import NetworkTools as net
import os
import asyncio
import websockets
import pandas as pd
import subprocess

#from models import SessionStats, example_POST_testbed, SampleStats, example_POST_demo

#from Stats import Stats
#from utils import *
#from sample_generator import SyntheticSample as synthetic

# OBJECTS
# ------------------------------------------------------------------------------
#stats = Stats(n_samples=n_samples)
app = FastAPI()

# FUNCTIONS
async def execute_command(entity: str, message: dict):
    """Runs the CLI command with a dynamic message."""
    command = ["./ws.js", entity, message]
    working_directory = "/root/lteenb-linux-2024-12-13"
    
    try:
        result = subprocess.run(command, cwd=working_directory, capture_output=True, text=True, check=True)
        return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr or str(e)}

# ROUTES
# ------------------------------------------------------------------------------
@app.get("/")
async def read_root():
    return {"Hello": "World"}

# Favicon
favicon_path = os.path.join("./rest/static", "Mobilenet_sin-fondo-negro.svg")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    response = FileResponse(favicon_path, media_type="image/svg+xml")
    response.headers["Cache-Control"] = "public, max-age=86400"  # Cache for 1 day
    return response

# Generic GET endpoint
@app.get("/get", tags=['Generic'])
async def generic_get(ip: Annotated[str, Query] = '192.168.159.160',
                      port: Annotated[int, Query(ge=1)] = 5000,
                      resource: Annotated[str, Query] = None):
    
    data, status, reason = await net.configure_http_request(request_type='GET', host_address=ip, port=port, resource=resource)
    await net.process_http_response(response=data, status=status, reason=reason)
    
    return status


# Get configuration
@app.get("/enb/get_config", tags=["eNB"])
async def get_eNB_config():
    '''Execute CLI command to get configuration from Websocket AMARI API'''
    output = await execute_command(entity="enb", message={"message": "config_get"})
    return output
# DEPENDENCIES
# ------------------------------------------------------------------------------
from fastapi import FastAPI, Query, Path, Body
from fastapi.responses import FileResponse, Response
from typing import Union, Annotated
import os
import pandas as pd
#from models import SessionStats, example_POST_testbed, SampleStats, example_POST_demo

#from Stats import Stats
#from utils import *
#from sample_generator import SyntheticSample as synthetic

# OBJECTS
# ------------------------------------------------------------------------------
#stats = Stats(n_samples=n_samples)
app = FastAPI()


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
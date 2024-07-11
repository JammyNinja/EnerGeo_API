# import requests
import json
import os
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse #returning regional image

from api.current import current_energy_generation
from api.historical import get_historical_output
from api.geo import geo_static_image, carbon_intensity_live_geodict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

this_folder = os.path.dirname(__file__)
path_to_data = os.path.join(this_folder, "..", "data")

# Define a root `/` endpoint
@app.get('/')
def index():
    return {'ok': True, "docs to see endpoints" : "/docs"}

@app.get('/current')
def get_current_generation_output():
    return current_energy_generation()

@app.get('/historical')
def get_historical():
    return get_historical_output()

@app.get('/geo/image_static')
async def geo_get_static_image():
    geo_filepath = geo_static_image()
    print("serving regional carbon intensity data from local", geo_filepath)
    return FileResponse(geo_filepath)

@app.get('/geo/carbon_intensity_geojson')
def geo_carbon_as_geo_dict():
    return carbon_intensity_live_geodict()

def cache_locally():
    """code to save locally, untested for compatibility with other functions"""
    # filename = "cache_live_response.json"
    # this_folder = os.path.dirname(__file__)
    # path_to_data = os.path.join(this_folder, "..", "data")
    # filepath = os.path.join(path_to_data, filename)
    # # with open(filepath, 'w') as file_cache_out:
    # #     json.dump(response, file_cache_out)
    # with open(filepath, 'r') as file_cache_in:
    #     response = json.load(file_cache_in)
    #     print(response)
    return None

if __name__ == "__main__":
    # exported()
    # query_elexon_api()
    # geo_test()
    # print(get_current())
    pass

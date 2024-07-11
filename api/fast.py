# import requests
import json
import os
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse #returning regional image

from api.current import current_energy_generation
from api.historical import get_historical_output

from api.geo import geo_static_image
from api.geo import solar_generation_live_geodict, carbon_intensity_live_geodict
from api.geo import geo_all_regional_live_geodict

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

@app.get('/test')
def try_args(user_input):
    return {'input_was' : user_input}


@app.get('/current')
def get_current_generation_output():
    return current_energy_generation()

@app.get('/historical')
def get_historical():
    return get_historical_output()

@app.get('/geo/image_static')
async def geo_get_static_image():
    geo_filepath = geo_static_image()
    print("serving regional carbon intensity data as image stored at", geo_filepath)
    return FileResponse(geo_filepath)

@app.get('/geo/regional/all')
def get_all_regional_data():
    return geo_all_regional_live_geodict()

@app.get('/geo/regional/carbon_intensity')
def get_geo_carbon_data_only():
    return carbon_intensity_live_geodict()

@app.get('/geo/regional/solar_generation')
def get_geo_solar_data_only():
    return solar_generation_live_geodict()

@app.get('/geo/get_core_geojson')
def serve_local_geo():
    from api.geo import local_geo_filepath
    print("serving local geojson")
    return FileResponse(local_geo_filepath)

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

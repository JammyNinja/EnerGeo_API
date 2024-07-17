# import requests
import json
import os
import pandas as pd
import time #for deleting old images
from pprint import pprint

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse #returning regional image

from api.current import current_energy_generation
from api.historical import get_historical_output

from api.geo import geo_static_image
from api.geo import solar_generation_live_geodict, carbon_intensity_live_geodict
from api.geo import geo_all_regional_live_geodict

#from api.agent.setup_environment import set_environment_variables
from api.agent.simple_langgraph import test_import, call_weather_app

# set_environment_variables("LangGraph Basics")

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
path_to_agent_images = os.path.join(this_folder, "agent", "images")

# Define a root `/` endpoint
@app.get('/')
def index():
    return {'ok': True, "docs to see endpoints" : "/docs"}

@app.get('/test')
async def try_args(user_input):
    print("Calling weather app with user input: ", user_input)
    prompt = f"""
        Gernerate an image of the current weather conditions in {user_input}.
        Please output a JSON style object with the following keys:
            "image_url", "image_path"
        Make sure they are sourrounded by curly braces.
    """

    agent_output = call_weather_app(prompt)
    # print("agent output:", agent_output)

    api_output = process_agent_output(agent_output)

    #handle obsolete images
    delete_surplus_images()

    #api_output is dict with image_url and image_path
    #return api_output
    return FileResponse(api_output["image_path"])

def process_agent_output(agent_output):
    """extract the relevant dictionary from string by grabbing curly braces"""
    print("original agent output", agent_output)
    agent_dict_out = '{'+ agent_output.split('}')[0].split('{')[1] + '}'

    print("extracted dictionary from agent:", agent_dict_out)
#     print(type(agent_dict_out))
    out_dict = json.loads(agent_dict_out.replace("'", '"'))

    return out_dict

def delete_surplus_images(limit=5):
    """
        keeps 5 most recent images
    """

    #define image directory defined at top of file
    # current_time = time.time()
    all_image_files = []

    for image_name in os.listdir(path_to_agent_images):
        # print(image_name)
        image_path = os.path.join(path_to_agent_images, image_name)
        all_image_files.append(image_path)

    # Sort them by modification time (most recent first)
    sorted_images = sorted(all_image_files, key=os.path.getmtime, reverse=True)
    # print(sorted_images)

    for img_path in sorted_images[limit:]:
        try:
            os.remove(img_path)
            print(f"Deleted: {os.path.basename(img_path)}")
        except Exception as e:
            print(f"Error deleting {os.path.basename(img_path)}: {e}")

    # pprint(f"Kept files: {''.join(sorted_images[:5])}")
    print("kept files:")
    pprint(sorted_images[:limit])


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
    delete_old_images()

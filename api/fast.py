import requests
import json
import os
from fastapi import FastAPI



import pandas as pd

# from api.csv_test import exported #calling from makefile, must prefix with api.

#geo
import geopandas as gpd
#use matplotlib backend, no need for display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a root `/` endpoint
@app.get('/')
def index():
    return {'ok': True, "docs" : "/docs"}

@app.get('/test')
def get_current_energy_production():
    """
        note that plurality may matter eg .loads() vs load() / dump(s)
    """

    filename = "test_current.json"
    this_folder = os.path.dirname(__file__)
    path_to_data = os.path.join(this_folder, "..", "data")
    filepath = os.path.join(path_to_data, filename)

    #load json from file
    with open(filepath) as file:
        data = json.load(file)
        print(data)

    test_var = {"test" : "TEST"}
    data.append(test_var)

    output = json.dumps(data)
    print(type(output))

    # return output
    return data

@app.get('/historical')
def query_local_csv(year=None):
    filename = "df_fuel_ckan.csv"
    this_folder = os.path.dirname(__file__)
    path_to_data = os.path.join(this_folder, "..", "data")
    filepath = os.path.join(path_to_data, filename)

    df = pd.read_csv(filepath)

    print("columns", df.columns)

    sources_list = ['GAS', 'COAL', 'NUCLEAR', 'WIND', 'HYDRO', 'IMPORTS','BIOMASS', 'OTHER', 'SOLAR']
    #convert to datetime for groupby
    df['DATETIME'] = pd.to_datetime(df.DATETIME)

    #sum over the years
    year_df = df.groupby(by=df["DATETIME"].dt.year)[sources_list].sum()

    #rename the index
    year_df.index.names = ["Year"]
    print(year_df)

    out = year_df.reset_index().to_dict(orient='records')

    # if year:
    #     out = out[int(year)]

    print(type(out))
    return out

@app.get('/current')
def query_elexon_api():
    url = "https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type/day-total?format=json"
    response = requests.get(url).json()

    l30_min = []
    l24_hrs = []

    for energy_type in response:
        l30_min.append({
            "type": energy_type['psrType'].upper(),
            "measure": energy_type['halfHourUsage']
        })

        l24_hrs.append({
            "type": energy_type['psrType'].upper(),
            "measure": energy_type['twentyFourHourUsage']
        })

    return [{"30_min": l30_min, "24_hours": l24_hrs}]


# @app.get('/test_package')
# def imported_func():
#     out = exported()
#     return out

def get_live_regional_data():
    url = "https://api.carbonintensity.org.uk/regional"
    response = requests.get(url).json()

    print(type(response))

def regional_response_to_df(response_regional):
    regions = response_regional['data'][0]['regions']

    rows = []
    for region in regions:
        region_id = region["regionid"]
        dno_region = region["dnoregion"]
        name = region["shortname"]
        intensity_forecast = region["intensity"]["forecast"]
        intensity_index = region["intensity"]["index"]

        row_dict = {
            "id" : region_id,
            "dno_region" : dno_region,
            "api_name" : name,
            "intensity_forecast" : intensity_forecast,
            "intensity_index" : intensity_index
        }

        for fuel in region["generationmix"]:
            fuel_name = fuel["fuel"]
            fuel_percentage = fuel["perc"]
            row_dict[fuel_name+"_perc"] = fuel_percentage

        rows.append(row_dict)

    return pd.DataFrame(rows)

@app.get('/test_geo')
def geo_test():
    print("geo testing")
    # filename = "dno_regions.geojson"
    filename= "national_grid_dno_regions_2024.geojson"
    this_folder = os.path.dirname(__file__)
    path_to_data = os.path.join(this_folder, "..", "data")
    filepath = os.path.join(path_to_data, filename)

    # Read the GeoJSON file
    uk_regions = gpd.read_file(filepath)
    print("file has been read")

    # live_data = get_live_regional_data()

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))

    print("plotting map")
    # Plot the map
    uk_regions.plot(ax=ax)

    # Remove axis
    ax.axis('off')

    # Add a title
    plt.title('UK Regions')

    out_filename = "out_test_2024.png"
    out_path = os.path.join(path_to_data, "output", out_filename )
    print("saving file")
    # Save the map as an image
    plt.savefig(out_path, dpi=300, bbox_inches='tight')

    # Display the map (optional)
    # plt.show()




if __name__ == "__main__":
    # exported()
    geo_test()
    # get_live_regional_data()

import geopandas as gpd
import pandas as pd
import os
import requests

url = "https://api.carbonintensity.org.uk/regional"

def get_api_regional_response():
    url = "https://api.carbonintensity.org.uk/regional"
    response = requests.get(url).json()
    regions = response['data'][0]['regions']
    return regions

def regional_response_to_df(response_regional):
    """
        parse API response into desired df, with columns:
        'id', 'dno_region', 'api_name', 'intensity_forecast', 'intensity_index',
       'biomass_perc', 'coal_perc', 'imports_perc', 'gas_perc', 'nuclear_perc',
       'other_perc', 'hydro_perc', 'solar_perc', 'wind_perc'
    """
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

def get_api_regions_as_df():
    regions = get_api_regional_response()
    regions_df = regional_response_to_df(regions)
    return regions_df

def process_local_geojson(filename = "national_grid_dno_regions_2024.geojson"):
    # filename = "national_grid_dno_regions_2024.geojson"
    path_to_data = os.path.join( "..", "data")
    filepath = os.path.join(path_to_data, filename)

    # Read the GeoJSON file
    uk_regions_2024 = gpd.read_file(filepath)

    #rename some areas so we can sort alphabetically and match api region id to region ids from file
    rename_geojson_areas_to_api = {"Southern England":  "South England", "South and Central Scotland" : "South Scotland"}
    uk_regions_2024["Area"] = uk_regions_2024["Area"].map(lambda x: rename_geojson_areas_to_api.get(x,x) )

    #get sample api response to lineup the ids
    region_response_df = get_api_regions_as_df()
    #line up the ids from file + api
    lineup_file_df = uk_regions_2024.sort_values(by="Area").rename(columns={"ID" : "geojson_id", "Area" : "geojson_name"}).reset_index(drop=True)
    lineup_api_df = region_response_df.iloc[:14, :3].sort_values(by="api_name").rename(columns={"id":"api_id"}).reset_index(drop=True)
    lineup_df = pd.concat([lineup_file_df,lineup_api_df], axis=1)[["geojson_id","api_id", "geojson_name", "api_name"]]
    #create id mapping dict
    id_map_dict = {}
    for geo_id, api_id,api_name in zip(lineup_df.geojson_id, lineup_df.api_id,lineup_df.api_name):
        print(f"Region: {api_name}. Geojson id: {geo_id} -> Api_id: {api_id}" )
        id_map_dict[geo_id] = [api_id, api_name]

    #execute the mapping of IDs
    uk_regions_2024["ID"] = uk_regions_2024["ID"].map(lambda id : id_map_dict[id][0])

    #sort by ID before save, for sanity
    uk_regions_2024 = uk_regions_2024.sort_values(by="ID")

    #gdf.to_file('dataframe.geojson', driver='GeoJSON')  

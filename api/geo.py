import geopandas as gpd
import pandas as pd
import os
import requests

#use matplotlib backend, no need for display to save image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

url = "https://api.carbonintensity.org.uk/regional"
path_to_geodata = os.path.join(os.path.dirname(__file__), "..", "data", "geo")

def get_api_regional_response():
    url = "https://api.carbonintensity.org.uk/regional"
    print("Getting current regional carbon intensity from: ", url)
    response = requests.get(url).json()
    regions = response['data'][0]['regions']
    return regions

def regional_response_to_df(regions):
    """
        parse API response into desired df, with columns:
        'id', 'dno_region', 'api_name', 'intensity_forecast', 'intensity_index',
       'biomass_perc', 'coal_perc', 'imports_perc', 'gas_perc', 'nuclear_perc',
       'other_perc', 'hydro_perc', 'solar_perc', 'wind_perc'
    """
    print("converting api response to dataframe...")
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
            "carbon_intensity_forecast" : intensity_forecast,
            "carbon_intensity_index" : intensity_index
        }

        for fuel in region["generationmix"]:
            fuel_name = fuel["fuel"]
            fuel_percentage = fuel["perc"]
            row_dict[fuel_name+"_perc"] = fuel_percentage

        rows.append(row_dict)
    
    return pd.DataFrame(rows)

def get_api_regions_as_df():
    """
        Orchestrates the API call and coversion to df functions
    """

    regions = get_api_regional_response()
    regions_df = regional_response_to_df(regions)
    return regions_df

#used to programmatically map geojson region_ids to API region ids
def process_local_geojson(filename_in = "national_grid_dno_regions_2024.geojson", filename_out="uk_dno_regions_2024.geojson"):
    """
        rename the IDs from downloaded geojson file with IDs as served by API
        only needs to be run once...
    """
    filepath_in = os.path.join(path_to_geodata, filename_in)
    filepath_out = os.path.join(path_to_geodata, filename_out)
    print(f"processing file: {filepath_in}")

    # Read the GeoJSON file
    uk_regions_2024 = gpd.read_file(filepath_in)

    #rename some areas so we can sort alphabetically and match api region id to region ids from file
    rename_geojson_areas_to_api = {"Southern England":  "South England", "South and Central Scotland" : "South Scotland"}
    uk_regions_2024["Area"] = uk_regions_2024["Area"].map(lambda x: rename_geojson_areas_to_api.get(x,x) )

    #get sample api response to lineup the ids
    region_response_df = get_api_regions_as_df()

    #line up the ids from file + api
    lineup_file_df = uk_regions_2024.sort_values(by="Area").rename(columns={"ID" : "geojson_id", "Area" : "geojson_name"}).reset_index(drop=True)
    lineup_api_df = region_response_df.iloc[:14, :3].sort_values(by="api_name").rename(columns={"id":"api_id"}).reset_index(drop=True)
    lineup_df = pd.concat([lineup_file_df,lineup_api_df], axis=1)[["geojson_id","api_id", "geojson_name", "api_name"]]
    #create id mapping dict thanks to lineup_df
    id_map_dict = {}
    for geo_id, api_id,api_name in zip(lineup_df.geojson_id, lineup_df.api_id,lineup_df.api_name):
        print(f"Region: {api_name}. Geojson id: {geo_id} -> Api_id: {api_id}" )
        id_map_dict[geo_id] = [api_id, api_name]

    #execute the mapping of IDs
    uk_regions_2024["ID"] = uk_regions_2024["ID"].map(lambda id : id_map_dict[id][0])

    #sort by ID before save, for sanity
    uk_regions_2024 = uk_regions_2024.sort_values(by="ID")

    print(f"saving processed file to: {filepath_out}")
    uk_regions_2024.to_file(filepath_out)
    return uk_regions_2024

def carbon_intensity_live_geodf():
    #firstly get the geopandas with regions, to be completed with live data
    geojson_filename = "uk_dno_regions_2024.geojson"
    filepath = os.path.join(path_to_geodata, geojson_filename)

    print("loading uk energy regions from file", filepath)
    uk_regions = gpd.read_file(filepath)

    #get the live data
    uk_live_df = get_api_regions_as_df()

    cols_to_drop = ["Name", "DNO","DNO_Full", "id", "api_name", "dno_region"]

    #merge them on their respective id columns
    return uk_regions.merge(uk_live_df, how="inner", left_on="ID", right_on="id").drop(columns=cols_to_drop)

def carbon_intensity_live_geodict():

    geodf = carbon_intensity_live_geodf()
    print("returning as geodict")
    return geodf.to_geo_dict(drop_id=True)

def geo_plot_matplotlib_save_local(filename_out = "carbon_intensity_regional.png"):
    """
        Fetch live carbon intensity data and plot. save locally in data/output folder
    """

    carbon_regions = carbon_intensity_live_geodf()

    fig, ax = plt.subplots(figsize=(6,10))
    ax.axis('off')
    carbon_regions.plot(ax=ax, column="carbon_intensity_index", legend=True, legend_kwds={"loc" : "upper right"}, cmap='viridis')
    plt.title('UK Regions carbon intensity')

    out_path = os.path.join(path_to_geodata, filename_out )
    print("saving regional carbon intensity data to", out_path)

    # Save the map as an image
    plt.savefig(out_path, dpi=300, bbox_inches='tight')

    return out_path

def geo_test_file():
    print("generating regional plot")
    regional_filepath = geo_plot_matplotlib_save_local()

    return regional_filepath

if __name__ == "__main__":
    # process_local_geojson()
    # geo_plot_matplotlib_save_local()
    pass

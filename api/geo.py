import geopandas as gpd
import pandas as pd
import os
import requests

#use matplotlib backend, no need for display to save image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

carbon_intensity_url = "https://api.carbonintensity.org.uk/regional"
solar_generation_url = "https://api.solar.sheffield.ac.uk/pvlive/api/v4/pes/14"

path_to_geodata = os.path.join(os.path.dirname(__file__), "..", "data", "geo")
local_geo_filename = "uk_dno_regions_2024_lonlat.geojson"
local_geo_filepath = os.path.join(path_to_geodata, local_geo_filename)

#process base geojson
#used to programmatically map geojson region_ids to API region ids
#now all ids/mapping stored in there. All future data to be joined to this.
def process_local_geojson(filename_out, filename_in = "national_grid_dno_regions_2024.geojson"):
    """
        rename the IDs from downloaded geojson file with IDs as served by API
        only needs to be run once...
    """
    # filename_out = geo_file_prod
    filepath_in = os.path.join(path_to_geodata, filename_in)
    filepath_out = os.path.join(path_to_geodata, filename_out)
    print(f"processing file: {filepath_in}")

    # Read the GeoJSON file
    uk_regions_2024 = gpd.read_file(filepath_in)

    #rename some areas so we can sort alphabetically and match api region id to region ids from file
    rename_geojson_areas_to_api = {"Southern England":  "South England", "South and Central Scotland" : "South Scotland"}
    uk_regions_2024["Area"] = uk_regions_2024["Area"].map(lambda x: rename_geojson_areas_to_api.get(x,x) )

    #get sample api response to lineup the ids
    print("calling carbon intensity api for sample region ids")
    region_response_df = carbon_intensity_live_df()

    #line up the ids from file + api
    lineup_file_df = uk_regions_2024.sort_values(by="Area").rename(columns={"ID" : "geojson_id", "Area" : "geojson_name"}).reset_index(drop=True)
    lineup_api_df = region_response_df.iloc[:14, :3].sort_values(by="api_name").reset_index(drop=True)

    lineup_df = pd.concat([lineup_file_df,lineup_api_df], axis=1)[["geojson_id","carbon_region_id", "geojson_name", "api_name"]]
    #create id mapping dict thanks to lineup_df
    id_map_dict = {}

    for geo_id, geo_name, api_id,api_name in zip(lineup_df.geojson_id, lineup_df.geojson_name, lineup_df.carbon_region_id,lineup_df.api_name):
        print(f"Geo name | Api name: {geo_name} | {api_name} - Geojson id | Api id: {geo_id} -> {api_id}" )
        id_map_dict[geo_id] = [api_id, api_name]

    #store the original ids in new column as will be useful later
    uk_regions_2024["pes_id"] = uk_regions_2024["ID"]

    #execute the mapping of IDs
    uk_regions_2024["ID"] = uk_regions_2024["ID"].map(lambda id : id_map_dict[id][0])

    #rename Area -> Region and sort by ID
    uk_regions_2024 = uk_regions_2024.sort_values(by="ID").rename(columns={"Area" : "Region"})

    #convert co-ordinates to longitude and latitude
    print("Converting co-ordinates to longitude latitude projection")
    uk_regions_2024_lonlat = convert_geodf_to_lonlat(uk_regions_2024)

    print(f"saving processed file to: {filepath_out}")
    uk_regions_2024_lonlat.to_file(filepath_out)
    return uk_regions_2024_lonlat

#helper for geojson processor
def convert_geodf_to_lonlat(geodf, lonlat_EPSG = 4326):
    """ projects the co-ordinates to lonlat
        GeoPandas projections
        https://geopandas.org/en/stable/docs/user_guide/projections.html
    """
    print("Co-ordinate Reference System before: ", geodf.crs)
    geodf_lonlat = geodf.to_crs(epsg=lonlat_EPSG)
    print("Co-ordinate Reference System after: ", geodf_lonlat.crs)
    return geodf_lonlat

#retrieve locally stored geojson as geodf
def get_regional_geojson():
    print("Loading uk energy regions from file", local_geo_filepath)
    return gpd.read_file(local_geo_filepath)


def get_api_carbon_regional_response(carbon_intensity_url = "https://api.carbonintensity.org.uk/regional"):
    print("Getting current regional carbon intensity from: ", carbon_intensity_url)
    response = requests.get(carbon_intensity_url).json()
    regions = response['data'][0]['regions']

    times = {
        "time_from" : response['data'][0]['from'],
        "time_to" :  response['data'][0]['to']
    }
    for region_dict in regions:
        region_dict['times'] = times

    return regions

def carbon_intensity_live_df():
    """
        Orchestrates the API call and coversion to df functions
    """
    regions = get_api_carbon_regional_response()

    def carbon_regional_response_to_df(regions):
        """
            parse API response into desired df, with columns:
            'id', 'dno_region', 'api_name', 'intensity_forecast', 'intensity_index',
        'biomass_perc', 'coal_perc', 'imports_perc', 'gas_perc', 'nuclear_perc',
        'other_perc', 'hydro_perc', 'solar_perc', 'wind_perc'
        """
        print("Converting carbon intensity api response to df...")
        rows = []
        for region in regions:
            region_id = region["regionid"]
            dno_region = region["dnoregion"]
            name = region["shortname"]
            intensity_forecast = region["intensity"]["forecast"]
            intensity_index = region["intensity"]["index"]

            time_from, time_to = region['times']['time_from'], region['times']['time_to']

            row_dict = {
                "carbon_region_id" : region_id,
                "dno_region" : dno_region,
                "api_name" : name,
                "carbon_intensity_forecast" : intensity_forecast,
                "carbon_intensity_index" : intensity_index,
                "carbon_time_from" : time_from,
                "carbon_time_to" : time_to
            }

            for fuel in region["generationmix"]:
                fuel_name = "generation_" + fuel["fuel"]
                fuel_percentage = fuel["perc"]
                row_dict[fuel_name+"_perc"] = fuel_percentage

            rows.append(row_dict)

        return pd.DataFrame(rows)

    regions_df = carbon_regional_response_to_df(regions)

    return regions_df

def solar_generation_live_df(solar_regions_list, extra_fields=True, printing=True):
    """
        Calls an api endpoint per region in solar_regions_list (14 regions)
        solar regions should correspond to those listed at:
        https://api.solar.sheffield.ac.uk/pvlive/api/v4/pes_list
    """
    base_url = f"https://api.solar.sheffield.ac.uk/pvlive/api/v4/pes/" #/4 for region_id 4

    #extra fields ctrl-f: Aggregated by PES region
    #doc: https://docs.google.com/document/d/e/2PACX-1vSDFb-6dJ2kIFZnsl-pBQvcH4inNQCA4lYL9cwo80bEHQeTK8fONLOgDf6Wm4ze_fxonqK3EVBVoAIz/pub
    extra_fields = ",".join([
        "bias_error", #estimate of Mean Normalised Bias Error
        "capacity_mwp", # estimate of total effective capacity
        "installedcapacity_mwp", #estimate of installed capacity Megawatt peak
        "lcl_mw", #lower confidence limit 90%
        "stats_error", #estimate of Mean Absolute Percent Error
        "ucl_mw", #upper cofidence limit (90%)
        "uncertainty_MW", #estimate of RMSE * effective capacity
        "site_count", #number of sites
        "updated_gmt", #latest update time of estimate
    ])
    if printing:
        print(f"Fetching solar API regional data from base url: {base_url}<region_id>")
        print("Extra fields:\n- ", "\n- ".join(extra_fields.split(',')) )
        print("Sample API url: ", f"{base_url}{solar_regions_list.iloc[0]}?extra_fields={extra_fields}")
        print(f"Fetching {len(solar_regions_list)} solar regions...")

    regions_solar_data = []
    for api_region_id in  solar_regions_list:
        region_url = base_url + str(api_region_id) + f"?extra_fields={extra_fields}"
        if printing:
            print(f"Fetching live solar data for pes region:", api_region_id)
        response=requests.get(region_url)

        if response.status_code == 200:
            region_data = response.json()
            region_dict = {f"solar_{k}":v for k,v in zip(region_data['meta'], region_data['data'][0])}
            regions_solar_data.append(region_dict)
        else:
            print(f"response not 200, for region_id: {api_region_id}", response.content)

    solar_live_data_df = pd.DataFrame(regions_solar_data)

    cols_rename = {
        # "datetime_gmt" : "solar_datetime_gmt",
        "solar_pes_id" : "solar_region_id",
        "solar_updated_gmt" : "solar_last_updated_gmt"
    }

    return solar_live_data_df.rename(columns=cols_rename)


def get_carbon_intensity_live_only():
    #firstly get the geopandas with regions, to be completed with live data
    uk_regions = get_regional_geojson()

    #get the live data
    carbon_df = carbon_intensity_live_df()

    # cols_to_drop = ["Name", "DNO","DNO_Full", "api_name", "dno_region"]
    #send almost all columns through since we're  getting carbon only
    cols_to_drop = ["api_name"]

    #merge them on their respective id columns

    out_df = pd.merge(left=uk_regions, right=carbon_df, how="inner",\
                      left_on="ID", right_on="carbon_region_id")

    return out_df.drop(columns=cols_to_drop)

def get_solar_generation_live_only():
    #contains mapping from id number to id letter (name)
    uk_regions_df = get_regional_geojson()

    solar_regions_list = uk_regions_df.sort_values(by="pes_id")["pes_id"]

    #contains live solar data indexed by id number (pes_id)
    solar_df = solar_generation_live_df(solar_regions_list, printing=True)

    out_df = pd.merge(left=uk_regions_df, right=solar_df, how="inner",
                      left_on="pes_id", right_on="solar_region_id")
    return out_df


def get_carbon_and_solar_regional_data():
    uk_energy_regions_df = get_regional_geojson()
    solar_regions_list = uk_energy_regions_df.sort_values(by="pes_id")["pes_id"]

    carbon_df = carbon_intensity_live_df()
    solar_df = solar_generation_live_df(solar_regions_list, extra_fields=True, printing=False)

    all_df = uk_energy_regions_df.merge(carbon_df, how="inner", left_on = "ID", right_on="carbon_region_id")\
                .merge(solar_df, how="inner", left_on="pes_id", right_on="solar_region_id")

    #choose columns
    return all_df


#api entrypoint
def carbon_intensity_live_geodict():
    carbon_geo_df = get_carbon_intensity_live_only()
    print("Returning carbon data as geodict")
    return carbon_geo_df.to_geo_dict(drop_id=True)
#api entrypoint
def solar_generation_live_geodict():
    solar_geo_df = get_solar_generation_live_only()
    print("Returning solar data as geodict")
    return solar_geo_df.to_geo_dict(drop_id=True)
#api entrypoint
def geo_all_regional_live_geodict():
    #add more if/when
    return get_carbon_and_solar_regional_data().to_geo_dict(drop_id=True)

#generate local image with live carbon data
def geo_plot_matplotlib_save_local(filename_out = "carbon_intensity_regional.png"):
    """
        Fetch live carbon intensity data and plot. save locally in data/output folder
    """

    carbon_regions = get_carbon_intensity_live_only()

    fig, ax = plt.subplots(figsize=(6,10))
    ax.axis('off')
    carbon_regions.plot(ax=ax, column="carbon_intensity_index", legend=True, legend_kwds={"loc" : "upper right"}, cmap='viridis')
    plt.title('UK Regions carbon intensity')

    out_path = os.path.join(path_to_geodata, filename_out )
    print("saving regional carbon intensity data to", out_path)

    # Save the map as an image
    plt.savefig(out_path, dpi=300, bbox_inches='tight')

    return out_path

#api entrypoint
def geo_static_image():
    """Generate and save an image
    returns filepath of that image for API to serve
    """
    print("Generating regional plot")
    regional_filepath = geo_plot_matplotlib_save_local()
    return regional_filepath

if __name__ == "__main__":
    process_local_geojson(filename_out=local_geo_filename)

    # process_local_geojson(filename_out = f"test_{local_geo_filename}")
    # geo_plot_matplotlib_save_local()
    # print(carbon_intensity_live_geodict())

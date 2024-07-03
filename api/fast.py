import requests
import json
import os
from fastapi import FastAPI
import pandas as pd


app = FastAPI()

# Define a root `/` endpoint
@app.get('/')
def index():
    return {'ok': True, 'test' : "tested"}

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

@app.get('/csv_local')
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

    # print(year_df[sources_list])
    out = year_df.reset_index().to_dict(orient='records')

    # if year:
    #     out = out[int(year)]

    print(type(out))
    return out

@app.get('/elexon_api')
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

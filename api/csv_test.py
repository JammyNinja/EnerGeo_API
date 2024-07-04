import pandas as pd
import os
import requests

def testing():
    """contains breakpoint!
        used for testing within container, without browser
    """

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
    #pandas 2 sums over all columns by default, even non numeric
    year_df = df.groupby(by=df["DATETIME"].dt.year)[sources_list].sum()

    # print(year_df[sources_list])
    out = year_df.to_dict(orient='index')

    print(type(out))

    breakpoint()

    return out

def test_live_api():
    url="https://live-json-first-y2qdisfueq-ew.a.run.app/current"
    response = requests.get(url).json()

    print (response)


def exported():
    return "hello from export"

if __name__ == "__main__":
    # testing()
    test_live_api()

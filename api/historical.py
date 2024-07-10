import os
import pandas as pd

from api.elements import elements_list, element_mappings

#constants - these could all be env?
filename = "df_fuel_ckan.csv"
path_to_data = os.path.join("data")

def get_df_from_csv(filename = "df_fuel_ckan.csv"):
    filepath = os.path.join(path_to_data, filename)
    return pd.read_csv(filepath)

def preprocess_df(df):
    #convert to datetime for groupby
    df['DATETIME'] = pd.to_datetime(df.DATETIME)

    #select only relevant columns
    sources_list = ['GAS', 'COAL', 'NUCLEAR', 'WIND', 'HYDRO','SOLAR','BIOMASS']#, 'IMPORTS', 'OTHER']
    df = df.set_index("DATETIME")[sources_list]

    rename_dict = {}
    for column in df.columns:
        for source, element in element_mappings.items():
            if column in source:
                rename_dict[column] = f"{column}_{element}"

    df = df.rename(columns=rename_dict)
    return df

def build_historical_output(df):
    yearly_df = df.groupby(df.index.year).sum()

    output = {}

    for year in yearly_df.index:
        year_data = {}
        for element in elements_list:
            elem_sources = [col for col in yearly_df if col.endswith(element)]
            sources = []
            for source in elem_sources:
                name = source.split('_')[0]
                value = yearly_df.loc[year][source]
                sources.append({"name" : name , "value" : value})
            year_data[element] = {"sources" : sources}
        output[year] = year_data

    return output

#called by api
def get_historical_output():
    hist_df = preprocess_df(get_df_from_csv())
    hist_out = build_historical_output(hist_df)

    return hist_out

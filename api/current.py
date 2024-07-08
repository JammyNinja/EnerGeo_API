import pandas as pd
from datetime import datetime
import pytz #for timezones

#define constants
four_elements = ["fire","air", "water", "earth"]
element_mappings = {
    "BIOMASS" : "fire",
    "NUCLEAR" : "fire",
    "SOLAR" : "fire",
    "FOSSIL OIL" : "earth",
    "FOSSIL HARD COAL" : "earth",
    "FOSSIL GAS" : "earth",
    "HYDRO PUMPED STORAGE" : "water",
    "HYDRO RUN-OF-RIVER AND POUNDAGE" : "water",
    "WIND ONSHORE" : "air",
    "WIND OFFSHORE" : "air",
}

def response_to_df(response):
    """ convert API response to dataframe"""
    rows = []
    for energy in response:
        energy_name = energy["psrType"]
        halfhr_use  = energy["halfHourUsage"]
        halfhr_perc = energy["halfHourPercentage"]
        day_use     = energy["twentyFourHourUsage"]
        day_perc    = energy["twentyFourHourPercentage"]

        element = element_mappings.get(energy_name.upper(), "ELEMENT NOT FOUND")

        rows.append({
            "energy" : energy_name,
            "30min_use" : halfhr_use,
            "30min_perc": halfhr_perc,
            "24hr_use" : day_use,
            "24hr_perc" : day_perc,
            "element" : element
        })

    response_df = pd.DataFrame(rows)
    return response_df

def get_current_uk_time():
    """
        Helper function to output current uk time as string
    """
    uk_tz = pytz.timezone('Europe/London')
    uk_time = datetime.now(uk_tz)
    format_time = uk_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    return format_time

def build_output_dict(response_df):
    """
        Get data in desired output format
    """
    out_dict = {}
    #add timestamp
    out_dict["timestamp"] = get_current_uk_time()
    #add overall totals
    out_dict["total"] = {
        "30_min" : response_df["30min_use"].sum(),
        "24_hours" : response_df["24hr_use"].sum()
    }

    #calculate totals per element
    total_df = response_df.groupby("element").sum()

    elements_dicts_out = {} # -> four key/value pairs
    for element in four_elements:
        #each element will include its list of energy sources
        sources_list = []
        for source in response_df.query(f"element == '{element}'").to_dict(orient="records"):
            sources_list.append({
                "name" : source["energy"].upper(),
                "30_min" : source["30min_use"],
                "24_hours" : source["24hr_use"]
            })
        #build the output for this element
        element_dict = {
            "30_min" : total_df.loc[element, "30min_use"],
            "24_hours" : total_df.loc[element, "24hr_use"],
            "sources" : sources_list
        }
        elements_dicts_out[element] = element_dict

    #include in output dictionary
    out_dict["elements"] = elements_dicts_out
    return out_dict

#called from api/fast.py
def get_current_data_as_elements(response):

    response_df = response_to_df(response)
    output_as_dict = build_output_dict(response_df)

    return output_as_dict

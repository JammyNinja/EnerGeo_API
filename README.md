# EnerGeo

## Introduction
Welcome to the backend of [EnerGeo](energeo.dev), a React-based web application designed to visualize real-time energy sourcing and environmental impact data. Our goal is to promote sustainable practices and raise awareness through interactive graphs and images. EnerGeo was developed during a hackathon themed "Earth, Fire, Air, Water - Where does our energy come from?"
By integrating MLOps, Cloud, and AI technologies, EnerGeo channels data from various APIs and leverages advanced LLM-based technologies. We aspire to provide users with a comprehensive tool that facilitates a direct and easier understanding of the environmental impact of energy sources, and our unique take is classifying them into the four aforementioned elements.
Currently EnerGeo offers visualizations of historical consumption levels in the UK (last 30 minutes and last 24 hours) and features an AI image generator that provides real-time visualizations of weather conditions in any location around the world.

## Table of Contents

1. [Local installation](#Local-Installation)
2. [Key Features / Endpoints](#key-features/endpoints)
3. [Technologies Used](#technologies-used)
4. [Data Sources](#data-sources)
5. [Team](#team--contributers)
6. [Acknowledgements](#acknowledgements)
7. [Front End Repo](https://energeo.dev/)




## Local installation
Please see below how to run the api locally on your machine. The API is deployed on Google Cloud Run, and is run in a Docker container. To run the /agent endpoint you will need to use your API keys for both OpenAI's API and weather API.

## Key Features/endpoints
  - ```/agent``` returns DALLE image created with prompt using a location and the current weather data at that location
  - ```/current``` returns JSON with the 30min and 24hr energy generation data, broken down by element
  - ```/geo/regional/carbon_intensity``` returns geoJSON with properties including carbon intensity for the 14 UK energy regions
  - ```/geo/image_static``` returns image with current carbon intensity values by UK energy region, by matplotlib
  - ```/geo/regional/solar_generation``` returns geoJSON with properties including solar output forecast by Uni of Sheffield
  - ```/geo/regional/all``` returns geoJSON with carbon and solar properties
  - ```/historical``` returns JSON with the yearly energy generation, also broken down by element


## Technologies Used
Using Python, we built a FastAPI using Uvicorn, which is deployed on Google cloud run in a Docker image.
We call multiple APIs (see Data Sources below) and assembled the responses with Pandas.

MORE STORY ON HOW WE DID IT

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)  ![GeoPandas](https://img.shields.io/badge/GeoPandas-black?style=for-the-badge&logo=GeoPandas) ![LangChain](https://img.shields.io/badge/Langchain-1c3c3c?style=for-the-badge&logo=Langchain) ![openAI](https://img.shields.io/badge/OpenAI-1c3c3c?style=for-the-badge&logo=openai) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white) ![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black) ![GeoJSON](https://img.shields.io/badge/GeoJSON-5A5A5A?style=for-the-badge&logo=geojson&logoColor=white)

- ChatGPT 4mini
- DALLE 3
- Weather API
-

## Data sources

### Live Data
#### Current UK energy generation:
Elexon provide an API that offers data about the UK energy network.
 - [Elexon API docs](https://bmrs.elexon.co.uk/api-documentation/introduction)
 - [Endpoint in use](https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type/day-total?format=json)

#### Carbon intensity
The [carbon intensity](https://carbonintensity.org.uk/) forecast API is made by National Grid ESO, in partnership with the Environmental Defense Fund Europe, University of Oxford, and WWF.
 - [Carbon Intensity API docs](https://carbon-intensity.github.io/api-definitions/#carbon-intensity-api-v2-0-0).
 - [Endpoint in use](https://api.carbonintensity.org.uk/regional)
 - [Carbon intensity regional forecast methodology PDF](https://github.com/carbon-intensity/methodology/raw/master/Regional%20Carbon%20Intensity%20Forecast%20Methodology.pdf)

#### Solar generation
We use solar energy generation forecast data provided by [University of Sheffield solar](https://www.solar.sheffield.ac.uk/). We get solar generation forecast by PES region.
- [API documentation](https://api.solar.sheffield.ac.uk/pvlive/docs)
- [API endpoint for national solar output](https://api.solar.sheffield.ac.uk/pvlive/api/v4/pes/0)

#### Weather Data
We query [free weather API](https://www.weatherapi.com/) for current weather data in a specified location


### Static data
#### Historic energy generation data
We downloaded a publicly available file from National Grid ESO's [data portal](https://www.nationalgrideso.com/data-portal). Contains data up to 17th July 2024. Find link to current document below.
- [Historic data page](https://www.nationalgrideso.com/data-portal/historic-generation-mix)
- [Historical data file download](https://api.nationalgrideso.com/dataset/88313ae5-94e4-4ddc-a790-593554d8c6b9/resource/f93d1835-75bc-43e5-84ad-12472b180a98/download/df_fuel_ckan.csv)

#### UK Energy Regions
Also from national grid data portal is a geoJSON file that contains the coordinates of UK regions. We use regions current at May 2024.
 - [Region boundaries page](https://www.nationalgrideso.com/data-portal/gis-boundaries-gb-dno-license-areas)
 - [GeoJSON file download](https://api.nationalgrideso.com/dataset/0e377f16-95e9-4c15-a1fc-49e06a39cfa0/resource/1c6a7dc0-1b6c-443a-bc67-5f7125649434/download/gb-dno-license-areas-20240503-as-geojson.geojson)

## Team / Contributers

- Frontend Engineer:
  - [Priscila Finkler Innocente](https://github.com/prifinkler)

- Data Scientists:
  - [Aryavachin Márquez Briceño](https://github.com/cipobt)
  - [Louis Auger](https://github.com/JammyNinja)

## Acknowledgements
- [Andrew Crossland, PhD](https://linkedin.com/in/afcrossland/) inspired our project with his real-time web-based tool, mygridgb.co.uk, and offered us constant support and encouragement throughout the hackathon.
- [Anna Putt](https://linkedin.com/in/anna-putt/) for organizing the MentorMe initiative and its first hackathon, "Earth, Fire, Air, Water - Where Does Our Energy Come From?", and Ben Fairbairn(https://linkedin.com/in/benfairbairn/) for coming up with the theme. We had the honour of winning the hackathon with this project!
- [Le Wagon - London](https://www.lewagon.com/london) trained us and provided an excellent co-working space in the heart of London for the duration of the hackathon.

## Front End
The front end of the application is on this [GitHub Repo](https://github.com/prifinkler/energeo)

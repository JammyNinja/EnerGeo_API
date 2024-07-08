FROM python:3.10.14-slim-bookworm
#-slim

WORKDIR project

COPY requirements_prod.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY api api
COPY data/test_current.json data/test_current.json
COPY data/df_fuel_ckan.csv data/df_fuel_ckan.csv
COPY data/geo/uk_dno_regions_2024.geojson data/geo/uk_dno_regions_2024.geojson

#install make as slim version doesn't come with it
RUN apt-get update && apt-get install make
COPY Makefile Makefile
COPY .env .env

# CMD uvicorn api.fast:app --host 0.0.0.0 --port $PORT
#uses makefile to run command (not sure if helpful tbh)
CMD make run_cmd

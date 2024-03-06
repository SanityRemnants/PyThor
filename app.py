from asyncio import sleep

from flask import Flask, request, Response
import copernicusmarine
from datetime import datetime
import json

import yaml

USERNAME = ""
PASSWORD = ""
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    USERNAME = config["coppernicus_acount"]["username"]
    PASSWORD = config["coppernicus_acount"]["password"]

wave_variables_dict = {"significant_wave_height": "VHM0",  # cmems_mod_glo_wav_anfc_0.083deg_PT3H-i
                       "wave_direction": "VMDR",  # cmems_mod_glo_wav_anfc_0.083deg_PT3H-i
                       "wave_period": "nic"}  # cmems_mod_glo_wav_anfc_0.083deg_PT3H-i
# "wind_direction":"nic",
# "wind_speed":"nic",
curr_variables = ["sea_current_speed", "sea_current_direction"]
curr_variables_names = ["eastward_sea_water_velocity",
                        "northward_sea_water_velocity"]  # ,  #cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i
tide_variables_dict = {"tide_height": "zos"}  # cmems_mod_glo_phy_anfc_0.083deg_PT1H-m


# TODO podmienić nic na aktualne nazwy zmiennych z copernicusa
# time, latitude, logitude
def parse_variables(request_vars):
    wave_vars = []
    curr_vars = []
    tide_vars = []
    for v in request_vars:
        if v in wave_variables_dict.keys():
            wave_vars.append(wave_variables_dict[v])
        if v in curr_variables:
            curr_vars = curr_variables_names.copy()
        if v in tide_variables_dict:
            tide_vars.append(tide_variables_dict[v])
    return wave_vars, curr_vars, tide_vars


def fetch_tide(data, variables):
    data_request = {
        "dataset_id_sst_gap_l3s": "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
        "longitude": [data["longitude_start"], data["longitude_end"]],
        "latitude": [data["latitude_start"], data["latitude_end"]],
        "time": [data["time_start"], data["time_end"]],
        "variables": variables
    }

    # Load xarray dataset
    sst_l3s = copernicusmarine.open_dataset(
        dataset_id=data_request["dataset_id_sst_gap_l3s"],
        minimum_longitude=data_request["longitude"][0],
        maximum_longitude=data_request["longitude"][1],
        minimum_latitude=data_request["latitude"][0],
        maximum_latitude=data_request["latitude"][1],
        start_datetime=data_request["time"][0],
        end_datetime=data_request["time"][1],
        variables=data_request["variables"], username=USERNAME, password=PASSWORD)
    return sst_l3s


def fetch_currents(data, variables):
    data_request = {
        "dataset_id_sst_gap_l3s": "cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i",
        "longitude": [data["longitude_start"], data["longitude_end"]],
        "latitude": [data["latitude_start"], data["latitude_end"]],
        "time": [data["time_start"], data["time_end"]],
        "variables": variables
    }

    # Load xarray dataset
    sst_l3s = copernicusmarine.open_dataset(
        dataset_id=data_request["dataset_id_sst_gap_l3s"],
        minimum_longitude=data_request["longitude"][0],
        maximum_longitude=data_request["longitude"][1],
        minimum_latitude=data_request["latitude"][0],
        maximum_latitude=data_request["latitude"][1],
        start_datetime=data_request["time"][0],
        end_datetime=data_request["time"][1],
        variables=data_request["variables"], username=USERNAME, password=PASSWORD)
    return sst_l3s


def fetch_wave(data, variables):
    data_request = {
        "dataset_id_sst_gap_l3s": "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i",
        "longitude": [data["longitude_start"], data["longitude_end"]],
        "latitude": [data["latitude_start"], data["latitude_end"]],
        "time": [data["time_start"], data["time_end"]],
        "variables": variables
    }

    # Load xarray dataset
    sst_l3s = copernicusmarine.open_dataset(
        dataset_id=data_request["dataset_id_sst_gap_l3s"],
        minimum_longitude=data_request["longitude"][0],
        maximum_longitude=data_request["longitude"][1],
        minimum_latitude=data_request["latitude"][0],
        maximum_latitude=data_request["latitude"][1],
        start_datetime=data_request["time"][0],
        end_datetime=data_request["time"][1],
        variables=data_request["variables"], username=USERNAME, password=PASSWORD)
    return sst_l3s


# Import modules
app = Flask(__name__)


@app.route('/api/weather')
def root():  # put application's code here
    latitude_start = request.args.get('latitude_start')
    latitude_end = request.args.get('latitude_end')
    logitude_start = request.args.get('logitude_start')
    logitude_end = request.args.get('logitude_end')
    interval = request.args.get('interval', 2)
    request_vars = request.args.get('variables', "").replace(" ", "").split(",")
    epoch_time_start = int(request.args.get('time_start'))
    epoch_time_end = int(request.args.get('time_end'))
    if not latitude_start or not latitude_end or not logitude_start or not logitude_end or not epoch_time_start or not epoch_time_end or len(
            request_vars) == 0:
        return Response(status=400)
    wave_vars, curr_vars, tide_vars = parse_variables(request_vars)
    time_start = datetime.fromtimestamp(epoch_time_start).date()
    time_end = datetime.fromtimestamp(epoch_time_end).date()
    data = {
        "longitude_start": float(logitude_start),
        "longitude_end": float(logitude_end),
        "latitude_start": float(latitude_start),
        "latitude_end": float(latitude_end),
        "time_start": str(time_start),
        "time_end": str(str(time_end))
    }
    waves, tides, currents = None, None, None
    res = {}
    if len(wave_vars) > 0:
        waves = fetch_wave(data, wave_vars).to_dict()
        res["waves"] = waves
    if len(tide_vars) > 0:
        tides = fetch_tide(data, tide_vars).to_dict()
        res["tides"] = tides
    if len(curr_vars) > 0:
        currents = fetch_currents(data, curr_vars).to_dict()
        res["currents"] = currents
    # Set parameters

    return res


if __name__ == '__main__':
    _ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_wav_anfc_0.083deg_PT3H-i", username=USERNAME,
                                      password=PASSWORD)
    _ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i", username=USERNAME,
                                      password=PASSWORD)
    _ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m", username=USERNAME,
                                      password=PASSWORD)
    app.run()

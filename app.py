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


variables_dict = {"significant_wave_height":"nic",
                  "wave_direction":"nic",
                  "wave_period":"nic",
                  "wind_direction":"nic",
                  "sea_current_speed":"nic",
                  "sea_current_direction":"nic",
                  "tide_height":"nic"} #TODO podmienić nic na aktualne nazwy zmiennych z copernicusa

def parse_variables(request_vars):
    vars = []
    for v in request_vars:
        if v in variables_dict.keys():
            vars.append(variables_dict[v])
    return vars

# Import modules
app = Flask(__name__)


@app.route('/api/weather')
def root():  # put application's code here
    latitude_start = request.args.get('latitude_start')
    latitude_end = request.args.get('latitude_end')
    logitude_start = request.args.get('logitude_start')
    logitude_end = request.args.get('logitude_end')
    interval = request.args.get('interval',2)
    request_vars = request.args.get('variables',"").replace(" ","").split(",")
    variables = parse_variables(request_vars)
    epoch_time_start = int(request.args.get('time_end'))
    epoch_time_end = int(request.args.get('time_start'))
    if not latitude_start or not latitude_end or not logitude_start or not logitude_end or not epoch_time_start or not epoch_time_end or len(variables) == 0:
        return Response(status=400)
    time_start = datetime.fromtimestamp(epoch_time_start).date()
    time_end = datetime.fromtimestamp(epoch_time_end).date()

    # Set parameters
    data_request = {
        "dataset_id_sst_gap_l3s": "cmems_obs-sst_atl_phy_nrt_l3s_P1D-m",
        "longitude": [float(logitude_start), float(logitude_end)],
        "latitude": [float(latitude_start), float(latitude_end)],
        "time": [str(time_start), str(time_end)],
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
    return json.dumps(sst_l3s.to_dict())


if __name__ == '__main__':
    sst_l3s = copernicusmarine.open_dataset(dataset_id= "cmems_obs-sst_atl_phy_nrt_l3s_P1D-m", username=USERNAME, password=PASSWORD)
    # Print loaded dataset information
    app.run()

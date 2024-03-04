from asyncio import sleep

from flask import Flask, request, Response
import copernicusmarine
from datetime import datetime

import yaml
USERNAME = ""
PASSWORD = ""
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    USERNAME = config["coppernicus_acount"]["username"]
    PASSWORD = config["coppernicus_acount"]["password"]

# Import modules
app = Flask(__name__)

def fetch_data(request):
    return copernicusmarine.open_dataset(
        dataset_id=request["dataset_id_sst_gap_l3s"],
        minimum_longitude=request["longitude"][0],
        maximum_longitude=request["longitude"][1],
        minimum_latitude=request["latitude"][0],
        maximum_latitude=request["latitude"][1],
        start_datetime=request["time"][0],
        end_datetime=request["time"][1],
        variables=request["variables"], username=USERNAME, password=PASSWORD)

@app.route('/api/weather')
def root():  # put application's code here
    latitude_start = request.args.get('latitude_start')
    latitude_end = request.args.get('latitude_end')
    logitude_start = request.args.get('logitude_start')
    logitude_end = request.args.get('logitude_end')
    if latitude_end and latitude_start and logitude_end and logitude_end:
        time_start = datetime.fromtimestamp(int(request.args.get('time_start'))).date()
        time_end = datetime.fromtimestamp(int(request.args.get('time_end'))).date()
    else:
        return Response(status=400)

    # Set parameters
    data_request = {
        "dataset_id_sst_gap_l3s": "cmems_obs-sst_atl_phy_nrt_l3s_P1D-m",
        "longitude": [float(logitude_start), float(logitude_end)],
        "latitude": [float(latitude_start), float(latitude_end)],
        "time": [str(time_start), str(time_end)],
        "variables": ["sea_surface_temperature"]
    }

    # Load xarray dataset
    sst_l3s = fetch_data(data_request)
    return sst_l3s.to_dict()


if __name__ == '__main__':
    #sst_l3s = copernicusmarine.open_dataset(dataset_id= "cmems_obs-sst_atl_phy_nrt_l3s_P1D-m", username=USERNAME, password=PASSWORD)
    # Print loaded dataset information
    app.run()

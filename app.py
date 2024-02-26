from datetime import datetime

USERNAME = "kdrozd"
PASSWORD = "Death5142"
# Import modules
import copernicusmarine
from flask import Flask, request

app = Flask(__name__)


@app.route('/api/weather')
def root():  # put application's code here
    latitude_start = request.args.get('latitude_start')
    latitude_end = request.args.get('latitude_end')
    logitude_start = request.args.get('logitude_start')
    logitude_end = request.args.get('logitude_end')
    time_start = datetime.fromtimestamp(int(request.args.get('time_start'))).date()
    time_end = datetime.fromtimestamp(int(request.args.get('time_end'))).date()

    # Set parameters
    data_request = {
        "dataset_id_sst_gap_l3s": "cmems_obs-sst_atl_phy_nrt_l3s_P1D-m",
        "longitude": [float(logitude_start), float(logitude_end)],
        "latitude": [float(latitude_start), float(latitude_end)],
        "time": [str(time_start), str(time_end)],
        "variables": ["sea_surface_temperature"]
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
        variables=data_request["variables"], username=USERNAME, password=PASSWORD
    )
    return sst_l3s.to_dict()


if __name__ == '__main__':
    app.run()

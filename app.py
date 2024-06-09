from copy import deepcopy
import numpy as np
from flask import Flask, request, Response
import copernicusmarine
from scipy.interpolate import RegularGridInterpolator, Rbf

from data_request import DataRequest
from fetcher import Fetcher
from interpolation import interpolate

import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    USERNAME = config["coppernicus_acount"]["username"]
    PASSWORD = config["coppernicus_acount"]["password"]

app = Flask(__name__)





@app.route('/api/weather')
def root():  # put application's code here
    data_request = DataRequest(request.args.get('latitude_start'), request.args.get('latitude_end'),
                               request.args.get('longitude_start'), request.args.get('longitude_end'),
                               request.args.get('time_start'), request.args.get('time_end'),
                               request.args.get('interval', 2),
                               request.args.get('variables', "").replace(" ", "").split(","))
    if not data_request.is_valid():
        return Response(status=400)
    result = Fetcher(data_request).fetch()

    wave_wind_not_inter = result["waves_and_wind"]
    res = interpolate(result,data_request.get_time_interval())
    return res





if __name__ == '__main__':
    '''_ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i", username=USERNAME,
                                      password=PASSWORD)
    _ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m", username=USERNAME,
                                      password=PASSWORD)'''

    app.run()
# print(fetch_wave(0, 0))

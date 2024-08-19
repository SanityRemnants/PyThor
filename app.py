from copy import deepcopy
import numpy as np
from flask import Flask, request, Response
import copernicusmarine
from scipy.interpolate import RegularGridInterpolator, Rbf

from data_request import DataRequest
from fetcher import Fetcher
from interpolation import interpolate, interpolate_for_copernicus

import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    USERNAME = config["coppernicus_acount"]["username"]
    PASSWORD = config["coppernicus_acount"]["password"]

app = Flask(__name__)


@app.route('/api/weather')
def root():
    data_request = DataRequest(request.args.get('latitude_start'), request.args.get('latitude_end'),
                               request.args.get('longitude_start'), request.args.get('longitude_end'),
                               request.args.get('time_start'), request.args.get('time_end'),
                               request.args.get('interval', 2),
                               request.args.get('variables', "").replace(" ", "").split(","))
    if not data_request.is_valid():
        return Response(status=400)
    result = Fetcher(data_request).fetch()

    res = interpolate(result, data_request.get_time_interval())

    return res


if __name__ == '__main__':

    app.run()
# print(fetch_wave(0, 0))

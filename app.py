from copy import deepcopy
import numpy as np
from flask import Flask, request, Response
import copernicusmarine
from scipy.interpolate import RegularGridInterpolator, Rbf

from data_request import DataRequest
from fetcher import Fetcher

import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    USERNAME = config["coppernicus_acount"]["username"]
    PASSWORD = config["coppernicus_acount"]["password"]

app = Flask(__name__)


def spherical_to_cartesian(lat, lon, r=1):
    lat_rad = np.deg2rad(lat)
    lon_rad = np.deg2rad(lon)
    x = r * np.cos(lat_rad) * np.cos(lon_rad)
    y = r * np.cos(lat_rad) * np.sin(lon_rad)
    z = r * np.sin(lat_rad)
    return x, y, z


@app.route('/api/weather')
def root():  # put application's code here
    data_request = DataRequest(request.args.get('latitude_start'), request.args.get('latitude_end'),
                               request.args.get('logitude_start'), request.args.get('logitude_end'),
                               request.args.get('time_start'), request.args.get('time_end'),
                               request.args.get('interval', 2),
                               request.args.get('variables', "").replace(" ", "").split(","))
    if not data_request.is_valid():
        return Response(status=400)
    result = Fetcher(data_request).fetch()

    wave_wind_not_inter = result["waves_and_wind"]
    lat = np.array(wave_wind_not_inter["latitude"])
    lon = np.array(wave_wind_not_inter["longitude"])
    time = np.array(wave_wind_not_inter["time"])

    lat_inter = np.arange(lat[0], lat[-1], 0.1)
    lon_inter = np.arange(lon[0], lon[-1], 0.1)
    if time[0] != time[-1]:
        time_inter = np.arange(time[0], time[-1], 10800)
    else:
        time_inter = time

    keys_to_check = ["dirpw", "swh", "perpw", "u", "v", "ws"]
    keys = []
    weather = {}
    for key in keys_to_check:
        if key in wave_wind_not_inter:
            keys.append(key)
            key_inter = key + "_inter"
            weather[key] = np.array(wave_wind_not_inter[key])
            weather[key+"_mask"] = np.isnan(weather[key]).astype(float)
            print(weather[key+"_mask"])
            keys.append(key+"_mask")
            result[key_inter] = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in
                                 range(len(time_inter))]
            result[key + "_mask" + "_inter"] = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in
                                                range(len(time_inter))]

    normal = {key: value.tolist() if isinstance(value, np.ndarray) else value for key, value in
              weather.items()}

    lon_grid, lat_grid = np.meshgrid(lon, lat)
    lon_inter_grid, lat_inter_grid = np.meshgrid(lon_inter, lat_inter)
    res = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in range(len(time))]
    for key in keys:
        for k in range(len(time)):
            # Interpolacja po długości i szerokości
            elem = weather[key]
            nan_mask = np.isnan(elem[k])
            indices = np.where(~nan_mask)
            data_points_valid = elem[k][indices]
            lat_valid = lat_grid[~nan_mask]
            lon_valid = lon_grid[~nan_mask]
            x, y, z = spherical_to_cartesian(lat_valid.ravel(), lon_valid.ravel())
            interp_spatial = Rbf(x, y, z, data_points_valid, function='thin_plate', smooth=0)

            x_inter, y_inter, z_inter = spherical_to_cartesian(lat_inter_grid, lon_inter_grid)
            res[k] = interp_spatial(x_inter, y_inter, z_inter)

        interpolator = RegularGridInterpolator((time, lat_inter, lon_inter), res)
        key_inter = key + "_inter"
        for k in range(len(time_inter)):
            # Interpolacja wzdłuż czasu
            for i in range(len(lat_inter)):
                for j in range(len(lon_inter)):
                    result[key_inter][k][i][j] = interpolator([time_inter[k], lat_inter[i], lon_inter[j]])

        weather[key] = [[[float(value[0]) for value in row] for row in slice_] for slice_ in result[key_inter]]
    keys_to_iter = deepcopy(list(weather.keys()))
    for k in keys_to_iter:
        if "mask" in k:
            key_to_nan = k.replace("_mask", "")
            for t in range(len(weather[key_to_nan])):
                for l in range(len(weather[key_to_nan][t])):
                    for lt in range(len(weather[key_to_nan][t][l])):
                        if weather[k][t][l][lt] >= 0.6:
                            weather[key_to_nan][t][l][lt] = np.NaN
            weather.pop(k)
    weather["time_inter"] = time_inter.tolist()
    weather["time"] = time.tolist()

    weather["normal"] = normal
    weather["lat"] = lat.tolist()
    weather["lon"] = lon.tolist()
    weather["lat_inter"] = lat_inter.tolist()
    weather["lon_inter"] = lon_inter.tolist()

    return weather



if __name__ == '__main__':
    '''_ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i", username=USERNAME,
                                      password=PASSWORD)
    _ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m", username=USERNAME,
                                      password=PASSWORD)'''

    app.run()
# print(fetch_wave(0, 0))

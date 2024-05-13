import json

import numpy as np
import scipy.interpolate
from flask import Flask, request, Response
import copernicusmarine
from scipy.interpolate import griddata, SmoothSphereBivariateSpline, RegularGridInterpolator

from data_request import DataRequest
from fetcher import Fetcher
import scipy.interpolate as sci

import yaml

USERNAME = ""
PASSWORD = ""
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    USERNAME = config["coppernicus_acount"]["username"]
    PASSWORD = config["coppernicus_acount"]["password"]

# Import modules
app = Flask(__name__)


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

    # return result

    wave_wind_not_inter = result["waves_and_wind"]
    lat = np.array(wave_wind_not_inter["latitude"])
    lon = np.array(wave_wind_not_inter["longitude"])
    time = np.array(wave_wind_not_inter["time"])

    coords = data_request.get_coordinates()
    lat_inter = np.arange(lat[0], lat[-1], 0.1)
    lon_inter = np.arange(lon[0], lon[-1], 0.1)
    if time[0] != time[-1]:
        time_inter = np.arange(time[0], time[-1], 10800)
    else:
        time_inter = time

    keys_to_check = ["dirpw", "swh", "perpw", "u", "v", "ws"]
    keys = []
    weather = {}
    normal = {}
    for key in keys_to_check:
        if key in wave_wind_not_inter:
            keys.append(key)
            key_inter = key + "_inter"
            weather[key] = np.array(wave_wind_not_inter[key])
            result[key_inter] = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in
                                     range(len(time_inter))]

    normal = {key: value.tolist() if isinstance(value, np.ndarray) else value for key, value in
              weather.items()}

    lat_rad = np.deg2rad(lat)
    lon_rad = np.deg2rad(lon)
    lon_rad = np.where(lon_rad < 0, lon_rad + 2*np.pi, lon_rad)


    lon_rad_inter = np.deg2rad(lon_inter)
    lat_rad_inter = np.deg2rad(lat_inter)
    lon_rad_inter = np.where(lon_rad_inter < 0, lon_rad_inter + 2 * np.pi, lon_rad_inter)

    lon_grid, lat_grid = np.meshgrid(lon_rad, lat_rad)
    res = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in range(len(time))]
    for key in keys:
        for k in range(len(time)):
            elem = weather[key]
            nan_mask = np.isnan(elem[k])
            indices = np.where(~nan_mask)
            lat_rad_valid = lat_grid[~nan_mask]
            lon_rad_valid = lon_grid[~nan_mask]
            data_points_valid = elem[k][indices].T.ravel()
            interp_spatial = SmoothSphereBivariateSpline(lat_rad_valid.ravel(), lon_rad_valid.ravel(), data_points_valid, s = len(data_points_valid)**3)

            res[k] = interp_spatial(lat_rad_inter, lon_rad_inter)

        interpolator = RegularGridInterpolator((time, lat_inter, lon_inter), res)
        key_inter = key + "_inter"
        for k in range(len(time_inter)):
            # Interpolacja wzdłuż czasu
            for i in range(len(lat_inter)):
                for j in range(len(lon_inter)):

                    result[key_inter][k][i][j] = interpolator([time_inter[k], lat_inter[i], lon_inter[j]])

        weather[key] = [[[float(value[0]) for value in row] for row in slice_] for slice_ in result[key_inter]]
    weather["time_inter"] = time_inter.tolist()
    weather["time"] = time.tolist()

    weather["normal"] = normal
    weather["lat"] = lat.tolist()
    weather["lon"] = lon.tolist()
    weather["lat_inter"] = lat_inter.tolist()
    weather["lon_inter"] = lon_inter.tolist()

    return weather
    '''
    
    lon_min = np.array(wave_wind_not_inter["longitude"])[0]
    lon_max = np.array(wave_wind_not_inter["longitude"])[-1]
    lat_min = np.array(wave_wind_not_inter["latitude"])[0]
    lat_max = np.array(wave_wind_not_inter["latitude"])[-1]
    time_min = np.array(wave_wind_not_inter["time"])[0]
    time_max = np.array(wave_wind_not_inter["time"])[-1]

    dirpw = np.array(wave_wind_not_inter["dirpw"])
    maska = np.isnan(dirpw)
    punkty = np.argwhere(~maska)
    wartosci = dirpw[~maska]
    nowa_rozdzielczosc = 2
    z_interp, y_interp, x_interp = np.meshgrid(
        np.linspace(time_min, time_max, int(nowa_rozdzielczosc * (time_max - time_min) + 1)),
        np.linspace(lat_min, lat_max, int(nowa_rozdzielczosc * (lat_max - lat_min) + 1)),
        np.linspace(lon_min, lon_max, int(nowa_rozdzielczosc * (lon_max - lon_min) + 1)))

    dane_zinterpolowane = griddata(punkty, wartosci, (z_interp, y_interp, x_interp), method='linear')
    return dane_zinterpolowane'''


if __name__ == '__main__':
    '''_ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i", username=USERNAME,
                                      password=PASSWORD)
    _ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m", username=USERNAME,
                                      password=PASSWORD)'''

    app.run()
# print(fetch_wave(0, 0))

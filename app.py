import json

import numpy
import scipy.interpolate
from flask import Flask, request, Response
import copernicusmarine
from scipy.interpolate import griddata

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
    lat = numpy.array(wave_wind_not_inter["latitude"])
    lon = numpy.array(wave_wind_not_inter["longitude"])
    time = numpy.array(wave_wind_not_inter["time"])
    dirpw = numpy.array(wave_wind_not_inter["dirpw"])
    coords = data_request.get_coordinates()
    lat_inter = numpy.arange(lat[0], lat[-1], 0.1)
    lon_inter = numpy.arange(lon[0], lon[-1], 0.1)
    if time[0] != time[-1]:
        time_inter = numpy.arange(time[0], time[-1], 10800)
    else:
        time_inter = time
    result["dirpw_inter"] = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in range(len(time_inter))]

    interpolator = scipy.interpolate.RegularGridInterpolator((time, lat, lon), dirpw)

    for k in range(len(time_inter)):
        for i in range(len(lat_inter)):
            for j in range(len(lon_inter)):
                result["dirpw_inter"][k][i][j] = interpolator([time_inter[k], lat_inter[i], lon_inter[j]])
    dirpw_inter_list = [[[float(value[0]) for value in row] for row in slice_] for slice_ in result["dirpw_inter"]]
    return {"inter":dirpw_inter_list,"time_inter":time_inter.tolist(),"time":time.tolist(),"normal":result["waves_and_wind"]["dirpw"],"lat":lat.tolist(),"lat_inter":lat_inter.tolist(),"lon":lon.tolist(),"lon_inter":lon_inter.tolist()}
    '''
    lon_min = numpy.array(wave_wind_not_inter["longitude"])[0]
    lon_max = numpy.array(wave_wind_not_inter["longitude"])[-1]
    lat_min = numpy.array(wave_wind_not_inter["latitude"])[0]
    lat_max = numpy.array(wave_wind_not_inter["latitude"])[-1]
    time_min = numpy.array(wave_wind_not_inter["time"])[0]
    time_max = numpy.array(wave_wind_not_inter["time"])[-1]

    dirpw = numpy.array(wave_wind_not_inter["dirpw"])
    maska = numpy.isnan(dirpw)
    punkty = numpy.argwhere(~maska)
    wartosci = dirpw[~maska]
    nowa_rozdzielczosc = 2
    z_interp, y_interp, x_interp = numpy.meshgrid(
        numpy.linspace(time_min, time_max, int(nowa_rozdzielczosc * (time_max - time_min) + 1)),
        numpy.linspace(lat_min, lat_max, int(nowa_rozdzielczosc * (lat_max - lat_min) + 1)),
        numpy.linspace(lon_min, lon_max, int(nowa_rozdzielczosc * (lon_max - lon_min) + 1)))

    dane_zinterpolowane = griddata(punkty, wartosci, (z_interp, y_interp, x_interp), method='linear')
    return dane_zinterpolowane
'''

if __name__ == '__main__':
    '''_ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i", username=USERNAME,
                                      password=PASSWORD)
    _ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m", username=USERNAME,
                                      password=PASSWORD)'''

    app.run()
# print(fetch_wave(0, 0))

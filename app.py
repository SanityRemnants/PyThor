import numpy
import scipy.interpolate
from flask import Flask, request, Response
import copernicusmarine
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

    wave_wind_not_inter = result["waves_and_wind"]
    lat = numpy.array(wave_wind_not_inter["latitude"])
    lon = numpy.array(wave_wind_not_inter["longitude"])
    dirpw = numpy.array(wave_wind_not_inter["dirpw"])
    coords = data_request.get_coordinates()
    lat_inter = numpy.arange(lat[0],lat[-1],0.1)
    lon_inter = numpy.arange(lon[0],lon[-1],0.1)
    result["dirpw_inter"] = [[[0]*len(lon_inter)]*len(lat_inter)]
    interpolate = scipy.interpolate.RegularGridInterpolator((numpy.array([1]),lat,lon),dirpw)
    for i in range(len(lat_inter)):
        for j in range(len(lon_inter)):
            print(1.,lat_inter[i],lon_inter[j])
            result["dirpw_inter"][0][i][j] = interpolate([1.,lat_inter[i],lon_inter[j]])[0]
    return  {"inter":result["dirpw_inter"],"normal":result["waves_and_wind"]["dirpw"],"lat":lat.tolist(),"lat_inter":lat_inter.tolist(),"lon":lon.tolist(),"lon_inter":lon_inter.tolist()}

if __name__ == '__main__':
    '''_ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i", username=USERNAME,
                                      password=PASSWORD)
    _ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m", username=USERNAME,
                                      password=PASSWORD)'''

    app.run()
# print(fetch_wave(0, 0))

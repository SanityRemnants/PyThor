import pytz
from flask import Flask, request, Response
from urllib.request import urlretrieve
import copernicusmarine
from datetime import datetime
import xarray as xr
from data_request import DataRequest
from fetcher import Fetcher

import yaml

'''
USERNAME = ""
PASSWORD = ""
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    USERNAME = config["coppernicus_acount"]["username"]
    PASSWORD = config["coppernicus_acount"]["password"]


def map_hour(hour):
    forecast_hours = {(0, 5): "00", (6, 11): "06",
                      (12, 17): "12", (18, 23): "18"}
    for key in forecast_hours:
        if key[0] <= hour <= key[1]:
            return forecast_hours[key]

# TODO podmienić nic na aktualne nazwy zmiennych z copernicusa
# time, latitude, logitude



def fetch_tide(request):
    data_request = request.parse_for_copernicus_currents()

    # Load xarray dataset
    sst_l3s = copernicusmarine.open_dataset(
        dataset_id=data_request["dataset_id"],
        minimum_longitude=data_request["longitude"][0],
        maximum_longitude=data_request["longitude"][1],
        minimum_latitude=data_request["latitude"][0],
        maximum_latitude=data_request["latitude"][1],
        start_datetime=data_request["time"][0],
        end_datetime=data_request["time"][1],
        variables=data_request["variables"], username=USERNAME, password=PASSWORD)
    return sst_l3s


def fetch_currents(request):
    data_request = request.parse_for_copernicus_currents()

    # Load xarray dataset
    current = copernicusmarine.open_dataset(
        dataset_id=data_request["dataset_id"],
        minimum_longitude=data_request["longitude"][0],
        maximum_longitude=data_request["longitude"][1],
        minimum_latitude=data_request["latitude"][0],
        maximum_latitude=data_request["latitude"][1],
        start_datetime=data_request["time"][0],
        end_datetime=data_request["time"][1],
        variables=data_request["variables"], username=USERNAME, password=PASSWORD)
    return sst_l3s


def fetch_wave_and_wind(request):
    now = datetime.now().astimezone(pytz.timezone('America/New_York'))

    forecast_hour = map_hour(now.hour)

    url = (
        "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs." +
        now.strftime("%Y%m%d")+"/"+forecast_hour+"/wave/gridded/"
        "gfswave.t"+forecast_hour+"z.global.0p25.f000.grib2" + request.parse_for_noaa()
    )

    filename = "ww" + now.strftime("%Y%m%d") + forecast_hour + ".grib2"
    try:
        urlretrieve(url, filename)
        wave_unproccessed = xr.load_dataset(filename, engine='cfgrib')
        for v in wave_unproccessed:
            print("{}, {}, {}".format(
                v, wave_unproccessed[v].attrs["long_name"], wave_unproccessed[v].attrs["units"]))
        return wave_unproccessed["swh"].values
    except Exception as e:
        return "Exception: " + str(e)

'''
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

    fetcher = Fetcher(data_request)
    '''waves_and_wind, tides, currents = None, None, None
    res = {}
    if len(wave_and_wind_vars) > 0:
        waves_and_wind = fetch_wave_and_wind(data, wave_and_wind_vars).tolist()
        res["waves_and_wind"] = waves_and_wind
    if len(tide_vars) > 0:
        tides = fetch_tide(data, tide_vars).to_dict()
        res["tides"] = tides
    if len(curr_vars) > 0:
        currents = fetch_currents(data, curr_vars).to_dict()
        res["currents"] = currents
    # Set parameters

    return res'''
    return fetcher.fetch()


if __name__ == '__main__':
    # _ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i", username=USERNAME,
    #                                  password=PASSWORD)
    # _ = copernicusmarine.open_dataset(dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m", username=USERNAME,
    #                                  password=PASSWORD)
    # print(fetch_wave(0, 0))
    app.run()

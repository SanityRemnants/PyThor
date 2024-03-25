from urllib.request import urlretrieve
import xarray as xr
import copernicusmarine
import pytz
import yaml
from datetime import datetime

import data_request as dr


class Fetcher:
    def __init__(self, request):
        if isinstance(request, dr.DataRequest):
            self.__request = request
        else:
            raise print("argument is not valid data request")
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            self.USERNAME = config["coppernicus_acount"]["username"]
            self.PASSWORD = config["coppernicus_acount"]["password"]

    @staticmethod
    def map_hour(hour):
        forecast_hours = {(0, 5): "00", (6, 11): "06",
                          (12, 17): "12", (18, 23): "18"}
        for key in forecast_hours:
            if key[0] <= hour <= key[1]:
                return forecast_hours[key]
    def fetch_currents(self, currents):
        data_request = currents.parse_for_copernicus_currents()
        sst_l3s = copernicusmarine.open_dataset(
            dataset_id=data_request["dataset_id"],
            minimum_longitude=data_request["longitude"][0],
            maximum_longitude=data_request["longitude"][1],
            minimum_latitude=data_request["latitude"][0],
            maximum_latitude=data_request["latitude"][1],
            start_datetime=data_request["time"][0],
            end_datetime=data_request["time"][1],
            variables=data_request["variables"], username=self.USERNAME, password=self.PASSWORD)
        return sst_l3s

    def fetch_tide(self, tide):
        data_request = tide.parse_for_copernicus_tide()
        sst_l3s = copernicusmarine.open_dataset(
            dataset_id=data_request["dataset_id"],
            minimum_longitude=data_request["longitude"][0],
            maximum_longitude=data_request["longitude"][1],
            minimum_latitude=data_request["latitude"][0],
            maximum_latitude=data_request["latitude"][1],
            start_datetime=data_request["time"][0],
            end_datetime=data_request["time"][1],
            variables=data_request["variables"], username=self.USERNAME, password=self.PASSWORD)
        return sst_l3s

    def fetch_wave_and_wind(self, request):
        now = datetime.now().astimezone(pytz.timezone('America/New_York'))

        forecast_hour = self.map_hour(now.hour)

        url = (
                "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs." +
                now.strftime("%Y%m%d") + "/" + forecast_hour + "/wave/gridded/"
                                                               "gfswave.t" + forecast_hour + "z.global.0p25.f000.grib2" + request.parse_for_noaa()
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


    def fetch(self):
        waves_and_wind, tides, currents = None, None, None
        res = {}
        if len(self.__request.noaa_variables) > 0:
            waves_and_wind = self.fetch_wave_and_wind(self.__request.noaa_variables).tolist()
        if len(self.__request.tide_variables) > 0:
            tides = self.fetch_tide(self.__request.tide_variables).to_dict()
        if len(self.__request.currents_variables) > 0:
            currents = self.fetch_currents(self.__request.currents_variables).to_dict()
        res["waves_and_wind"] = waves_and_wind
        res["tides"] = tides
        res["currents"] = currents
        return res

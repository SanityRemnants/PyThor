import asyncio
from urllib.request import urlretrieve

import numpy as np
import xarray as xr
import copernicusmarine
import pytz
import yaml
from datetime import datetime, timedelta
import time
import os
import atexit

import data_request as dr


def rm_grib_files(file_name: str):
    """
    hook function that gets registered after each downloaded grib file to ensure that after the program ends
     there are no residual files left (grib files and corresponding .idx files)
    :param file_name: a name of a grib file to be removed after program exit
    :return:
    """
    try:
        os.remove(file_name)
        os.remove(file_name + ".923a8.idx")
    except FileNotFoundError:
        return


class Fetcher:
    """
    The class is responsible for fetching and processing data from external weather sources.
    """

    def __init__(self, request):
        self.currents = None
        self.tide = None
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
        """
        map provided hour to the closest correct forecast hour (00,06,12,18)
        :param hour: float or int
        :return:
        """
        forecast_hours = {(0, 5): "00", (6, 11): "06",
                          (12, 17): "12", (18, 23): "18"}
        for key in forecast_hours:
            if key[0] <= hour <= key[1]:
                return forecast_hours[key]

    @staticmethod
    def curr_map_hour(hour):
        """
        map provided hour to the closest correct forecast hour (00,06,12,18)
        :param hour: float or int
        :return:
        """
        forecast_hours = {(0, 5): 0, (6, 11): 6,
                          (12, 17): 12, (18, 23): 18}
        for key in forecast_hours:
            if key[0] <= hour <= key[1]:
                return forecast_hours[key]

    @staticmethod
    def curr_map_later_date(date):
        """
        map provided hour to the closest correct forecast hour (00,06,12,18)
        :param date: datetime
        :return:
        """
        map_date = date
        forecast_hours = {(0, 5): 6, (6, 11): 12,
                          (12, 17): 18, (18, 23): 0}
        for key in forecast_hours:
            if key[0] <= date.hour <= key[1]:
                map_date = map_date.replace(hour=forecast_hours[key])
                if forecast_hours[key] == 0:
                    map_date = map_date + timedelta(days=1)
                return map_date

    def run_currents_task(self, data_request):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.fetch_currents_async(data_request))
        loop.close()

    async def fetch_currents_async(self, data_request):
        time_start = data_request["time"][0].replace(hour=self.curr_map_hour(data_request["time"][0].hour))
        time_end = self.curr_map_later_date(data_request["time"][1])
        self.currents = copernicusmarine.open_dataset(
            dataset_id=data_request["dataset_id"],
            minimum_longitude=data_request["longitude"][0],
            maximum_longitude=data_request["longitude"][1],
            minimum_latitude=data_request["latitude"][0],
            maximum_latitude=data_request["latitude"][1],
            start_datetime=time_start,
            end_datetime=time_end,
            variables=data_request["variables"], username=self.USERNAME, password=self.PASSWORD)

    def fetch_currents(self):
        """
        send request to copernicus service for currents data
        :return: xarray dataset
        """
        data_request = self.__request.parse_for_copernicus_currents()
        self.run_currents_task(data_request)
        return self.currents

    def run_tide_task(self, data_request):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.fetch_tide_async(data_request))
        loop.close()

    async def fetch_tide_async(self, data_request):
        self.tide = copernicusmarine.open_dataset(
            dataset_id=data_request["dataset_id"],
            minimum_longitude=data_request["longitude"][0],
            maximum_longitude=data_request["longitude"][1],
            minimum_latitude=data_request["latitude"][0],
            maximum_latitude=data_request["latitude"][1],
            start_datetime=data_request["time"][0],
            end_datetime=data_request["time"][1],
            variables=data_request["variables"], username=self.USERNAME, password=self.PASSWORD)

    def fetch_tide(self):
        """
        send request to copernicus service for tide data
        :return: xarray dataset
        """
        data_request = self.__request.parse_for_copernicus_tide()
        self.run_tide_task(data_request)
        return self.tide

    def fetch_wave_and_wind(self):
        """
        Fetch wave and wind data from NOAA and process it for further use.

        :return: Processed wave and wind data.
        """
        now = datetime.now().astimezone(pytz.timezone('America/New_York'))
        res = {}
        time_start, time_end = self.__request.get_time()
        time_start, time_end = time_start.astimezone(pytz.timezone('UTC')), time_end.astimezone(
            pytz.timezone('UTC'))
        forecast_time = time_start
        i = 0
        j = 0
        time_data = []
        forecast_hour = None
        while forecast_time <= time_end:

            if forecast_time <= now:

                forecast_hour = self.map_hour(forecast_time.hour)
                j = forecast_time.hour % 6
                h = '{:03d}'.format(j)
                url = (
                        "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfswave.pl?dir=%2Fgfs." +
                        forecast_time.strftime("%Y%m%d") + "%2F" + forecast_hour + "%2Fwave%2Fgridded&file="
                                                                                   "gfswave.t" + forecast_hour +
                        "z.global.0p25.f" + h + ".grib2" + self.__request.parse_for_noaa()
                )
                print(forecast_hour)
                print(h)
            else:
                h = '{:03d}'.format(j)
                forecast_hour = self.map_hour(now.hour)

                url = (
                        "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfswave.pl?dir=%2Fgfs." +
                        now.strftime("%Y%m%d") + "%2F" + forecast_hour + "%2Fwave%2Fgridded&file="
                                                                         "gfswave.t" + forecast_hour +
                        "z.global.0p25.f" + h + ".grib2" + self.__request.parse_for_noaa()
                )
                print(forecast_hour)
                print(h)

            filename = "ww" + forecast_time.strftime("%Y%m%d") + forecast_hour + str(j) + ".grib2"
            atexit.register(rm_grib_files, filename)
            try:
                urlretrieve(url, filename)
                wave_unproccessed = xr.load_dataset(filename, engine='cfgrib')
                res["longitude"] = wave_unproccessed["longitude"].values.tolist()
                res["latitude"] = wave_unproccessed["latitude"].values.tolist()
                t = wave_unproccessed["time"].values
                t = int(t.astype('datetime64[s]').astype('int64'))
                t = t + 3600 * j
                time_data.append(t)
                j = j + 1

                for v in wave_unproccessed:

                    print("{}, {}, {}".format(
                        v, wave_unproccessed[v].attrs["long_name"], wave_unproccessed[v].attrs["units"]))
                    if v in res:
                        res[v].append(wave_unproccessed[v].values.tolist())
                    else:
                        res[v] = []
                        res[v].append(wave_unproccessed[v].values.tolist())
            except Exception as e:
                return str(e)

            i = i + 1
            forecast_time = forecast_time + timedelta(hours=1)
        res["time"] = []
        for e in time_data:
            res["time"].append(e)

        return res

    def fetch(self) -> dict[str, dict]:
        """
        fetch relevant data based on the DataRequest provided in the constructor
        :return: a dict structured like:
            - waves_and_wind : dict with waves and wind data from noaa
            - tides : dict with tides data from copernicus
            - currents : dict with currents data from copernicus
        """
        waves_and_wind, tides, currents = None, None, None
        res = {}
        if len(self.__request.noaa_variables) > 0:
            waves_and_wind = self.fetch_wave_and_wind()
        res["waves_and_wind"] = waves_and_wind
        res["copernicus"] = {}
        if len(self.__request.tide_variables) > 0:
            tides = self.fetch_tide().to_dict()
            res["copernicus"]["tides"] = tides
        if self.__request.currents_variables != [[],[]]:
            currents = self.fetch_currents().to_dict()
            res["copernicus"]["currents"] = currents

        return res

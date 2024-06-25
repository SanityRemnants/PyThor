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

    def fetch_currents(self):
        """
        send request to copernicus service for currents data
        :return: xarray dataset
        """
        data_request = self.__request.parse_for_copernicus_currents()
        currents = copernicusmarine.open_dataset(
            dataset_id=data_request["dataset_id"],
            minimum_longitude=data_request["longitude"][0],
            maximum_longitude=data_request["longitude"][1],
            minimum_latitude=data_request["latitude"][0],
            maximum_latitude=data_request["latitude"][1],
            start_datetime=data_request["time"][0],
            end_datetime=data_request["time"][1],
            variables=data_request["variables"], username=self.USERNAME, password=self.PASSWORD)
        return currents

    def fetch_tide(self):
        """
        send request to copernicus service for tide data
        :return: xarray dataset
        """
        data_request = self.__request.parse_for_copernicus_tide()
        tide = copernicusmarine.open_dataset(
            dataset_id=data_request["dataset_id"],
            minimum_longitude=data_request["longitude"][0],
            maximum_longitude=data_request["longitude"][1],
            minimum_latitude=data_request["latitude"][0],
            maximum_latitude=data_request["latitude"][1],
            start_datetime=data_request["time"][0],
            end_datetime=data_request["time"][1],
            variables=data_request["variables"], username=self.USERNAME, password=self.PASSWORD)
        return tide

    def get_forecast_url(self, forecast_time, now, j):
        """
        Generate the URL for fetching the wave and wind data based on the forecast time.

        :param forecast_time: Current forecast time.
        :param now: Current time.
        :param j: Hour offset for the forecast.
        :return: Generated URL and forecast hour.
        """
        if forecast_time <= now:
            forecast_hour = self.map_hour(forecast_time.hour)
            j = forecast_time.hour % 6
            h = '{:03d}'.format(j)
            url = (
                    "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfswave.pl?dir=%2Fgfs." +
                    forecast_time.strftime("%Y%m%d") + "%2F" + forecast_hour + "%2Fwave%2Fgridded&file="
                                                                               "gfswave.t" + forecast_hour + "z.global.0p25.f" + h + ".grib2" + self.parse_for_noaa()
            )
        else:
            h = '{:03d}'.format(j)
            forecast_hour = self.map_hour(now.hour)
            url = (
                    "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfswave.pl?dir=%2Fgfs." +
                    now.strftime("%Y%m%d") + "%2F" + forecast_hour + "%2Fwave%2Fgridded&file="
                                                                     "gfswave.t" + forecast_hour + "z.global.0p25.f" + h + ".grib2" + self.parse_for_noaa()
            )
        return url, forecast_hour, j

    def fetch_data_from_url(self, url, filename):
        """
        Fetch data from the specified URL and save it to the given filename.

        :param url: URL to fetch the data from.
        :param filename: Name of the file to save the data to.
        :return: Loaded dataset from the fetched file.
        """
        urlretrieve(url, filename)
        wave_unprocessed = xr.load_dataset(filename, engine='cfgrib')
        return wave_unprocessed

    def process_wave_data(self, wave_unprocessed, j):
        """
        Process the wave data by extracting necessary information and adjusting the time.

        :param wave_unprocessed: Loaded dataset containing wave data.
        :param j: Hour offset for the forecast.
        :return: Processed data including time and other variables.
        """
        res = {"longitude": wave_unprocessed["longitude"].values.tolist(),
               "latitude": wave_unprocessed["latitude"].values.tolist()}
        t = wave_unprocessed["time"].values
        t = int(t.astype('datetime64[s]').astype('int64'))
        t = t + 3600 * j
        time_data = [t]

        for v in wave_unprocessed:
            print("{}, {}, {}".format(v, wave_unprocessed[v].attrs["long_name"], wave_unprocessed[v].attrs["units"]))
            if v in res:
                res[v].append(wave_unprocessed[v].values.tolist())
            else:
                res[v] = [wave_unprocessed[v].values.tolist()]
        return res, time_data

    def fetch_wave_and_wind(self):
        """
        Fetch wave and wind data from NOAA and process it for further use.

        :return: Processed wave and wind data.
        """
        now = datetime.now().astimezone(pytz.timezone('America/New_York'))
        res = {}
        time_start, time_end = self.__request.get_time()
        time_start, time_end = time_start.astimezone(pytz.timezone('America/New_York')), time_end.astimezone(
            pytz.timezone('America/New_York'))
        forecast_time = time_start
        j = 0
        time_data = []

        while forecast_time <= time_end:
            url, forecast_hour, j = self.get_forecast_url(forecast_time, now, j)
            filename = "ww" + forecast_time.strftime("%Y%m%d") + forecast_hour + str(j) + ".grib2"

            try:
                wave_unprocessed = self.fetch_data_from_url(url, filename)
                wave_res, wave_time_data = self.process_wave_data(wave_unprocessed, j)

                if not res:
                    res = wave_res
                else:
                    for key, value in wave_res.items():
                        if key in res:
                            res[key].extend(value)
                        else:
                            res[key] = value

                time_data.extend(wave_time_data)
                j += 1

            except Exception as e:
                return str(e)

            forecast_time += timedelta(hours=1)

        res["time"] = time_data
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
        if len(self.__request.tide_variables) > 0:
            tides = self.fetch_tide().to_dict()
        if len(self.__request.currents_variables) > 0:
            currents = self.fetch_currents().to_dict()
        res["waves_and_wind"] = waves_and_wind
        res["tides"] = tides
        res["currents"] = currents
        return res

import asyncio
from urllib.request import urlretrieve

import atexit
import xarray as xr
import copernicusmarine
import pytz
from datetime import datetime, timedelta

import PyThor.data.data_request as dr
from PyThor.app_pythor import config
from PyThor.config.config import save_folder
from PyThor.utilities.files import rm_grib_files, rm_cache_files

# Register cleanup functions
atexit.register(rm_grib_files)
if config.settings["clear_cache"]:
    atexit.register(rm_cache_files)


class Fetcher:
    """
    The class is responsible for fetching and processing data from external weather sources.
    """

    def __init__(self, request):
        self.currents = None
        self.tide = None
        self.wind = None
        if isinstance(request, dr.DataRequest):
            self.__request = request
        else:
            raise print("argument is not valid data request")
        self.USERNAME = config.settings["coppernicus_acount"]["username"]
        self.PASSWORD = config.settings["coppernicus_acount"]["password"]

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
        time_start, time_end = data_request["time"][0].astimezone(pytz.timezone('UTC')).replace(tzinfo=None), \
            data_request["time"][1].astimezone(
                pytz.timezone('UTC')).replace(tzinfo=None)
        time_start = time_start.replace(hour=self.curr_map_hour(data_request["time"][0].hour))
        time_end = self.curr_map_later_date(time_end)
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

    def run_wind_task(self, data_request):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.fetch_wind_async(data_request))
        loop.close()

    async def fetch_wind_async(self, data_request):
        time_start, time_end = data_request["time"][0].astimezone(pytz.timezone('UTC')).replace(tzinfo=None), \
            data_request["time"][1].astimezone(
                pytz.timezone('UTC')).replace(tzinfo=None)
        time_start = time_start.replace(hour=self.curr_map_hour(data_request["time"][0].hour))
        time_end = self.curr_map_later_date(time_end)
        self.wind = copernicusmarine.open_dataset(
            dataset_id=data_request["dataset_id"],
            minimum_longitude=data_request["longitude"][0],
            maximum_longitude=data_request["longitude"][1],
            minimum_latitude=data_request["latitude"][0],
            maximum_latitude=data_request["latitude"][1],
            start_datetime=time_start,
            end_datetime=time_end,
            variables=data_request["variables"], username=self.USERNAME, password=self.PASSWORD)

    def fetch_wind_copernicus(self):
        """
        send request to copernicus service for wind data
        :return: xarray dataset
        """
        data_request = self.__request.parse_for_copernicus_wind()
        self.run_wind_task(data_request)
        return self.wind

    def run_tide_task(self, data_request):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.fetch_tide_async(data_request))
        loop.close()

    async def fetch_tide_async(self, data_request):
        time_start = data_request["time"][0]
        time_end = data_request["time"][1]
        time_start, time_end = time_start.astimezone(pytz.timezone('UTC')).replace(tzinfo=None), time_end.astimezone(
            pytz.timezone('UTC')).replace(tzinfo=None)
        self.tide = copernicusmarine.open_dataset(
            dataset_id=data_request["dataset_id"],
            minimum_longitude=data_request["longitude"][0],
            maximum_longitude=data_request["longitude"][1],
            minimum_latitude=data_request["latitude"][0],
            maximum_latitude=data_request["latitude"][1],
            start_datetime=time_start,
            end_datetime=time_end,
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
        now = datetime.now().astimezone(pytz.timezone('UTC'))
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
            else:
                h = '{:03d}'.format(j)
                forecast_hour = self.map_hour(now.hour)

                url = (
                        "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfswave.pl?dir=%2Fgfs." +
                        now.strftime("%Y%m%d") + "%2F" + forecast_hour + "%2Fwave%2Fgridded&file="
                                                                         "gfswave.t" + forecast_hour +
                        "z.global.0p25.f" + h + ".grib2" + self.__request.parse_for_noaa()
                )
            filename = "ww" + forecast_time.strftime("%Y%m%d") + forecast_hour + str(j) + ".grib2"

            try:
                print(save_folder / filename)
                urlretrieve(url, save_folder / filename)
                wave_unproccessed = xr.load_dataset(save_folder / filename, engine='cfgrib')
                res["longitude"] = wave_unproccessed["longitude"].values.tolist()
                res["latitude"] = wave_unproccessed["latitude"].values.tolist()
                t = wave_unproccessed["time"].values
                t = int(t.astype('datetime64[s]').astype('int64'))
                t = t + 3600 * j
                time_data.append(t)
                j = j + 1

                for v in wave_unproccessed:
                    if v in res:
                        res[v].append(wave_unproccessed[v].values.tolist())
                    else:
                        res[v] = []
                        res[v].append(wave_unproccessed[v].values.tolist())
            except Exception as e:
                print(str(e))

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
        print("Fetching data...")
        if config.settings["noaa_active"] is True:
            if len(self.__request.noaa_variables) > 0:
                waves_and_wind = self.fetch_wave_and_wind()
        res["waves_and_wind"] = waves_and_wind
        res["copernicus"] = {}
        if len(self.__request.tide_variables) > 0:
            tides = self.fetch_tide().to_dict()
            res["copernicus"]["tides"] = tides
        if self.__request.currents_variables != [[], []]:
            currents = self.fetch_currents().to_dict()
            res["copernicus"]["currents"] = currents
        if self.__request.wind_variables != [[], []]:
            wind = self.fetch_wind_copernicus()
            wind_d = wind.to_dict()
            res["copernicus"]["wind"] = wind_d
        print("Fetching finished")
        return res

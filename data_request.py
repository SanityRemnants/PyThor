from datetime import datetime


class DataRequest:
    """
    A class that handles processing received API request and storing request data
    """

    class __RangeParam:
        def __init__(self, start, end):
            self.start = start
            self.end = end

    @staticmethod
    def __parse_variables(request_vars) -> tuple[list, list, list, list, list]:
        """
        parse variable names from the API request to corresponding variable names for NOAA and Copernicus services
        :param request_vars: API request variables
        :return: a tuple of three list: noaa variables, currents variables and tide variables
        """
        wave_and_wind_dict = {
            "wave_direction": ["var_DIRPW=on"],
            "wave_height": ["var_HTSGW=on"],
            "wave_period": ["var_PERPW=on"],
            "wind_direction": ["var_UGRD=on", "var_VGRD=on"],
            "wind_speed": ["var_WIND=on"]
        }
        curr_variables = ["sea_current_speed", "sea_current_direction"]
        curr_variables_names = ["eastward_sea_water_velocity",
                                "northward_sea_water_velocity"]  # cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i

        tide_variables_dict = {"tide_height": "zos"}  # cmems_mod_glo_phy_anfc_0.083deg_PT1H-m
        wave_variables_dict = {"wave_direction": "VMDR", "wave_height": "VHM0", "wave_period": "VTM01_SW1"}
        wind_variables = ["wind_speed", "wind_direction"]
        wind_variables_names = ["eastward_wind",
                                "northward_wind"]  # cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i
        noaa_vars = []

        wave_vars = []
        wind_vars = [[], []]

        curr_vars = [[], []]
        tide_vars = []
        request_vars.sort()
        for v in request_vars:
            if v in wave_and_wind_dict.keys():
                for name in wave_and_wind_dict[v]:
                    noaa_vars.append(name)
            if v in curr_variables:
                curr_vars[1].append(v)
                curr_vars[0] = curr_variables_names.copy()
            if v in tide_variables_dict:
                tide_vars.append(tide_variables_dict[v])
            if v in wind_variables:
                wind_vars[1].append(v)
                wind_vars[0] = wind_variables_names.copy()
            if v in wave_variables_dict:
                wave_vars.append(wave_variables_dict[v])
        return noaa_vars, curr_vars, tide_vars, wave_vars, wind_vars

    def __init__(self, latitude_start, latitude_end, longitude_start, longitude_end, time_start, time_end, interval,
                 variables):
        self.__latitude = self.__RangeParam(float(latitude_start), float(latitude_end))
        self.__longitude = self.__RangeParam(float(longitude_start), float(longitude_end))
        try:
            self.__time = self.__RangeParam(datetime.fromtimestamp(int(time_start)),
                                            datetime.fromtimestamp(int(time_end)))
        except:
            self.__time = None
        self.__time_interval = float(interval)
        self.noaa_variables, self.currents_variables, self.tide_variables, self.wave_variables, self.wind_variables = self.__parse_variables(
            variables)

    def parse_for_noaa(self) -> str:
        """
        parse API request data to fit noaa standards:
        - convert units
        - prepare correct noaa api request ending (request without specified adress and files)
        :return: noaa api request ending (containing coordinates and variables)
        """
        left = self.__longitude.start
        if left < 0:
            left = 180 + (180 + left)
        right = self.__longitude.end
        if right < 0:
            right = 180 + (180 + right)
        if right < left:
            right = 360 + right
        result = "&lev_surface=on&subregion=&toplat=" + str(self.__latitude.end) \
                 + "&leftlon=" + str(left) \
                 + "&rightlon=" + str(right) \
                 + "&bottomlat=" + str(self.__latitude.start)
        for v in self.noaa_variables:
            result += "&" + v
        return result

    def get_time(self) -> tuple[datetime, datetime]:
        """
        returns time range in datetime objects
        :return: tuple of dates (start,end)
        """
        time_start = self.__time.start
        time_end = self.__time.end
        return time_start, time_end

    def get_coordinates(self) -> dict[str, list]:
        """
        get coordinates from the API request in lat lon units
        :return: dict with structure longitude: [start,stop], latitude: [start,stop]
        """
        return {"longitude": [self.__longitude.start, self.__longitude.end],
                "latitude": [self.__latitude.start, self.__latitude.end]}

    def get_time_interval(self):
        """
        get time interval in hours
        :return: float
        """
        return self.__time_interval

    def parse_for_copernicus_currents(self) -> dict:
        """
        parse API request into copernicus request dictionary for currents variables
        :return: a dict compatible with copernicus marine API
        """
        result = {
            "dataset_id": "cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i",
            "longitude": [self.__longitude.start, self.__longitude.end],
            "latitude": [self.__latitude.start, self.__latitude.end],
            "time": [self.__time.start, self.__time.end],
            "variables": self.currents_variables[0],
            "request": self.currents_variables[1]
        }
        return result

    def parse_for_copernicus_tide(self):
        """
        parse API request into copernicus request dictionary for tide variables
        :return: a dict compatible with copernicus marine API
        """
        result = {
            "dataset_id": "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
            "longitude": [self.__longitude.start, self.__longitude.end],
            "latitude": [self.__latitude.start, self.__latitude.end],
            "time": [self.__time.start, self.__time.end],
            "variables": self.tide_variables
        }
        return result

    def parse_for_copernicus_wind(self):
        """
        parse API request into copernicus request dictionary for tide variables
        :return: a dict compatible with copernicus marine API
        """
        result = {
            "dataset_id": "cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H",
            "longitude": [self.__longitude.start, self.__longitude.end],
            "latitude": [self.__latitude.start, self.__latitude.end],
            "time": [self.__time.start, self.__time.end],
            "variables": self.wind_variables
        }
        return result

    def parse_for_copernicus_wave(self):
        """
        parse API request into copernicus request dictionary for tide variables
        :return: a dict compatible with copernicus marine API
        """
        result = {
            "dataset_id": "cmems_mod_glo_wav_anfc_0.083deg_PT3H-i",
            "longitude": [self.__longitude.start, self.__longitude.end],
            "latitude": [self.__latitude.start, self.__latitude.end],
            "time": [self.__time.start, self.__time.end],
            "variables": self.wave_variables
        }
        return result

    def is_valid(self) -> bool:
        """
        checks whether the recieved API request is valid
        :return: true if valid
        """
        if not (-180.0 <= self.__longitude.start <= 180.0):
            return False
        if not (-180.0 <= self.__longitude.end <= 180.0):
            return False
        if not (-90.0 <= self.__latitude.start <= 90.0):
            return False
        if not (-90.0 <= self.__latitude.end <= 90.0):
            return False
        if self.__latitude.start > self.__latitude.end:
            return False
        if self.__time is None:
            return False
        if len(self.tide_variables) == 0 and len(self.currents_variables) == 0 and len(self.noaa_variables) == 0:
            return False
        return True

    def __str__(self):
        result = ""
        for s in self.get_time():
            result += str(s).strip()
        result += str(self.get_time_interval())
        for s in self.get_coordinates().values():
            result += str(s[0]) + str(s[1])
        for s in self.tide_variables + self.currents_variables + self.noaa_variables:
            result += str(s)
        print(result)
        return result

from datetime import datetime

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


class DataRequest:
    class __RangeParam:
        def __init__(self, start, end):
            self.start = start
            self.end = end

    @staticmethod
    def __parse_variables(request_vars):
        noaa_vars = []
        curr_vars = []
        tide_vars = []
        for v in request_vars:
            if v in wave_and_wind_dict.keys():
                for name in wave_and_wind_dict[v]:
                    noaa_vars.append(name)
            if v in curr_variables:
                curr_vars = curr_variables_names.copy()
            if v in tide_variables_dict:
                tide_vars.append(tide_variables_dict[v])
        return noaa_vars, curr_vars, tide_vars

    def __init__(self, latitude_start, latitude_end, longitude_start, longitude_end, time_start, time_end, interval,
                 variables):
        self.__latitude = self.__RangeParam(latitude_start, latitude_end)
        self.__longitude = self.__RangeParam(longitude_start, longitude_end)
        self.__time = self.__RangeParam(datetime.fromtimestamp(int(time_start)).date,
                                        datetime.fromtimestamp(int(time_end)).date)
        self.__time_interval = interval
        self.noaa_variables, self.currents_variables, self.tide_variables = self.__parse_variables(variables)

    def parse_for_noaa(self):
        result = "&lev_surface=on&subregion=&toplat=" + self.__latitude.end \
                 + "&leftlon=" + self.__longitude.start \
                 + "&rightlon=" + self.__longitude.end \
                 + "&bottomlat=" + self.__latitude.start
        for v in self.noaa_variables:
            result += "&" + v
        return result

    def get_time(self):
        return self.__time.start, self.__time.end

    def parse_for_copernicus_currents(self):
        result = {
            "dataset_id": "cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i",
            "longitude": [self.__longitude.start, self.__longitude.end],
            "latitude": [self.__latitude.start, self.__latitude.end],
            "time": [self.__time.start, self.__time.end],
            "variables": self.currents_variables
        }
        return result

    def parse_for_copernicus_tide(self):
        result = {
            "dataset_id": "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
            "longitude": [self.__longitude.start, self.__longitude.end],
            "latitude": [self.__latitude.start, self.__latitude.end],
            "time": [self.__time.start, self.__time.end],
            "variables": self.tide_variables
        }
        return result

    def is_valid(self):
        return True

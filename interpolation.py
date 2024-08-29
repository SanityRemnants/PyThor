from copy import deepcopy

import numpy as np
from scipy.interpolate import Rbf, RegularGridInterpolator
import data_request as dr


def spherical_to_cartesian(lat, lon, r=1):
    lat_rad = np.deg2rad(lat)
    lon_rad = np.deg2rad(lon)
    x = r * np.cos(lat_rad) * np.cos(lon_rad)
    y = r * np.cos(lat_rad) * np.sin(lon_rad)
    z = r * np.sin(lat_rad)
    return x, y, z


def get_data(wave_wind_not_inter):
    lat = np.array(wave_wind_not_inter["latitude"])
    lon = np.array(wave_wind_not_inter["longitude"])
    time = np.array(wave_wind_not_inter["time"])
    return lat, lon, time

def get_copernicus_data(data):
    lat = np.array(data["coords"]["latitude"]["data"])
    lon = np.array(data["coords"]["longitude"]["data"])
    time = np.array(data["coords"]["time"]["data"])
    time = time.astype('datetime64[s]').astype('int64')
    return lat, lon, time

def check_keys(keys_to_check, wave_wind_not_inter, keys, weather, result, lon_inter, lat_inter, time_inter):
    wave_and_wind_dict = {
        "dirpw": "wave_direction",
        "swh": "wave_height",
        "perpw": "wave_period",
        "u": "u",
        "v": "v",
        "ws": "wind_speed"
    }
    for key in keys_to_check:
        if key in wave_wind_not_inter:
            if key == "dirpw":
                components = [wave_and_wind_dict[key] + "_x", wave_and_wind_dict[key] + "_y"]
                og_key = key
                for c in components:
                    key = c
                    keys.append(key)
                    key_inter = key + "_inter"
                    if key[-1] == "x":
                        weather[key] = np.cos(np.deg2rad(np.array(wave_wind_not_inter[og_key])))
                    else:
                        weather[key] = np.sin(np.deg2rad(np.array(wave_wind_not_inter[og_key])))

                    weather[key + "_mask"] = np.isnan(weather[key]).astype(float)
                    print(weather[key + "_mask"])
                    keys.append(key + "_mask")
                    result[key_inter] = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in
                                         range(len(time_inter))]
                    result[key + "_mask" + "_inter"] = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in
                                                        range(len(time_inter))]
            else:
                keys.append(wave_and_wind_dict[key])
                key_inter = wave_and_wind_dict[key] + "_inter"
                weather[wave_and_wind_dict[key]] = np.array(wave_wind_not_inter[key])
                weather[wave_and_wind_dict[key] + "_mask"] = np.isnan(weather[wave_and_wind_dict[key]]).astype(float)
                print(weather[wave_and_wind_dict[key] + "_mask"])
                keys.append(wave_and_wind_dict[key] + "_mask")
                result[key_inter] = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in
                                     range(len(time_inter))]
                result[wave_and_wind_dict[key] + "_mask" + "_inter"] = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in
                                                    range(len(time_inter))]


def latlon_interpolation(time, weather, key, lat_grid, lon_grid, lat_inter_grid, lon_inter_grid, res):
    for k in range(len(time)):
        elem = weather[key]
        nan_mask = np.isnan(elem[k])
        indices = np.where(~nan_mask)
        data_points_valid = elem[k][indices]
        lat_valid = lat_grid[~nan_mask]
        lon_valid = lon_grid[~nan_mask]
        x, y, z = spherical_to_cartesian(lat_valid.ravel(), lon_valid.ravel())
        interp_spatial = Rbf(x, y, z, data_points_valid, function='thin_plate', smooth=0)

        x_inter, y_inter, z_inter = spherical_to_cartesian(lat_inter_grid, lon_inter_grid)
        res[k] = interp_spatial(x_inter, y_inter, z_inter)


def time_interpolation(time, lat_inter, lon_inter, res, key, time_inter, result, weather):
    interpolator = RegularGridInterpolator((time, lat_inter, lon_inter), res)
    key_inter = key + "_inter"
    for k in range(len(time_inter)):
        for i in range(len(lat_inter)):
            for j in range(len(lon_inter)):
                result[key_inter][k][i][j] = interpolator([time_inter[k], lat_inter[i], lon_inter[j]])
    weather[key] = [[[float(value[0]) for value in row] for row in slice_] for slice_ in result[key_inter]]


def apply_nan_masc(keys_to_iter, weather, land_treshhold):
    for k in keys_to_iter:
        if "mask" in k:
            key_to_nan = k.replace("_mask", "")
            for t in range(len(weather[key_to_nan])):

                for l in range(len(weather[key_to_nan][t])):
                    wl = weather[k][t][l]
                    for lt in range(len(weather[key_to_nan][t][l])):
                        wlt = wl[lt]
                        if wlt >= land_treshhold:
                            weather[key_to_nan][t][l][lt] = np.NaN
            # weather.pop(k)


def interpolate_for_copernicus(weather, result, request):
    if isinstance(request, dr.DataRequest):
        interval = request.get_time_interval()
    cop_weather = {}
    try:
        data = result["copernicus"]
    except:
        return weather
    resoution = 0.15
    land_treshhold = 0.5
    for el in data:
        element = data[el]
        lat, lon, time = get_copernicus_data(element)

        if weather != {}:
            lat_inter = weather["lat_inter"]
            lon_inter = weather["lon_inter"]
            time_inter = weather["time_inter"]
        else:
            if weather["time_inter"][0] != time[-1]:
                time_inter = np.arange(time[0], time[-1], int(interval * 3600))
            else:
                time_inter = time
            lat_inter = np.arange(lat[0], lat[-1], resoution)
            lon_inter = np.(lon[0], lon[-1], resoution)
            weather["time_inter"] = time_inter.tolist()
            weather["lat_inter"] = lat_inter.tolist()
            weather["lon_inter"] = lon_inter.tolist()

        lon_grid, lat_grid = np.meshgrid(lon, lat)
        lon_inter_grid, lat_inter_grid = np.meshgrid(lon_inter, lat_inter)
        for key in element["data_vars"]:
            res = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in range(len(time))]
            key_inter = key + "_inter"
            result[key_inter] = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in
                                 range(len(time_inter))]
            reduced_array = [sublist[0] for sublist in element["data_vars"][key]["data"]]
            if 1 == 0:
                cop_weather[key] = np.array(reduced_array)
                cop_weather[key + "_mask"] = np.isnan(reduced_array).astype(float)
                latlon_interpolation(time, cop_weather, key, lat_grid, lon_grid, lat_inter_grid, lon_inter_grid, res)
                time_interpolation(time, lat_inter, lon_inter, res, key, time_inter, result, cop_weather)
            else:
                cop_weather[key] =  reduced_array
                weather["time_inter"] = time
                weather["lat_inter"] = lat
                weather["lon_inter"] = lon


    keys_to_iter = deepcopy(list(cop_weather.keys()))
    apply_nan_masc(keys_to_iter, cop_weather, land_treshhold)
    weather_copy = cop_weather.copy()
    for key in cop_weather:
        if key[-5:] != "_mask":
            if key == "zos":
                weather["tide_height"] = cop_weather[key]
            else:
                weather[key] = cop_weather[key]
    try:
        curr_request = request.parse_for_copernicus_currents()["request"]
    except:
        return weather
    for e in curr_request:
        if e == "sea_current_direction":
            key_weather = np.arctan2(weather["uo"], weather["vo"]) * (180 / np.pi) + 180
            key_weather = np.mod(key_weather, 360)
            weather[e] = key_weather
        elif e == "sea_current_speed":
            wind_speed = np.sqrt(weather["uo"] ** 2 + weather["vo"] ** 2)
            weather[e] = wind_speed
    del weather["uo"]
    del weather["vo"]

    return weather


def interpolate(result, request):
    if isinstance(request, dr.DataRequest):
        interval = request.get_time_interval()
    resoution = 0.15
    land_treshhold = 0.5
    weather = {}
    wave_wind_not_inter = result["waves_and_wind"]
    if wave_wind_not_inter is not None:
        lat, lon, time = get_data(wave_wind_not_inter)
        lat_inter = np.arange(lat[0], lat[-1], resoution)
        lon_inter = np.arange(lon[0], lon[-1], resoution)
        if time[0] != time[-1]:
            time_inter = np.arange(time[0], time[-1], int(interval * 3600))
        else:
            time_inter = time

        keys_to_check = ["dirpw", "swh", "perpw", "u", "v", "ws"]
        keys = []

        check_keys(keys_to_check, wave_wind_not_inter, keys, weather, result, lon_inter, lat_inter, time_inter)

        lon_grid, lat_grid = np.meshgrid(lon, lat)
        lon_inter_grid, lat_inter_grid = np.meshgrid(lon_inter, lat_inter)
        res = [[[0] * len(lon_inter) for _ in range(len(lat_inter))] for _ in range(len(time))]

        for key in keys:
            latlon_interpolation(time, weather, key, lat_grid, lon_grid, lat_inter_grid, lon_inter_grid, res)
            time_interpolation(time, lat_inter, lon_inter, res, key, time_inter, result, weather)

        keys_to_iter = deepcopy(list(weather.keys()))

        apply_nan_masc(keys_to_iter, weather, land_treshhold)
        weather_copy = weather.copy()
        for el in weather_copy:
            if el[-2:] == "_x":
                key = el[:-2]
                key_weather = np.rad2deg(np.arctan2(weather[key + "_y"], weather[key + "_x"]))
                key_weather = np.mod(key_weather, 360)
                weather[key] = [[[float(value) for value in row] for row in slice_] for slice_ in key_weather]
                del weather[key + "_x"]
                del weather[key + "_y"]
            elif el == "v":
                key = "wind_direction"
                key_weather=  np.arctan2(weather["u"], weather["v"]) * (180 / np.pi) + 180
                key_weather = np.mod(key_weather, 360)
                weather[key] = [[[float(value) for value in row] for row in slice_] for slice_ in key_weather]
                del weather["u"]
                del weather["v"]
            elif el[-4:]  == "mask":
                del weather[el]


        weather["time_inter"] = time_inter.tolist()
        # weather["time"] = time.tolist()

        # weather["normal"] = normal
        # weather["lat"] = lat.tolist()
        # weather["lon"] = lon.tolist()
        weather["lat_inter"] = lat_inter.tolist()
        weather["lon_inter"] = lon_inter.tolist()

    return interpolate_for_copernicus(weather, result, interval)

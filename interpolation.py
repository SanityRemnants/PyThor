from copy import deepcopy
import numpy as np
from scipy.interpolate import Rbf, RegularGridInterpolator


def spherical_to_cartesian(lat, lon, r=1):
    """
    Converts spherical coordinates (latitude, longitude, radius) to Cartesian coordinates (x, y, z).

    :param lat: Latitude in degrees.
    :param lon: Longitude in degrees.
    :param r: Radius, default is 1.
    :return: Tuple of Cartesian coordinates (x, y, z).
    """
    lat_rad = np.deg2rad(lat)
    lon_rad = np.deg2rad(lon)
    x = r * np.cos(lat_rad) * np.cos(lon_rad)
    y = r * np.cos(lat_rad) * np.sin(lon_rad)
    z = r * np.sin(lat_rad)
    return x, y, z


def prepare_interpolation_grids(lat, lon, time, interval, resolution=0.15):
    """
    Prepares the latitude, longitude, and time grids for interpolation.

    :param lat: Array of latitudes.
    :param lon: Array of longitudes.
    :param time: Array of time points.
    :param interval: Time interval for interpolation in hours.
    :param resolution: Resolution for latitude and longitude grids.
    :return: Interpolated latitude, longitude, and time grids.
    """
    lat_inter = np.arange(lat[0], lat[-1], resolution)
    lon_inter = np.arange(lon[0], lon[-1], resolution)
    time_inter = np.arange(time[0], time[-1], int(interval * 3600)) if time[0] != time[-1] else time
    return lat_inter, lon_inter, time_inter


def initialize_result_containers(keys, lat_inter, lon_inter, time_inter):
    """
    Initializes containers for the results and masks.

    :param keys: List of keys to be interpolated.
    :param lat_inter: Interpolated latitude grid.
    :param lon_inter: Interpolated longitude grid.
    :param time_inter: Interpolated time grid.
    :return: Initialized result and weather containers.
    """
    result = {}
    weather = {}
    for key in keys:
        key_inter = key + "_inter"
        result[key_inter] = np.zeros((len(time_inter), len(lat_inter), len(lon_inter)))
        result[key + "_mask_inter"] = np.zeros((len(time_inter), len(lat_inter), len(lon_inter)))
    return result, weather


def interpolate_spatial_data(weather, keys, lat_grid, lon_grid, lat_inter_grid, lon_inter_grid):
    """
    Interpolates spatial data using Radial Basis Function (RBF).

    :param weather: Dictionary containing weather data.
    :param keys: List of keys to be interpolated.
    :param lat_grid: Original latitude grid.
    :param lon_grid: Original longitude grid.
    :param lat_inter_grid: Interpolated latitude grid.
    :param lon_inter_grid: Interpolated longitude grid.
    :return: Interpolated spatial data.
    """
    res = {key: np.zeros((len(weather[key]), len(lat_inter_grid), len(lon_inter_grid))) for key in keys}
    for key in keys:
        for k in range(len(weather[key])):
            elem = weather[key]
            nan_mask = np.isnan(elem[k])
            indices = np.where(~nan_mask)
            data_points_valid = elem[k][indices]
            lat_valid = lat_grid[~nan_mask]
            lon_valid = lon_grid[~nan_mask]
            x, y, z = spherical_to_cartesian(lat_valid.ravel(), lon_valid.ravel())
            interp_spatial = Rbf(x, y, z, data_points_valid, function='thin_plate', smooth=0)

            x_inter, y_inter, z_inter = spherical_to_cartesian(lat_inter_grid, lon_inter_grid)
            res[key][k] = interp_spatial(x_inter, y_inter, z_inter)
    return res


def interpolate_temporal_data(res, keys, time, lat_inter, lon_inter, time_inter):
    """
    Interpolates temporal data using RegularGridInterpolator.

    :param res: Interpolated spatial data.
    :param keys: List of keys to be interpolated.
    :param time: Original time grid.
    :param lat_inter: Interpolated latitude grid.
    :param lon_inter: Interpolated longitude grid.
    :param time_inter: Interpolated time grid.
    :return: Interpolated temporal data.
    """
    for key in keys:
        interpolator = RegularGridInterpolator((time, lat_inter, lon_inter), res[key])
        key_inter = key + "_inter"
        for k in range(len(time_inter)):
            for i in range(len(lat_inter)):
                for j in range(len(lon_inter)):
                    res[key][k][i][j] = interpolator([time_inter[k], lat_inter[i], lon_inter[j]])
    return res


def apply_land_mask(weather, keys, land_threshold=0.5):
    """
    Applies land mask to the interpolated data based on the given threshold.

    :param weather: Dictionary containing weather data.
    :param keys: List of keys to be masked.
    :param land_threshold: Threshold to identify land areas.
    :return: Weather data with land mask applied.
    """
    keys_to_iter = deepcopy(list(weather.keys()))
    for k in keys_to_iter:
        if "mask" in k:
            key_to_nan = k.replace("_mask", "")
            for t in range(len(weather[key_to_nan])):
                for l in range(len(weather[key_to_nan][t])):
                    for lt in range(len(weather[key_to_nan][t][l])):
                        if weather[k][t][l][lt] >= land_threshold:
                            weather[key_to_nan][t][l][lt] = np.NaN
    return weather


def interpolate(result, interval):
    """
    Main function to interpolate wave and wind data over latitude, longitude, and time.

    :param result: Dictionary containing non-interpolated wave and wind data.
    :param interval: Time interval for interpolation in hours.
    :return: Dictionary with interpolated wave and wind data.
    """
    wave_wind_not_inter = result["waves_and_wind"]
    lat = np.array(wave_wind_not_inter["latitude"])
    lon = np.array(wave_wind_not_inter["longitude"])
    time = np.array(wave_wind_not_inter["time"])

    lat_inter, lon_inter, time_inter = prepare_interpolation_grids(lat, lon, time, interval)

    keys_to_check = ["dirpw", "swh", "perpw", "u", "v", "ws"]
    keys = [key for key in keys_to_check if key in wave_wind_not_inter]
    weather = {key: np.array(wave_wind_not_inter[key]) for key in keys}
    for key in keys:
        weather[key + "_mask"] = np.isnan(weather[key]).astype(float)

    result, weather = initialize_result_containers(keys, lat_inter, lon_inter, time_inter)

    lon_grid, lat_grid = np.meshgrid(lon, lat)
    lon_inter_grid, lat_inter_grid = np.meshgrid(lon_inter, lat_inter)

    spatial_data = interpolate_spatial_data(weather, keys, lat_grid, lon_grid, lat_inter_grid, lon_inter_grid)
    temporal_data = interpolate_temporal_data(spatial_data, keys, time, lat_inter, lon_inter, time_inter)

    for key in keys:
        weather[key] = temporal_data[key].tolist()

    weather = apply_land_mask(weather, keys)

    weather["time_inter"] = time_inter.tolist()
    weather["lat_inter"] = lat_inter.tolist()
    weather["lon_inter"] = lon_inter.tolist()

    return weather

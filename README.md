## What is PyThor?
PyThor is a library designed to allow the user to access marine data and weather forecasts provided by National Oceanic and Atmospheric Administration and Copernicus Marine Service.

  ## Using the library and constructing queries
To use the data provided by Copernicus Marine Service, you must have a free account on [the website](https://data.marine.copernicus.eu/register). After creating the account, login details should be provided in the config.yaml file, supplementing the data in the following fragment of the file:
```
coppernicus_acount:
  username: ""
  password: ""
```
An account is only required to obtain data on tides and sea currents, an account is not required to use other functionalities of the library.
Downloading data from the copernicus website results in a noticeably longer execution time.

The application runs at 127.0.0.1:5000 by default.

To obtain weather data, please submit a query in the following format:

/api/weather?latitude_start=**latitude_start**&latitude_end=**latitude_end**&longitude_start=**longitude_start**&longitude_end=**longitude_end**&variables=**variables**&time_start=**time_start**&time_end=**time_end**

- **latitude_start** - latitude origin in dotted floating point format
- **latitude_end** - end of latitude in dotted floating point format
- **longitude_start** - longitude start in dotted floating point format
- **longitude_end** - end of longitude in dotted floating point format
- **variables** - expected weather data parameters separated by a commas
- **time_start** - the beginning of the time for which we want to obtain data in Unix time format
- **time_end** - end of time for which we want to obtain data in Unix time format (providing the same value as in the **time_start** field will return data for a point in time)


## sample query:
[http://127.0.0.1:5000/api/weather?latitude_start=36&latitude_end=37&longitude_start=15&longitude_end=16&variables=wave_direction,wave_height,wave_period,wind_direction,wind_speed&time_start=1715415818&time_end=1715441018](http://127.0.0.1:5000/api/weather?latitude_start=36&latitude_end=37&longitude_start=15&longitude_end=16&variables=wave_direction,wave_height,wave_period,wind_direction,wind_speed&time_start=1715415818&time_end=1715441018)

## weather parameters:
- wave_direction
- wave_height
- wave_period
- wind_direction
- wind_speed
- sea_current_speed
- sea_current_direction
- tide_height

## Instalation
### Anaconda
Run: \
    ```conda create --name <envname> --file requirements.txt``` \
In order to install all the required libraries for the app to function.

Currently only conda installation is supported due to some libraries not being compatible with pip

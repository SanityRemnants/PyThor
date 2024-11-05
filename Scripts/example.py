from PyThor import runPythor
from PyThor.app_pythor import config

config.override({"coppernicus_acount": {
    "username": "",
    "password": ""},
    "resolution": 0.15,
    "land_treshhold": 0.2,
    "clear_cache": True})
runPythor(host='localhost', port=8080)

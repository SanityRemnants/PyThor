import atexit
import os

from flask import Flask, request, Response

from PyThor.config.config import Config
from PyThor.data.data_request import DataRequest
from PyThor.data.fetcher import Fetcher
from PyThor.data.interpolation import interpolate
import json

config = Config()
clear_cache = config.settings["clear_cache"]


def clear_c():
    files = os.listdir("./cache/")
    for f in files:
        os.remove("./cache/" + f)
    os.rmdir("cache/")


if clear_cache:
    atexit.register(clear_c)

app = Flask(__name__)

if not os.path.exists('cache'):
    os.mkdir("cache")


@app.route('/')
def index():
    return "PyThor is working"


@app.route('/api/weather')
def root():
    data_request = DataRequest(request.args.get('latitude_start'), request.args.get('latitude_end'),
                               request.args.get('longitude_start'), request.args.get('longitude_end'),
                               request.args.get('time_start'), request.args.get('time_end'),
                               request.args.get('interval', 60),
                               request.args.get('variables', "").replace(" ", "").split(","))
    file_name = str(data_request)
    print("Checking cache folder...")
    if not os.path.isfile(f'cache/{file_name}.json'):
        print("Cache miss")
        time = [int(request.args.get('time_start')), int(request.args.get('time_end'))]
        if not data_request.is_valid():
            return Response(status=400)
        result = Fetcher(data_request).fetch()

        res = interpolate(result, data_request, time)

        with open(f'cache/{file_name}.json', 'w') as f:
            json.dump(res, f)
        return res
    else:
        print("Cache hit")
        with open(f'cache/{file_name}.json', 'r') as f:
            return json.load(f)


def runPythor(host="127.0.0.1", port=5000):
    app.run(host=host, port=port)


if __name__ == '__main__':
    runPythor()
# print(fetch_wave(0, 0))

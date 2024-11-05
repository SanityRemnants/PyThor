from argparse import ArgumentParser
from PyThor import PyThor

parser = ArgumentParser(description="PyThor: A tool to download and interpolate weather forecasts. Default address: 127.0.0.1 and port: 5000")
parser.add_argument("-a","--address", help="Endpoint address", type=str)
parser.add_argument("-p","--port", help="Endpoint port", type=int)
args = parser.parse_args()

PyThor.runPythor(args.address, args.port)

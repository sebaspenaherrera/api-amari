'''
This file presents the default parameters that are used for the API.

The parameters are:
- host: the host of the API
- port: the port of the API
- reload: if the API should reload on changes
- data_path: the path where the data is stored
- local_data_path: the path where the local data is stored
TODO:
- date: the current date
- time: the current time
- datetime: the current datetime
- log_path: the path where the logs are stored
- log_file: the log file
- log_level: the log level
- log_format: the log format
'''

API_APP = "rest.endpoints:app"
API_PORT = 8000
API_HOST = "0.0.0.0"
API_RELOAD = True
API_DATA_PATH = "./data"
N_SAMPLES = 20
HOST_NAME = "amari-api"
AMARI_HOST = "192.168.159.160"
AMARI_PORT = 5000
AMARI_PATH = "/root/lteenb-linux-2024-12-13"
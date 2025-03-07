# *************************************************************************************************
# REST utilities
# Description: This file contains the synchronous/async methods that are used by the REST Server
# Author: Sebastian Peñaherrera
# Date: 04/03/2025
# Last Updated: 04/03/2025
# Version: 0.1
# Status: Under development
# *************************************************************************************************

import json
import time
import os
import re
from datetime import datetime
from config.configurator import ConfigManager
from termcolor import colored

def get_timestamp():
    '''
    Return the current timestamp

    Returns:
    - The current timestamp
    '''

    ts = int(time.time())
    return ts


def get_date():
    '''
    Return the current date

    Returns:   
    - The current date
    '''

    date = datetime.now().date()
    return date


def get_time():
    '''
    Return the current time

    Returns:
    - The current time
    '''

    current_time = datetime.now().time()
    return current_time


def get_current_dir(file):
    '''
    Return the current directory

    Returns:
    - The current directory
    '''

    return os.path.dirname(os.path.realpath(file.__file__))

def check_dir(path: str):
    '''
    Check if a directory exists

    Parameters:
    path: str. The path to the directory

    Returns:
    - True if the directory exists, False otherwise
    '''

    return os.path.exists(path)


def create_dir(path: str):
    '''
    Create a directory in the specified path

    Parameters:
    path: str. The path to the directory

    Returns:
    - The directory has been created
    '''
    
    if not check_dir(path):
        os.mkdir(path)
        print("The directory {} has been created".format(path))
    else:
        print("The directory {} already exists".format(path))


def check_local_data_path(path: str):
    '''
    Check if the local data path exists, else create it

    Parameters:
    path: str. The path to the local data

    Returns:
    - None
    '''

    # Check if the ./data directory exists, else create it
    if not check_dir(path):
        create_dir(path)

    # Check if the ./data_path/date exists, else create it
    local_path = get_local_data_path()
    if not check_dir(local_path):
        create_dir(local_path)


def get_local_data_path():
    '''
    Returns the path to the ./{API_DATA_PATH}/{current_date}

    Returns:
    - The path to the local data
    '''

    return f"{ConfigManager.get_parameters('API_DATA_PATH')}/{get_date()}"


def check_file(path: str):
    '''
    Check if a file exists

    Parameters:
    path: str. The path to the file

    Returns:
    - True if the file exists, False otherwise
    '''

    return os.path.exists(path)


def write_file(path: str, content: json, mode: str = 'w'):
    '''
    Write a json content to a file

    Parameters:
    path: str. The path to the file
    content: json. The content to be written
    mode: str, default='w'. The mode to open the file

    Returns:
    - None
    '''
    
    # Check is the directory exists
    check_local_data_path(ConfigManager.get_parameters('rest_data_path'))
    # check_local_data_path(Parameters.rest_data_path)

    # Check if the file already exists
    if check_file(path):
        with open(path, mode=mode) as file:
            json.dump(content, file, indent=4)
    else:
        with open(path, mode='w') as file:
            json.dump(content, file, indent=4)


def convert_dict_to_json(data: dict):
    '''
    Wrapper that parses a dictionary into a json string

    Parameters:
    - data: dict. The dictionary to be parsed

    Returns:
    - The json string: str
    '''
    
    # Convert the dict to json
    return json.dumps(data, indent=4)


def generate_file_path(timestamp: str, dir_path: str):
    '''
    Generate the file path to save the stats. The format is ./data_path/date/Stats_timestamp.json

    Parameters:
    - timestamp: str. The timestamp of the stats
    - dir_path: str. The path to the directory

    Returns:
    - The path to the file
    '''
    
    return "{}/Stats_{}.json".format(dir_path, timestamp)


def parse_string_to_int(input_str):
    '''
    This method parses a string in different formats to an integer

    Parameters:
    - input_str: str. The string to be parsed

    Returns:
    - The parsed integer
    '''
    
    # If input_str is None, return None
    if input_str is None:
        return input_str

    # If input is empty, return None
    if input_str == "":
        return None

    # If the input is a number, return it
    if isinstance(input_str, int):
        return input_str

    # If the string has special characters, do not parse it
    #if not input_str.isalnum():
    #    return input_str

    # If the string is a hexadecimal number, parse it to int
    if input_str.startswith('0x'):
        return int(input_str, 16)

    # If the string is a hexadecimal number without '0X' at the beginning , parse it to int
    if re.match(r'([A-F]+\d*)', input_str):
        return int(input_str, 16)

    # Use regular expression to extract numeric part
    match = re.match(r'([-+]?\d*\.\d+|[-+]?\d+)', input_str)
    if match:
        numeric_part = match.group(0)
        return int(float(numeric_part))

    # Use regular expression to extract numeric part, if it contains [<>=] symbols
    match = re.match(r'(?:[<>=])+(\d+)', input_str)
    if match:
        numeric_part = match.group(1)
        return int(numeric_part)

    # If parsing fails, returns string
    return ""


def log_message(message: str, type: str = 'INFO', entity: str = 'REST Server', limit: int = 1000, bold: bool = False):
    '''
    This method logs a message to the console

    Parameters:
    - message: str. The message to be logged
    - type: str, default='INFO'. The type of the message (INFO or ERROR)
    - entity: str, default='REST Server'. The entity that logs the message
    - limit: int, default=1000. The limit of the message to be logged
    - bold: bool, default=False. If True, the message is bold

    Returns:
    - None
    '''
    
    if len(message) > limit:
        message = message[:limit] + '...'

    if bold:
        attr = ['bold']
    else:
        attr = []

    # Log the message
    if type == 'INFO':
        print(f'{get_time()} ({entity}) --> {colored(message, "cyan", attrs=attr)}')
    elif type == 'ERROR':
        print(f'{get_time()} ({entity}) --> {colored(message, "red", attrs=attr)}')
    elif type == 'WARNING':
        print(f'{get_time()} ({entity}) --> {colored(message, "yellow", attrs=attr)}')
    elif type == 'DEBUG':
        print(f'{get_time()} ({entity}) --> {colored(message, "blue", attrs=attr)}')
    elif type == 'HIGHLIGHT':
        print(f'{get_time()} ({entity}) --> {colored(message, "magenta", attrs=attr)}')
    elif type == 'SUCCESS':
        print(f'{get_time()} ({entity}) --> {colored(message, "green", attrs=attr)}')
    else:        
        print(f'{get_time()} ({entity}) --> {colored(message, "white", attrs=attr)}')
'''
Developed by: Sebastian Peñaherrera. Thanks to Carlos Baena for the initial version of the API
Date: 04/03/2025
Last Updated: 04/03/2025
Version: 0.1

Description: This is the main file for the API that interfaces the AMARI.
'''

import uvicorn
from utils.utils import *
from config.defaultParams import *
from config.configurator import ConfigManager
import argparse


if __name__ == "__main__":
    # Create the input ArgumentParser
    parser = argparse.ArgumentParser(description='This is the main file for the REST Server for that exposes the API.')

    # Add the input parameters
    parser.add_argument('--host', type=str, help='REST host address', default=API_HOST)
    parser.add_argument('--port', type=int, help='REST host port', default=API_PORT)
    parser.add_argument('--amari-host', type=str, help="CROWDCELL'S host address", default=API_HOST)
    parser.add_argument('--amari-port', type=int, help="CROWDCELL'S host port", default=API_PORT)

    # Parse the command-line arguments
    args = parser.parse_args()

    # Extract key-value pair arguments
    ConfigManager.update_parameters("API_HOST", args.host)
    ConfigManager.update_parameters("API_PORT", args.port)
    ConfigManager.update_parameters("API_AMARI_HOST", args.amari_host)
    ConfigManager.update_parameters("API_AMARI_PORT", args.amari_port)

    # Check if the local_data_path exists, if not create it
    check_local_data_path(ConfigManager.get_parameters('API_DATA_PATH'))

    # Run the rest API app using Uvicorn with the parameters in config_parameters file
    uvicorn.run(app=ConfigManager.get_parameters('API_APP'), 
                port=ConfigManager.get_parameters('API_PORT'), 
                host=ConfigManager.get_parameters('API_HOST'),
                reload=ConfigManager.get_parameters('API_RELOAD'))
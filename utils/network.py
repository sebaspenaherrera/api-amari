'''
Description: This file contains the network utility functions.
Author: Sebastian Peñaherrera
Date: 07/03/2025
Last Updated: 07/03/2025
Version: 0.1
Status: Under development
*************************************************************************************************
'''

import httpx
from config.configurator import ConfigManager
from utils.utils import log_message
from config.defaultParams import HOST_NAME


class NetworkTools:
    '''
    This class contains the network utility functions
    '''
    
    @staticmethod
    async def configure_http_request(request_type: str = 'GET', host_address: str = '127.0.0.1', port: int | str = 5000, resource: str = '/', headers: dict = None, query: dict = None, data: dict = None, message: str = None, timeout: int = 5):
        '''
        This async function sends a http request to the specified host_address and port

        Parameters:
        -----------------------------------------------------------------------------------------
        - request_type: str, default='GET'. The type of the request to be sent
        - host_address: str, default='
        - port: int | str, default=5000. The port of the host_address
        - resource: str, default='/monitoring'. The resource to be accessed in the host_address
        - headers: dict, default=None. The headers of the request
        - query: dict, default=None. The query parameters of the request
        - data: dict, default=None. The data to be sent in the request
        - message: str, default=None. The message to be printed to the console

        Returns:
        -----------------------------------------------------------------------------------------
        - A dictionary with the response data and the response status code
        '''
        
        # Check the input parameters
        if isinstance(port, str):
            port = port
        else:
            port = str(port)
        
        # If host_address contains '.' then it is an IP address
        if '.' in host_address:
            host_address = host_address
        else:
            host_address = ConfigManager.get_parameters(host_address)

        # Configure the header
        base = "http://" + host_address + ":" + port

        if headers is None:
            headers =   {
                        'content-type': 'application/json', 
                        'accept': 'application/json'
                        }

        # Create an httpx request
        async with httpx.AsyncClient() as client:
            try:
                log_message(entity=HOST_NAME, message=f'Sending {request_type} request to {base+resource}', type='INFO')
                if request_type == 'GET':
                    response = await client.get(base+resource, headers=headers, params=query, timeout=timeout)
                elif request_type == 'POST':
                    response = await client.post(base+resource, headers=headers, json=data, params=query, timeout=timeout)
                
                response.raise_for_status()
                reason = response.reason_phrase
            except httpx.RequestError as exc:
                log_message(message=f"An error occurred while requesting {exc.request.url!r}. Error: {exc.__class__.__name__}.", type='ERROR')
                return None, 500, exc.__class__.__name__
            except httpx.HTTPStatusError as exc:
                log_message(message=f'Error sending request: {request_type} to {base+resource}: {exc.response.status_code}', type='ERROR')
                return None, exc.response.status_code, exc.response.reason_phrase
        
        status = response.status_code 
        data_received = response.json()

        # Log the message
        if message is not None:
            if status == 200:
                log_message(entity=HOST_NAME, message=f'Succesful request: {message}', type='SUCCESS')
            else:
                log_message(entity=HOST_NAME, message=f'Unsuccesful request: {message}', type='ERROR')
        else:
            log_message(entity=HOST_NAME, message=f'Request status: {status}', type='DEBUG')

        # Return the response
        return data_received, status, reason
    

    @staticmethod
    async def process_http_response(response: dict, status: int, reason: str, message: str = None):
        '''
        This async function processes the http response

        Parameters:
        -----------------------------------------------------------------------------------------
        - response: dict. The response data
        - status: int. The response status code
        - reason: str. The response reason phrase
        - message: str, default=None. The message to be printed to the console

        Returns:
        -----------------------------------------------------------------------------------------
        - None
        '''
        
        # Log the message
        if message is not None:
            if status == 200:
                log_message(entity=HOST_NAME, message=f'Succesful response: {message}', type='SUCCESS')
            else:
                log_message(entity=HOST_NAME, message=f'Unsuccesful response: {message}', type='ERROR')
        else:
            log_message(entity=HOST_NAME, message=f'Response status: {status}', type='DEBUG')
        
        # Return the response
        return response, status, reason
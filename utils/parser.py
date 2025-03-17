"""
Description: This module contains the parser for the Amari API.
"""

import json
from utils.utils import log_message

class Parser:

    @staticmethod
    def check_response(data: dict) -> bool:
        """Checks if the response is valid."""
        if "error" in data:
            return False
        else:
            return True
        

    @staticmethod
    def parse_response(data: str) -> dict:
        """Parses the response from the CLI command."""
        start_idx = data.find("{")  # Find the start of the actual JSON content
        end_idx = data.rfind("}") + 1  # Find the end of the actual JSON content
        json_str = data[start_idx:end_idx]

        # Try parsing the JSON
        try:
            parsed_data = json.loads(json_str)

            # Check if the response is valid
            if Parser.check_response(parsed_data):
                return parsed_data, True
            else:
                return parsed_data, False
        except json.JSONDecodeError as e:
            log_message(entity='Parser', message=f"Error parsing JSON: {e}", type='ERROR')
            return {"error": f"Error parsing JSON: {e}"}
        
    
    @staticmethod
    def search_parameter(params: dict, key: str) -> str:
        """Searches for a parameter in a dictionary."""
        if key in params:
            return params[key]
        else:
            return None

        
"""
Description: This module contains the parser for the Amari API.
"""

import json
import re
from utils.utils import log_message

class Parser:

    @staticmethod
    def check_cli_error(code: int) -> bool:
        """Checks if the CLI command returned an error."""
        if code == 0:
            return False
        else:
            return True
        

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
        

    @staticmethod
    def extract_pdsch_messages(log_data, discard_si: bool = False) -> dict:
        """Extracts PDSCH messages from the log data"""
        pdsch_messages = {}
        
        # Check if response and logs exist
        if log_data.get("status") and "response" in log_data and "logs" in log_data["response"]:
            logs = log_data["response"]["logs"]
            
            # Iterate through logs and filter PDSCH channel messages
            for log in logs:
                if log.get("channel") == "PDSCH":
                    if discard_si:
                        if "si" not in log.get("data")[0]:
                            pdsch_messages[log.get("timestamp")] = Parser.parse_log_data(log.get("data")[0])
                        else:
                            continue
                    else:
                        pdsch_messages[log.get("timestamp")] = Parser.parse_log_data(log.get("data")[0])

        return pdsch_messages
    

    @staticmethod
    def parse_log_data(line: list[str]) -> dict:
        """Parses the data field from the log file"""

        parsed_dict = {}
        # Regular expression to match key-value pairs
        matches = re.findall(r'(\w+)=([\w:.]+)', line)

        for key, value in matches:
            # If the value contains ":", split it into start and end
            if ':' in value:
                start, end = map(int, value.split(':'))
                parsed_dict[f"{key}_start"] = start
                parsed_dict[f"{key}_end"] = end
            elif value.isdigit():
                parsed_dict[key] = int(value)  # Convert to integer
            elif re.match(r'^\d+\.\d+$', value):  
                parsed_dict[key] = float(value)  # Convert to float
            else:
                parsed_dict[key] = value  # Keep as string if not numeric

        return parsed_dict

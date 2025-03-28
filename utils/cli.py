"""
This module contains the CLI utilities for the Amari API.
"""
import subprocess
import json
from utils.parser import Parser
from config.configurator import ConfigManager
from utils.utils import log_message

class Cli:

    @staticmethod
    async def execute_command(entity: str, message: dict):
        """Runs the CLI command with a dynamic message."""

        # Convert dictionary to a valid JSON string
        message_str = json.dumps(message)  
        command = ["./ws.js", entity, message_str]
        log_message(entity="CLI", message=f"Executing command: {' '.join(command)}", type="INFO")
        working_directory = ConfigManager.get_parameters('AMARI_PATH')
        
        try:
            result = subprocess.run(command, cwd=working_directory, capture_output=True, text=True, check=True)
            response, status = Parser.parse_response(data=result.stdout)
            return {"status": status, "response": response}
        except subprocess.CalledProcessError as e:
            return {"status": 500, "response" : None, "error": e.stderr or str(e)}
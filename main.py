"""
main.py

This module runs a test of the Autolab class with our preset json file
NOTE ALL JSON PATHS MUST REFER TO A PATH IN THE /Autolab
     WORKING DIRECTORY

Usage:
- Set the 'input_json_path' variable
- Run this script

Created: 07/11/2023

"""

from autolab import Autolab

# Place your JSON path here (default is "inputs_win.json")
input_json_path = "inputs_win.json"

if __name__ == "__main__":
    autolab = Autolab()
    instructions = autolab.generate_procedure(input_json_path, cleanup=True, enable_logging=True)
    print(type(instructions))
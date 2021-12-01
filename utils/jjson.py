import json
from pathlib import Path

def get_path():
    """
    A function to get the current path to main.py

    Returns:
     - cwd (string) : Path to main.py directory
    """
    cwd = Path(__file__).parent[1]
    return str(cwd)

def read_json(filename):
    """
    A function to read a json file and return the data.

    Params:
     - filename (string) : The name of the file to open

    Returns:
     - data (dict) : A dict of the data in the file
    """
    cwd = get_path()
    with open(cwd+'/client_config/'+filename+'.json', 'r') as file:
        data = json.load(file)
    return data

def write_json(data, filename):
    """
    A function use to write data to a json file

    Params:
     - data (dict) : The data to write to the file
     - filename (string) : The name of the file to write to
    """
    cwd = get_path()
    with open(cwd+'/client_config/'+filename+'.json', 'w') as file:
        json.dump(data, file, indent=4)
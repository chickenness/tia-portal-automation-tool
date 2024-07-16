from .modules import objects
from pathlib import Path
import json

class PPError(Exception):
    pass

def parse(path: str) -> objects.Config:
    """
    Initialize TIA Portal config parser with the path to the configuration file
    Loads and process the JSON configuration file into python classes.

    :param path: String path to the JSON configuration file
    """

    config_file_path: Path = Path(path)
    
    if not config_file_path.exists():
        raise PPError(f"JSON config file does not exist: {config_file_path}")

    if not config_file_path.is_file():
        raise PPError(f"JSON config is not a file: {config_file_path}")

    with open(config_file_path, 'r') as file:
        conf: dict = json.load(file)

    parsed = objects.start(**conf)

    print(parsed, type(parsed))

    return parsed

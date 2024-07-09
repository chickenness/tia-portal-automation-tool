import json
from abc import ABC
from pathlib import Path


"""
TODO:
    - [X] load config
    - [X] tia portal dll
        - [X] version
        - [X] dll
        - [X] path
    - [X] default values
    - [ ] class for the json?
    - [ ] project (at least one)
        - [ ] name
        - [ ] path
        - [ ] devices (at least one)
            - [ ] name
            - [ ] article number
            - [ ] version
    - [ ] Error Handling
    - [ ] Logging?
"""

class PPError(Exception):
    pass


class Config(ABC):


    def print(self, level: int = 0) -> None:
        for key, value in vars(self).items():
            if isinstance(value, Config):
                print(f"{key} = ")
                value.print(level+1)
            else:
                print(f"{'\t'*level}{key} = {value}")


    def process(self, config: dict) -> None:
        """
        Set the config values based on the JSON config file

        :param config: Dictionary values of the JSON configuration
        """

        for key, value in vars(self).items():
            if key in config:
                setattr(self, key, config[key])



class Device:

    def __init__(self) -> None:
        self.name: str = ""
        self.article_number: str = ""
        self.version: str = ""

class Project(Config):

    def __init__(self) -> None:
        self.name: str = ""
        self.directory: Path | None = None
        self.devices: list = []


class TIA(Config):

    def __init__(self) -> None:
        self.version: int = 18
        self.filename: str = "Siemens.Engineering.dll"
        self.dll: Path = Path(rf"C:/Program Files/Siemens/Automation/Portal V{self.version}/PublicAPI/V{self.version}/{self.filename}")
        self.project: Project | None = None

    def process(self, config: dict) -> None:
        super().process(config)

        if isinstance(self.project, dict):
            conf = self.project.copy()
            self.project = Project()
            self.project.process(conf)
        else:
            self.project = None



class PortalParser:
    """
    A class to parse TIA Portal JSON configuration file.
    """
    
    def __init__(self, config_file_path: Path) -> None:
        """
        Initialize TIA Portal config parser with the path to the configuration file

        :param config_file_path: Path to the JSON configuration file
        """
        
        self.config_file_path: Path = config_file_path
        self.config: Config | None = None
    
    def load(self) -> None:
        """
        Loads and process the JSON configuration file into python classes.
        """

        if not isinstance(self.config_file_path, Path):
            raise PPError(f"JSON config file is not a valid path.")

        if not self.config_file_path.exists():
            raise PPError(f"JSON config file does not exist: {self.config_file_path}")

        if not self.config_file_path.is_file():
            raise PPError(f"JSON config is not a file: {self.config_file_path}")

        with open(self.config_file_path, 'r') as file:
            conf = json.load(file)

        self.config = TIA()
        self.config.process(conf)
        self.config.print()




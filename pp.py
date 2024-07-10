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
    - [X] class for the json?
    - [x] project (at least one)
        - [x] name
        - [x] path
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

    def __init__(self, **config: dict) -> None:
        """
        Set the config values based on the JSON config file.
        This will call the function in each classes.

        :param config: Dictionary values of the JSON configuration
        """

        for key, value in config.items():
            func = f"fn_{key}"
            if hasattr(self, func):
                getattr(self, func)(value)

    def print(self, level: int = 0) -> None:
        for key, value in vars(self).items():
            if isinstance(value, Config):
                print(f"{key} = ")
                value.print(level+1)
            else:
                print(f"{'\t'*level}{key} = {value}")





class Device(Config):

    def __init__(self, **config: dict) -> None:
        self.device_name: str = ""
        self.article_number: str = ""
        self.version: str = ""

        super().__init__(**config)

    def fn_device_name(self, value):
        self.device_name = value

    def fn_article_number(self, value):
        self.article_number = value

    def fn_version(self, value):
        self.version = value


class Project(Config):

    def __init__(self, **config: dict) -> None:
        self.name: str              = "AutomationProject420"
        self.directory: Path        = Path.home()
        self.devices: list[Device]  = []

        super().__init__(**config)

    def fn_name(self, value) -> None:
        self.name = value

    def fn_directory(self, value) -> None:
        self.directory = value

    def fn_devices(self, devices) -> None:
        for _, value in devices.items():
            device = Device(**value)
            self.devices.append(device)




class TIA(Config):

    def __init__(self, **config: dict) -> None:
        self.version: int               = 18
        self.filename: str              = "Siemens.Engineering.dll"
        self.dll: Path                  = Path(rf"C:/Program Files/Siemens/Automation/Portal V{self.version}/PublicAPI/V{self.version}/{self.filename}")
        self.project: Project | None    = None
        
        super().__init__(**config)

    def fn_version(self, value) -> None:
        if not value.isnumeric():
            raise PPError("Not a valid integer.")

        self.version = int(value)

    def fn_filename(self, value) -> None:
        self.filename = value

    def fn_dll(self, value) -> None:
        self.dll = Path(value)

    def fn_project(self, value) -> None:
        if not isinstance(value, dict):
            raise PPError("Invalid Project")

        self.project = Project(**value)


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

        self.config = TIA(**conf)
        # self.config.process(conf)
        self.config.print()




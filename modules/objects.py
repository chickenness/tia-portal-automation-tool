from abc import ABC
from pathlib import Path

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

    def __repr__(self) -> str:
        text = ""
        for key, value in vars(self).items():
            text += '\n'
            text += f"{key} = {value}"

        return text


    def print(self, level: int = 0) -> None:
        for key, value in vars(self).items():
            if isinstance(value, Config):
                print(f"{key} = ")
                value.print(level+1)
            else:
                print(f"{'\t'*level}{key} = {value}")





class Device(Config):

    def __init__(self, **config: dict) -> None:
        self.device_name: str       = "PLCDev_1"
        self.article_number: str    = "OrderNumber:6ES7 513-1AL02-0AB0"
        self.version: str           = "2.6"

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
        self.directory = Path(value)

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

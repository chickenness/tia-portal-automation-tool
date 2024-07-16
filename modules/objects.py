from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class Config:
    pass


@dataclass
class Device(Config):
    device_name: str        = "PLCDev_1"
    article_number: str     = "OrderNumber:6ES7 513-1AL02-0AB0"
    version: str            = "2.6"
    device: str             = field(init=False)

    def __post_init__(self):
        self.device = f"{self.article_number}/V{self.version}"

@dataclass
class Project(Config):
    name: str               = "AutomationProject420"
    directory: Path         = Path.home()
    devices: list[Device]   = field(default_factory=list)

@dataclass
class TIA(Config):
    version: int            = 18
    filename: str           = "Siemens.Engineering.dll"
    dll: Path               = field(init=False)
    project: Config         = field(default_factory=Project)

    def __post_init__(self):
        self.dll = Path(rf"C:/Program Files/Siemens/Automation/Portal V{self.version}/PublicAPI/V{self.version}/{self.filename}")



def parse_device(**config: dict[str, Any]) -> Device | ValueError:
    conf = Device()
    keys = config.keys()

    if 'device_name' in keys:
        value = interpret_string(config['device_name'])
        if isinstance(value, ValueError):
            return value
        conf.device_name = value
    if 'article_number' in keys:
        value = interpret_string(config['article_number'])
        if isinstance(value, ValueError):
            return value
        conf.device_name = value
    if 'version' in keys:
        value = interpret_string(config['version'])
        if isinstance(value, ValueError):
            return value
        conf.version = value

    return conf

def parse_project(**config: dict[str, Any]) -> Project | ValueError:
    conf = Project()
    keys = config.keys()

    if 'name' in keys:
        value = interpret_string(config['name'])
        if isinstance(value, ValueError):
            return value
        conf.name = value
    if 'directory' in keys:
        value = interpret_path(config['directory'])
        if isinstance(value, ValueError):
            return value
        conf.directory = value
    if 'devices' in keys:
        conf.devices = []
        for _, dev in config['devices'].items():
            value = interpret_device(dev)
            if isinstance(value, ValueError):
                return value
            conf.devices.append(value)


    return conf


def parse_tia(**config: dict[str, Any]) -> TIA | ValueError:
    conf = TIA()
    keys = config.keys()

    if 'version' in keys:
        value = interpret_number(config['version'])
        if isinstance(value, ValueError):
            return value
        conf.version = value
    if 'filename' in keys:
        value = interpret_string(config['filename'])
        if isinstance(value, ValueError):
            return value
        conf.filename = value
    if 'dll' in keys:
        value = interpret_path(config['dll'])
        if isinstance(value, ValueError):
            return value
        conf.dll = value
    if 'project' in keys:
        value = interpret_project(config['project'])
        if isinstance(value, ValueError):
            return value
        conf.project = value


    return conf
    
def interpret_number(value: Any) -> int | ValueError:
        if isinstance(value, int):
            return value

        if not isinstance(value, str) or not value.isnumeric():
            return ValueError(f"Not a valid number: {value}")

        return int(value)

def interpret_string(value: Any) -> str | ValueError:
        if not isinstance(value, str):
            return ValueError(f"Not a valid string: {value}")

        return value

def interpret_path(value: Any) -> Path | ValueError:
    if not isinstance(value, str):
        return ValueError(f"Not a valid string path: {value}")

    return Path(value)

def interpret_project(value: Any) -> Project | ValueError:
    if not isinstance(value, dict):
        return ValueError(f"Invalid project: {value}")
    
    return parse_project(**value)

def interpret_device(value: Any) -> Device | ValueError:
    if not isinstance(value, dict):
        return ValueError(f"Invalid device: {value}")
    
    return parse_device(**value)


def start(**config: dict) -> Config | ValueError:

    conf: Config | ValueError = parse_tia(**config)

    return conf



# class Config(ABC):
#
#     def __init__(self, **config: dict) -> None:
#         """
#         Set the config values based on the JSON config file.
#         This will call the function in each classes.
#
#         :param config: Dictionary values of the JSON configuration
#         """
#
#         for key, value in config.items():
#             func = f"fn_{key}"
#             if hasattr(self, func):
#                 getattr(self, func)(value)
#
#     def __repr__(self) -> str:
#         text = ""
#         for key, value in vars(self).items():
#             text += '\n'
#             text += f"{key} = {value}"
#
#         return text
#
#
#     def print(self, level: int = 0) -> None:
#         for key, value in vars(self).items():
#             if isinstance(value, Config):
#                 print(f"{key} = ")
#                 value.print(level+1)
#             else:
#                 print(f"{'\t'*level}{key} = {value}")
#
#
#
#
#
# class Device(Config):
#
#     def __init__(self, **config: dict) -> None:
#         self.device_name: str       = "PLCDev_1"
#         self.article_number: str    = "OrderNumber:6ES7 513-1AL02-0AB0"
#         self.version: str           = "2.6"
#
#         super().__init__(**config)
#
#     def fn_device_name(self, value):
#         self.device_name = value
#
#     def fn_article_number(self, value):
#         self.article_number = value
#
#     def fn_version(self, value):
#         self.version = value
#
#
#
# class Project(Config):
#
#     def __init__(self, **config: dict) -> None:
#         self.name: str              = "AutomationProject420"
#         self.directory: Path        = Path.home()
#         self.devices: list[Device]  = []
#
#         super().__init__(**config)
#
#     def fn_name(self, value) -> None:
#         self.name = value
#
#     def fn_directory(self, value) -> None:
#         self.directory = Path(value)
#
#     def fn_devices(self, devices) -> None:
#         for _, value in devices.items():
#             device = Device(**value)
#             self.devices.append(device)
#
#
#
#
# class TIA(Config):
#
#     def __init__(self, **config: dict) -> None:
#         self.version: int               = 18
#         self.filename: str              = "Siemens.Engineering.dll"
#         self.dll: Path                  = Path(rf"C:/Program Files/Siemens/Automation/Portal V{self.version}/PublicAPI/V{self.version}/{self.filename}")
#         self.project: Project | None    = None
#         
#         
#         super().__init__(**config)
#
#     def fn_version(self, value) -> None:
#         if not value.isnumeric():
#             raise PPError("Not a valid integer.")
#
#         self.version = int(value)
#
#     def fn_filename(self, value) -> None:
#         self.filename = value
#
#     def fn_dll(self, value) -> None:
#         self.dll = Path(value)
#
#     def fn_project(self, value) -> None:
#         if not isinstance(value, dict):
#             raise PPError("Invalid Project")
#
#         self.project = Project(**value)

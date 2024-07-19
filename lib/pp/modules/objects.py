from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class Config:
    """
    The keys are based on https://cache.industry.siemens.com/dl/files/163/109477163/att_926042/v1/TIAPortalOpennessenUS_en-US.pdf
    """
    pass


@dataclass
class Device(Config):
    """
    Found on 7.15.3 around page 213
    """

    DeviceItemTypeId: str   = "OrderNumber:6ES7 510-1DJ01-0AB0/V2.0"
    DeviceTypeId: str       = "PLC_1"
    DeviceItemName: str     = "NewDevice"
    DeviceName: str         = ""

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
    enable_ui: bool         = True
    project: Config         = field(default_factory=Project)

    def __post_init__(self):
        self.dll = Path(rf"C:/Program Files/Siemens/Automation/Portal V{self.version}/PublicAPI/V{self.version}/{self.filename}")


def process_config(config: Config, **data: dict[str, Any]) -> Config:
    """
    I created this function so that there's no need to type in the individual key names.
    Tends to get annoying to rename them or add a new key to be parsed.

    1. Check the variables of the class 'config'
    2. Check the keys of the dictionary 'data'
    3. Iterate only the keys that's in the class
    4. Check the type of the key-variable and perform operation for it
    5. Set the value of the config class variable based on the previous step result
    """
    
    variables = vars(config).keys()
    for key, value in data.items():
        if not key in variables:
            continue

        config_var = getattr(config, key)

        if isinstance(config_var, bool):
            result = interpret_bool(value)
            setattr(config, key, result)
        if isinstance(config_var, int):
            result = interpret_number(value)
            setattr(config, key, result)
        if isinstance(config_var, str):
            result = interpret_string(value)
            setattr(config, key, result)
        if isinstance(config_var, Path):
            result = interpret_path(value)
            setattr(config, key, result)

    return config



def parse_device(**data: dict[str, Any]) -> Device:
    conf = process_config(Device(), **data)
    keys = data.keys()

    return conf

def parse_project(**data: dict[str, Any]) -> Project:
    conf = process_config(Project(), **data)
    keys = data.keys()

    if 'devices' in keys:
        conf.devices = []
        for _, dev in data['devices'].items():
            value = interpret_device(dev)
            conf.devices.append(value)

    return conf


def parse_tia(**data: dict[str, Any]) -> TIA:
    conf = process_config(TIA(), **data)
    keys = data.keys()

    if 'project' in keys:
        value = interpret_project(data['project'])
        conf.project = value
    conf.__post_init__()

    return conf


def interpret_bool(value: Any) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"Not a boolean logic: {value}")
    
    return value

    
def interpret_number(value: Any) -> int:
        if isinstance(value, int):
            return value

        if not isinstance(value, str) or not value.isnumeric():
            raise ValueError(f"Not a valid number: {value}")

        return int(value)

def interpret_string(value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError(f"Not a valid string: {value}")
        if not value:
            return None

        return value

def interpret_path(value: Any) -> Path:
    if not isinstance(value, str):
        raise ValueError(f"Not a valid string path: {value}")

    return Path(value)

def interpret_project(value: Any) -> Project:
    if not isinstance(value, dict):
        raise ValueError(f"Invalid project: {value}")
    
    return parse_project(**value)

def interpret_device(value: Any) -> Device:
    if not isinstance(value, dict):
        raise ValueError(f"Invalid device: {value}")
    
    return parse_device(**value)


def start(**config: dict) -> Config:

    conf: Config = parse_tia(**config)

    return conf

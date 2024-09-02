from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class Config:
    """
    The keys are based on https://cache.industry.siemens.com/dl/files/886/109826886/att_1163875/v1/TIAPortalOpenness_enUS_en-US.pdf.
    Adding the key and its type annotation along with its default value should be enough.
    If the said key is another json object, create a new child class Config for it then its functions as well: interpret_class and parse_class.
    """
    pass


@dataclass
class Tag(Config):
    tag_name: str                           = ""
    data_type: str                          = ""
    logical_address: str                    = ""

@dataclass
class TagTable(Config):
    name: str                               = ""
    tags: list[Tag]                         = field(default_factory=list)

@dataclass
class DeviceItem(Config):
    """
    Found on 7.16.2 around p. 223

    |-----------------|----------|--------------------------------------------|
    | Name            | Type     | Description                                |
    |-----------------|----------|--------------------------------------------|
    | typeIdentifier  | string   | type identifier of the created device item |
    | name            | string   | name of created device item                |
    | positionNumber  | int      | position number of the created device item |
    |-----------------|----------|--------------------------------------------|
    """

    TypeIdentifier: str                     = "OrderNumber:6ES7 521-1BL00-0AB0/V2.1"
    Name: str                               = "IO1"
    PositionNumber: int                     = 0

@dataclass
class Device(Config):
    """
    Found on 7.15.3 around page 213

    |--------------------|--------|--------------------------------------------|
    | Name               | Type   | Description                                |
    |--------------------|--------|--------------------------------------------|
    | DeviceItemTypeId   | string | Type identifier of the device item         |
    | DeviceTypeId       | string | Type identifier of the device              |
    | DeviceItemName     | string | Name of the created device item            |
    | DeviceName         | string | Name of the created device                 |
    |--------------------|--------|--------------------------------------------|
    """

    DeviceItemTypeId: str                   = "OrderNumber:6ES7 510-1DJ01-0AB0/V2.0"
    DeviceTypeId: str                       = "PLC_1"
    DeviceItemName: str                     = "NewDevice"
    DeviceName: str                         = ""
    items: list[DeviceItem]                 = field(default_factory=list)
    slots_required: int                     = 2
    network_address: str                    = "192.168.0.112"
    tag_table: TagTable                     = field(default_factory=TagTable)

@dataclass
class Network(Config):
    address: str                            = "192.168.0.112"
    subnet_name: str                        = "Profinet"
    io_controller: str                      = "PNIO"

@dataclass
class MasterCopy(Config):
    block_type: str                         = ""
    source: str                             = ""
    destination: str                        = ""
    name: str                               = ""
    is_mastercopy: bool                     = True

@dataclass
class Instance(Config):
    block_type: str                         = ""
    name: str                               = ""
    programming_language: str               = ""
    number: int                             = 0
    xml_path: Path                          = Path().home()
    networks: dict[int, list[MasterCopy]]   = field(default_factory=dict)

@dataclass
class Library(Config):
    path: Path                              = Path()
    read_only: bool                         = True
    master_copies: list[MasterCopy]         = field(default_factory=list)
    instances: list[Instance]               = field(default_factory=list)

@dataclass
class Project(Config):
<<<<<<< HEAD
    name: str                               = "AutomationProject420"
    directory: Path                         = Path.home()
    overwrite: bool                         = False
    devices: list[Device]                   = field(default_factory=list)
    networks: list[Network]                 = field(default_factory=list)
    libraries: list[Library]                = field(default_factory=list)
=======
    name: str                           = "AutomationProject420"
    directory: Path                     = Path.home()
    overwrite: bool                     = False
    devices: list[Device]               = field(default_factory=list)
    networks: list[Network]             = field(default_factory=list)
    libraries: list[Library]            = field(default_factory=list)
>>>>>>> 1a68340 (UPDATE: Allow project overwriting for #7)

@dataclass
class TIA(Config):
    version: int                            = 18
    filename: str                           = "Siemens.Engineering.dll"
    dll: Path                               = field(init=False)
    enable_ui: bool                         = True
    project: Config                         = field(default_factory=Project)

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

def parse_device_item(**data: dict[str, Any]) -> DeviceItem:
    conf = process_config(DeviceItem(), **data)

    return conf


def parse_network(**data: dict[str, Any]) -> Network:
    conf = process_config(Network(), **data)

    return conf

def parse_library(**data: dict[str, Any]) -> Library:
    conf = process_config(Library(), **data)
    keys=  data.keys()

    if 'master_copies' in keys:
        for master_copy in data['master_copies']:
            value = interpret_master_copy(master_copy)
            conf.master_copies.append(value)

    if 'instances' in keys:
        for master_copy in data['instances']:
            value = interpret_instance(master_copy)
            conf.instances.append(value)

    return conf

def parse_master_copy(**data: dict[str, Any]) -> MasterCopy:
    conf = process_config(MasterCopy(), **data)

    return conf

def parse_instance(**data: dict[str, Any]) -> Instance:
    conf = process_config(Instance(), **data)
    keys = data.keys()

    if 'networks' in keys:
        for id, instances in data['networks'].items():
            key = int(id)
            value: list[MasterCopy] = []
            for master_copy in instances:
                result = interpret_master_copy(master_copy)
                value.append(result)

            conf.networks[key] = value

    return conf

def parse_tag_table(**data: dict[str, Any]) -> TagTable:
    conf = process_config(TagTable(), **data)
    keys = data.keys()

    if 'tags' in keys:
        for tag in data['tags']:
            value = interpret_tag(tag)
            conf.tags.append(value)

    return conf

def parse_tag(**data: dict[str, Any]) -> Tag:
    conf = process_config(Tag(), **data)

    return conf

def parse_device(**data: dict[str, Any]) -> Device:
    conf = process_config(Device(), **data)
    keys = data.keys()

    if 'items' in keys:
        for item in data['items']:
            value = interpret_device_item(item)
            conf.items.append(value)
    if 'tag_table' in keys:
        value = interpret_tag_table(data['tag_table'])
        conf.tag_table = value

    return conf

def parse_project(**data: dict[str, Any]) -> Project:
    conf = process_config(Project(), **data)
    keys = data.keys()

    if 'devices' in keys:
        for dev in data['devices']:
            value = interpret_device(dev)
            conf.devices.append(value)

    if 'networks' in keys:
        for network in data['networks']:
            value = interpret_network(network)
            conf.networks.append(value)

    if 'libraries' in keys:
        for library in data['libraries']:
            value = interpret_library(library)
            conf.libraries.append(value)

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

def interpret_string(value: Any) -> str | None:
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

def interpret_network(value: Any) -> Network:
    if not isinstance(value, dict):
        raise ValueError(f"Invalid network configuration: {value}")

    return parse_network(**value)

def interpret_library(value: Any) -> Library:
    if not isinstance(value, dict):
        raise ValueError(f"Invalid library configuration: {value}")

    return parse_library(**value)

def interpret_master_copy(value: Any) -> MasterCopy:
    if not isinstance(value, dict):
        raise ValueError(f"Invalid MasterCopy configuration: {value}")

    return parse_master_copy(**value)

def interpret_instance(value: Any) -> Instance:
    if not isinstance(value, dict):
        raise ValueError(f"Invalid MasterCopy Instance configuration: {value}")

    return parse_instance(**value)

def interpret_device_item(value: Any) -> DeviceItem:
    if not isinstance(value, dict):
        raise ValueError(f"Invalid device item: {value}")
    
    return parse_device_item(**value)

def interpret_tag_table(value: Any) -> TagTable:
    if not isinstance(value, dict):
        raise ValueError(f"Invalid Tag Table value: {value}")

    return parse_tag_table(**value)

def interpret_tag(value: Any) -> Tag:
    if not isinstance(value, dict):
        raise ValueError(f"Invalid Tag Table value: {value}")

    return parse_tag(**value)


def start(**config: dict) -> Config:

    conf: Config = parse_tia(**config)

    return conf

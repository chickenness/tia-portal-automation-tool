from enum import Enum, auto
import json
from pathlib import Path

class Source(Enum):
    CONFIG = auto()
    MASTERCOPY = auto()
    PLC = auto()

class Plc(Enum):
    OB = auto()
    FB = auto()
    FC = auto()
    DB = auto()



SOURCE = {
    "type": dict,
    "default": {},
    "schema": {
        "from" : {"type": Source, "default": Source.MASTERCOPY},
        "name" : {"type": str, "default": ""},
    }
}

NETWORK_CALLS = {
    "type": list,
    "default": [],
    "item_schema": {
    }
}

BLOCK = {
    "type": dict,
    "default": {},
    "schema": {
        "enum" : {"type": Plc, "default": Plc.OB},
        "name" : {"type": str, "default": "Block_1"},
        "number" : {"type": int, "default": 0},
        "programming_language" : {"type": str, "default": "LAD"},
        "source" : SOURCE,
        "network_calls": PROGRAM_BLOCK,
    }
}

# Only allows single InstanceDB
ORGANIZATION_BLOCK = {
    **BLOCK,

}

# Allows all InstanceDB types
FUNCTION_BLOCK = {
    **BLOCK,
}

# Only allows single and Parameter InstanceDB
FUNCTION = {
    **BLOCK,
}

PROGRAM_BLOCK = {
    "type": list,
    "default": [],
    "enum": Plc,
    "unique_item_schema": {
        Plc.OB: ORGANIZATION_BLOCK,
        Plc.FB: FUNCTION_BLOCK,
        Plc.FC: FUNCTION,
    }
}

TAG = {
    "type": list,
    "default": [],
    "item_schema": {
        "Name": {"type": str, "default": ""},
        "DataTypeName": {"type": str, "default": ""},
        "LogicalAddress": {"type": str, "default": ""}
    }
}

TAG_TABLE = {
    "type": dict,
    "default": {},
    "schema": {
        "Name": {"type": str, "default": ""},
        "Tags": TAG, 
        }
}

LOCAL_MODULE = {
    "type": list,
    "default": [],
    "item_schema": {
        "TypeIdentifier": {"type": str, "default": ""},
        "Name": {"type": str, "default": ""},
        "PositionNumber": {"type": int, "default": 0}
    }
}

DEVICE = {
    "type": list,
    "default": [],
    "item_schema": {
        "network_address": {"type": str, "default": "192.168.0.112"},
        "slots_required": {"type": int, "default": 2},
        "p_name": {"type": str, "default": "PLC_1"},
        "p_typeIdentifier": {"type": str, "default": "OrderNumber:6ES7 510-1DJ01-0AB0/V2.0"},
        "p_deviceName": {"type": str, "default": "NewPlcDevice"},
        "Program blocks": PROGRAM_BLOCK,
        "PLC tags": TAG_TABLE,
        "Local modules": LOCAL_MODULE,
    }
}

NETWORK = {
    "type": list,
    "default": [],
    "item_schema": {
        "address": {"type": str, "default": "192.168.0.112"},
        "subnet_name": {"type": str, "default": "Profinet"},
        "io_controller": {"type": str, "default": "PNIO"}
    }
}

LIBRARY = {
    "type": list,
    "default": [],
    "item_schema": {
        "path": {"type": Path, "default": Path()},
        "read_only": {"type": bool, "default": True},
    }
}


PROJECT = {
    "type": dict,
    "default": {},
    "schema": {
        "name": {"type": str, "default": "AwesomeTIA420"},
        "directory": {"type": Path, "default": Path.home()},
        "overwrite": {"type": bool, "default": False},
        "devices": DEVICE,
        "networks": NETWORK,
        "libraries": LIBRARY,
        }
    }

SCHEMA = {
    "dll": {"type": Path, "default": Path(r'"C:/Program Files/Siemens/Automation/Portal V18/PublicAPI/V18/Siemens.Engineering.dll')},
    "enable_ui": {"type": bool, "default": True},
    "project": PROJECT,
}





def clean_config(config, schema):
    cleaned_config = {}
    
    for key, expected_type in schema.items():
        value = config.get(key, expected_type['default'])
        
        if value is None:
            cleaned_config[key] = expected_type['default']
            continue
        
        if isinstance(value, expected_type['type']):
            if expected_type['type'] == dict:
                cleaned_config[key] = clean_config(value, expected_type['schema'])
            elif expected_type['type'] == list:
                if expected_type.get('item_schema'):
                    cleaned_config[key] = [
                        clean_config(item, expected_type['item_schema']) if isinstance(item, dict) else item
                        for item in value
                    ]
                elif expected_type.get('unique_item_schema'):
                    cleaned_config[key] = [
                        clean_config(item, expected_type['unique_item_schema'][expected_type.get('enum')[item['enum']]]['schema']) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    cleaned_config[key] = value  # Accept as-is if no item_schema
            elif expected_type['type'] == Path:
                cleaned_config[key] = Path(value)
            else:
                cleaned_config[key] = value
        elif expected_type['type'] == bool and isinstance(value, str):
            cleaned_config[key] = value.lower() in ['true', '1']
        elif expected_type['type'] == list and isinstance(value, str):
            cleaned_config[key] = value.split(',')
        elif expected_type['type'] == dict and isinstance(value, str):
            cleaned_config[key] = json.loads(value)
        elif expected_type['type'] == Path and isinstance(value, str):
            cleaned_config[key] = Path(value)
        elif expected_type['type'] == Plc and isinstance(value, str):
            cleaned_config[key] = Plc[value]
        elif expected_type['type'] == Source and isinstance(value, str):
            cleaned_config[key] = Source[value]
        else:
            cleaned_config[key] = expected_type['default']

    return cleaned_config


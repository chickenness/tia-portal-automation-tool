from enum import Enum, auto
import json
import jsonschema
from jsonschema import validate, Draft7Validator
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
        # "network_calls": PROGRAM_BLOCK,
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
    "dll": {"type": Path, "default": Path(r'C:/Program Files/Siemens/Automation/Portal V18/PublicAPI/V18/Siemens.Engineering.dll')},
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


BLOCK = {
    "type": "object",
    "required": ["enum", "name", "source"],
    "properties": {
        "enum" : {"type": "string", "default": "OB"},
        "name" : {"type": "string", "default": "Block_1"},
        "number" : {"type": "integer", "default": 0},
        "programming_language" : {"type": "string", "default": "LAD"},
        "source" : {"type": "string", "default": "MASTERCOPY"},
        "network_calls": {"$ref": "#/$defs/blocks"}, 
    }
}

PROGRAM_BLOCK = {
    "type": "object",
    "required": [],
    "properties": { "blocks": {"$ref": "#/$defs/blocks"}, }
}

TAG = {
    "type": "object",
    "required": ["Name", "DataTypeName", "LogicalAddress"],
    "properties": {
        "Name": {"type": "string", "default": ""},
        "DataTypeName": {"type": "string", "default": ""},
        "LogicalAddress": {"type": "string", "default": ""}
    }
}

TAG_TABLE = {
    "type": "object",
    "required": ["Name"],
    "properties": {
        "Name": {"type": "string", "default": ""},
        "Tags":{"type": "array", "items": TAG, "default": []},
        }
}

LOCAL_MODULE = {
    "type": "object",
    "required": [],
    "properties": {
        "TypeIdentifier": {"type": "string", "default": ""},
        "Name": {"type": "string", "default": ""},
        "PositionNumber": {"type": "integer", "default": 0}
    }
}

DEVICE = {
    "type": "object",
    "required": ["p_name", "p_typeIdentifier", "p_deviceName"],
    "properties": {
        "network_address": {"type": "string", "default": "192.168.0.112", "format": "ipv4"},
        "slots_required": {"type": "integer", "default": 2},
        "p_name": {"type": "string", "default": "PLC_1"},
        "p_typeIdentifier": {"type": "string", "default": "OrderNumber:6ES7 510-1DJ01-0AB0/V2.0"},
        "p_deviceName": {"type": "string", "default": "NewPlcDevice"},
        "Program blocks":{"type": "array", "items": PROGRAM_BLOCK, "default": []},
        "PLC tags":{"type": "array", "items": TAG_TABLE, "default": []},
        "Local modules":{"type": "array", "items": LOCAL_MODULE, "default": []},
    }
}

NETWORK = {
    "type": "object",
    "required": ["address", "subnet_name", "io_controller"],
    "properties": {
        "address": {"type": "string", "default": "192.168.0.112", "format": "ipv4"},
        "subnet_name": {"type": "string", "default": "Profinet"},
        "io_controller": {"type": "string", "default": "PNIO"}
    }
}

LIBRARY = {
    "type": "object",
    "required": ["path", "read_only"],
    "properties": {
        "path": {"type": "string", "default": f"{Path()}", "format": "path"},
        "read_only": {"type": "boolean", "default": True},
    }
}

PROJECT = {
    "type": "object",
    "required": ["name", "directory"],
    "properties": {
        "name": {"type": "string", "default": "AwesomeTIA420"},
        "directory": {"type": "string", "default": f"{Path.home()}", "format": "path"},
        "overwrite": {"type": "boolean", "default": False},
        "devices":{"type": "array", "items": DEVICE, "default": []},
        "networks":{"type": "array", "items": NETWORK, "default": []},
        "libraries": {"type": "array", "items": LIBRARY, "default": []},
    }
}

SCHEMA = {
    "type": "object",
    "required": ["dll", "enable_ui", "project"],
    "$defs": {
        "blocks":{
            "type": "array",
            "items": {
                "anyOf": [
                    BLOCK,
                ]
            },
            "default": []},
    },
    "properties": {
        "dll": {
            "type": "string",
            "default": r"C:/Program Files/Siemens/Automation/Portal V18/PublicAPI/V18/Siemens.Engineering.dll",
            "format": "path"
        },
        "enable_ui": { "type": "boolean", "default": True },
        "project": PROJECT,
    }
}

def validate_path(validator, path, instance, schema):
    if not isinstance(instance, str):
        yield jsonschema.ValidationError(f"{instance} is not a string.")

validator = Draft7Validator(SCHEMA)
validator.VALIDATORS["path"] = validate_path

from enum import Enum
from jsonschema import Draft202012Validator, validators, Draft7Validator, ValidationError
from pathlib import Path
from typing import Any

class Source(Enum):
    NONE = "NONE"
    MASTERCOPY = "MASTERCOPY"
    PLC = "PLC"

class Plc(Enum):
    OB = "OB"
    FB = "FB"
    FC = "FC"
    DB = "DB"


SOURCE = {
    "type": "object",
    "required": [],
    "properties": {
        "from" : {"type": "string", "default": "MASTERCOPY"},
        "name" : {"type": "string", "default": ""},
    }
}


BLOCK = {
    "type": "object",
    "required": ["enum", "name", "source"],
    "properties": {
        "enum" : {"type": "string", "default": "OB"},
        "name" : {"type": "string", "default": "Block_1"},
        "number" : {"type": "integer", "default": 0},
        "programming_language" : {"type": "string", "default": "LAD"},
        "source" : SOURCE,
        # "network_calls": {"$ref": "#/$defs/blocks"}, 

    },
}

TAG = {
    "type": "object",
    "required": ["Name", "DataTypeName"],
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
    "required": ['TypeIdentifier', 'Name', 'PositionNumber'],
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
        "Program blocks": {"type": "array", "items": BLOCK, "default": []},
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
        "path": {"type": "path", "default": ""},
        "read_only": {"type": "boolean", "default": True},
    }
}

PROJECT = {
    "type": "object",
    "required": ["name"],
"properties": {
        "name": {"type": "string", "default": "AwesomeTIA420"},
        "directory": {"type": "path", "default": f"{Path.home()}"},
        "overwrite": {"type": "boolean", "default": False},
        "devices":{"type": "array", "items": DEVICE, "default": []},
        "networks":{"type": "array", "items": NETWORK, "default": []},
        "libraries": {"type": "array", "items": LIBRARY, "default": []},
    }
}

SCHEMA = {
    "type": "object",
    "required": ["project"],
    "$defs": {
        "blocks":{ "type": "array", "items": BLOCK, "default": [] },
    },
    "properties": {
        "dll": {
            "type": "path",
            "default": r"C:/Program Files/Siemens/Automation/Portal V18/PublicAPI/V18/Siemens.Engineering.dll",
        },
        "enable_ui": { "type": "boolean", "default": True },
        "project": PROJECT,
    }
}

def is_pathlib(checker, instance):
    instance = Path(instance)
    return (isinstance(instance, Path))



ExtendedValidator = validators.extend(
    Draft202012Validator,
    type_checker= Draft202012Validator.TYPE_CHECKER.redefine('path', is_pathlib,)
)

def apply_defaults_and_filter(config: dict, schema: dict) -> dict[str, Any]:
    filtered_config: dict[str, Any] = {}

    for key, value in schema['properties'].items():
        if key in config:
            filtered_config[key] = config[key]
        else:
            filtered_config[key] = value.get('default')

        if isinstance(filtered_config[key], dict):
            filtered_config[key] = apply_defaults_and_filter(filtered_config[key], schema['properties'][key])

        if isinstance(filtered_config[key], list):
            filtered_config[key] = []
            item_schema = value['items']
            for item in config.get(key, []):
                filtered_config[key].append(apply_defaults_and_filter(item, item_schema))

    return filtered_config

def clean_config(config: dict, schema: dict) -> dict[str, Any]:
    try:
        validator = ExtendedValidator( schema=schema)
        validator.validate(instance=config)
    except ValidationError as e:
        return {"error": f"Validation error: {e.message}"}
    else:
        return apply_defaults_and_filter(config, schema)



from schema import Schema, And, Or, Use, Optional, SchemaError

schema_None = None

schema_program_block = {
    "name": str,
    Optional("number", default=0): int,
    Optional("programming_language", default="LAD"): And(str, Use(str.upper)),
    Optional("source", default={"from": Source.NONE}): {
        "from": And(str, Use(Source)),
        Optional("name"): str,
    },
    Optional("network_calls", default=[]): And(list),
}

schema_plc_tag = {
        "Name": str,
        "DataTypeName": str,
        "LogicalAddress": str,
    }

schema_plc_tag_table = {
        "Name": str,
        Optional("Tags", default=[]): And(list, [schema_plc_tag]),
    }

schema_module = {
        "TypeIdentifier": str,
        "Name": str,
        "PositionNumber": int,
    }

schema_device = {
    "p_name": str, # PLC1
    "p_typeIdentifier": str, # OrderNumber:6ES7 510-1DJ01-0AB0/V2.0
    Optional("network_address", default="192.168.0.112"): str,
}

schema_device_plc = {
        **schema_device,
        "p_deviceName": str, # NewPlcDevice
        Optional("slots_required", default=2): int,
        Optional("Program blocks", default=[]): And(list, [schema_program_block]),
        Optional("PLC tags", default=[]): And(list, [schema_plc_tag_table]),
        Optional("Local modules", default=[]): And(list, [schema_module]),
    }


schema_device_ionode = {
        **schema_device,
        "p_deviceName": str, # NewPlcDevice
        Optional("slots_required", default=2): int,
        Optional("Modules", default=[]): And(list, [schema_module]),
    }


schema_device_hmi = {
        **schema_device,
        Optional("HMI tags", default=[]): And(list, [schema_plc_tag_table]),
    }

schema_network = {
        "address": str, # 192.168.0.112
        "subnet_name": str, # Profinet
        "io_controller": str, # PNIO
    }


schema_library = {
    "path": And(str, Use(Path), lambda p: Path(p)),
    Optional("read_only", default=True): bool,
    }

schema = Schema(
    {
        Optional("dll", default=Path(r"C:/Program Files/Siemens/Automation/Portal V18/PublicAPI/V18/Siemens.Engineering.dll")): And(str, Use(Path), lambda p: Path(p)),
        Optional("enable_ui", default=True): bool,
        "project": {
            "name": str,
            Optional("directory", default=Path.home()): And(str, Use(Path), lambda p: Path(p)),
            Optional("overwrite", default=False): bool,
            Optional("devices", default=[]): And(list, [Or(schema_device_plc, schema_device_hmi, schema_device_ionode)]),  # List of DEVICE
            Optional("networks", default=[]): And(list, [schema_network]),  # List of NETWORK
            Optional("libraries", default=[]): And(list, [schema_library]),  # List of LIBRARY
        },
    },
    ignore_extra_keys=True  
)

def validate_config(data):
    return schema.validate(data)

s = None

# Define the schema
s = Schema(
    {
        "name": str,
        "extra": Schema({
            Optional("other"): str,
            Optional("ss"): s  # Reference itself
        })
    },
    name="ss",
    as_reference=True
)

# Example data
d = {
    'name': 'win',
    'extra': {
        "other": "shit",
        "ss": {
            "name": "another",  # This must match the structure expected by s
            "extra": {
                "other": "more data",
                "ss": None  # This can also be None if not needed
            }
        }
    }
}

o = s.validate(d)
print()
print(o)
import json
print(json.dumps(s.json_schema("https://example.com/my-schema.json"), indent=2))

from enum import Enum
from jsonschema import validate, Draft7Validator
from pathlib import Path
from typing import Any
import jsonschema

class Source(Enum):
    CONFIG = "CONFIG"
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
        "path": {"type": "string", "default": "", "format": "path"},
        "read_only": {"type": "boolean", "default": True},
    }
}

PROJECT = {
    "type": "object",
    "required": ["name"],
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
    "required": ["dll", "project"],
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
    try:
        Path(instance)
    except TypeError as e:
        yield jsonschema.ValidationError(f"{instance} should be string. {e}")

validator = Draft7Validator(SCHEMA)
validator.VALIDATORS["path"] = validate_path

import json

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
        validate(instance=config, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        return {"error": f"Validation error: {e.message}"}
    else:
        return apply_defaults_and_filter(config, schema)

import json
from pathlib import Path

SCHEMA = {
    "dll": {"type": Path, "default": Path(r'"C:/Program Files/Siemens/Automation/Portal V18/PublicAPI/V18/Siemens.Engineering.dll')},
    "enable_ui": {"type": bool, "default": True},
    "project": {
        "type": dict,
        "default": {},
        "schema": {
            "name": {"type": str, "default": "AwesomeTIA420"},
            "directory": {"type": Path, "default": Path.home()},
            "overwrite": {"type": bool, "default": False},
            "devices": {
                "type": list,
                "default": [],
                "item_schema": {
                    "network_address": {"type": str, "default": "192.168.0.112"},
                    "slots_required": {"type": int, "default": 2},
                    "Local modules": {
                        "type": list,
                        "default": [],
                        "item_schema": {
                            "TypeIdentifier": {"type": str, "default": ""},
                            "Name": {"type": str, "default": ""},
                            "PositionNumber": {"type": int, "default": 0}
                        }
                    },
                    "PLC tags": {
                        "type": dict,
                        "default": {},
                        "schema": {
                            "Name": {"type": str, "default": ""},
                            "Tags": {
                                "type": list,
                                "default": [],
                                "item_schema": {
                                    "Name": {"type": str, "default": ""},
                                    "DataTypeName": {"type": str, "default": ""},
                                    "LogicalAddress": {"type": str, "default": ""}
                                }
                            }
                        }
                    },
                    "p_name": {"type": str, "default": "PLC_1"},
                    "p_typeIdentifier": {"type": str, "default": "OrderNumber:6ES7 510-1DJ01-0AB0/V2.0"},
                    "p_deviceName": {"type": str, "default": "NewPlcDevice"},
                }
            },
            "networks": {
                "type": list,
                "default": [],
                "item_schema": {
                    "address": {"type": str, "default": "192.168.0.112"},
                    "subnet_name": {"type": str, "default": "Profinet"},
                    "io_controller": {"type": str, "default": "PNIO"}
                }
            },
            "libraries": {
                "type": list,
                "default": [],
                "item_schema": {
                    "path": {"type": Path, "default": Path()},
                    "read_only": {"type": bool, "default": True},
                }
            },
        }
    }
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
                else:
                    cleaned_config[key] = value  # Accept as-is if no item_schema
            elif expected_type['type'] == Path:
                cleaned_config[key] = Path(value)  # Convert to Path
            else:
                cleaned_config[key] = value
        elif expected_type['type'] == bool and isinstance(value, str):
            cleaned_config[key] = value.lower() in ['true', '1']
        elif expected_type['type'] == list and isinstance(value, str):
            cleaned_config[key] = value.split(',')
        elif expected_type['type'] == dict and isinstance(value, str):
            cleaned_config[key] = json.loads(value)
        elif expected_type['type'] == Path and isinstance(value, str):
            cleaned_config[key] = Path(value)  # Convert string to Path
        else:
            cleaned_config[key] = expected_type['default']

    return cleaned_config


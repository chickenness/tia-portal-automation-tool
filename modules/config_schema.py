from enum import Enum
from pathlib import Path

class Source(Enum):
    LIBRARY = "LIBRARY"
    PLC = "PLC"

class Plc(Enum):
    OB = "OB"
    FB = "FB"
    FC = "FC"
    DB = "DB"

from schema import Schema, And, Or, Use, Optional, SchemaError

schema_source = {
    "name": str,
}

schema_source_plc = Schema({
    **schema_source,
    "plc": str, 
})

schema_source_library = Schema({
    **schema_source,
    "library": str, 
})

schema_single_instancedb = Schema({
    "name": str,
    Optional("number", default=1): int,
    "instanceOfName": str
})

schema_multi_instance_db = Schema({

})

schema_program_block = dict()
schema_program_block.update({
    "name": str,
    "type": And(str, Use(Plc)),
    Optional("number", default=0): int,
    Optional("programming_language", default="LAD"): And(str, Use(str.upper)),
    Optional("source", default=None): Or(schema_source_plc, schema_source_library),
    Optional('instances', default=[]): [Schema(schema_program_block)],
})

schema_program_block_ob = {**schema_program_block}
schema_program_block_fb = {**schema_program_block}
schema_program_block_fc = {**schema_program_block}
schema_program_block_ob.update({
    Optional('instancedb', default={}): schema_single_instancedb,
})
schema_program_block_fb.update({
    Optional('instancedb', default={}): Or(schema_single_instancedb,),
})
schema_program_block_fc.update({
    Optional('instancedb', default={}): Or(schema_single_instancedb,),
})
schema_program_block_ob = Schema(schema_program_block_ob)
schema_program_block_fb = Schema(schema_program_block_fb)
schema_program_block_fc = Schema(schema_program_block_fc)


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
        Optional("Program blocks", default=[]): And(list, [Or(schema_program_block_ob,schema_program_block_fb,schema_program_block_fc)]),
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
        # Optional("dll", default=Path(r"C:/Program Files/Siemens/Automation/Portal V18/PublicAPI/V18/Siemens.Engineering.dll")): And(str, Use(Path), lambda p: Path(p)),
        # Optional("enable_ui", default=True): bool,
        # "project": {
        "name": str,
        Optional("directory", default=Path.home()): And(str, Use(Path), lambda p: Path(p)),
        Optional("overwrite", default=False): bool,
        Optional("devices", default=[]): And(list, [Or(schema_device_plc, schema_device_hmi, schema_device_ionode)]),
        Optional("networks", default=[]): And(list, [schema_network]),
        Optional("libraries", default=[]): And(list, [schema_library]),

        # },
    },
    ignore_extra_keys=True  
)

def validate_config(data):
    return schema.validate(data)


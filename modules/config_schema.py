from enum import Enum
from pathlib import Path
from schema import Schema, And, Or, Use, Optional, SchemaError

class SourceType(Enum):
    LIBRARY = "LIBRARY"
    PLC     = "PLC"

class PlcType(Enum):
    OB = "OB"
    FB = "FB"
    FC = "FC"

class DatabaseType(Enum):
    GLOBAL      = "GlobalDB"
    INSTANCE    = "InstanceDB"


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


schema_database = {
    "type": And(str, Use(DatabaseType)),
    "name": str,
    "programming_language": And(str, Use(str.upper)),
    Optional("number", default=1): int,
}

schema_globaldb = Schema(schema_database)
schema_instancedb = Schema({
    **schema_database,
    "instanceOfName": str,
    Optional("data", {}): Schema({
        Optional("Address", default="DB"): str,
        Optional("BlockNumber", default=1): int,
        Optional("BitOffset", default=0): int,
        Optional("Informative", default=True): bool,
    }),
})

schema_multi_instance_db = Schema({

})

schema_program_block = {
    "name": str,
    "programming_language": And(str, Use(str.upper)),
    Optional("number", default=0): int,
}

schema_program_block.update({
    "type": And(str, Or(Use(PlcType), Use(DatabaseType))),
    Optional("source", default=None): Or(schema_source_plc, schema_source_library),
    Optional('network_sources', default=[]): And(list, [[Schema(schema_program_block)]]),
})

        # Optional("directory", default=Path.home()): And(str, Use(Path), lambda p: Path(p)),
schema_program_block_ob = {**schema_program_block}
schema_program_block_fb = {**schema_program_block}
schema_program_block_fc = {**schema_program_block}
schema_program_block_ob.update({
    Optional('db', default={}): schema_instancedb,
    Optional('network_sources', default=[]): And(list, [[Schema(schema_program_block_ob)]]),
})
schema_program_block_fb.update({
    Optional('db', default={}): Or(schema_instancedb, schema_multi_instance_db),
    Optional('network_sources', default=[]): And(list, [[Schema(schema_program_block_fb)]]),
})
schema_program_block_fc.update({
    Optional('db', default={}): Or(schema_instancedb,),
    Optional('network_sources', default=[]): And(list, [[Schema(schema_program_block_fc)]]),
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
        Optional("Program blocks", default=[]): And(list, [Or(schema_program_block_ob,schema_program_block_fb,schema_program_block_fc, schema_globaldb)]),
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


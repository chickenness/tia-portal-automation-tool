from modules import config_schema, portal
from pathlib import Path

import json
# import wx



json_config = Path(r"C:\Users\Chi\Documents\TITUS GLOBAL\Data\configs\HeHeProject.json")
with open(json_config) as file:
    config = json.load(file)
    validated_config = config_schema.validate_config(config)

import clr
from System.IO import DirectoryInfo, FileInfo

DLL_PATH: Path = Path(r"C:/Program Files/Siemens/Automation/Portal V18/PublicAPI/V18/Siemens.Engineering.dll")
clr.AddReference(DLL_PATH.as_posix())
import Siemens.Engineering as SE

portal.execute(
    SE,
    validated_config,
    {
        "DirectoryInfo": DirectoryInfo,
        "FileInfo": FileInfo,
        "enable_ui": True,
    }
)

# from pprint import pprint
# pprint(validated_config)

# from modules import xml_builder
# from modules.config_schema import PlcType, DatabaseType
#
# data = {
#
#             "Program blocks": [
#                 {
#                     "type": "FB",
#                     "name": "FunctionBlock_1",
#                     "programming_language": "FBD"
#                 },
#                 {
#                     "type": "OB",
#                     "name": "YouKnow",
#                     "programming_language": "FBD",
#                     "source": {
#                         "name": "YouKnow",
#                         "library": "Library1"
#                     }
#                 },
#                 {
#                     "type": "FB",
#                     "name": "Reset_Main",
#                     "number": 2,
#                     "programming_language": "STL",
#                     "network_sources": [
#                         [
#                                 {
#                                     "type": "FB",
#                                     "name": "Reset_1a",
#                                     "programming_language": "FBD"
#                                 },
#                                 {
#                                     "type": "FB",
#                                     "name": "Reset_1b",
#                                     "programming_language": "FBD"
#                                 },
#                                 {
#                                     "type": "FB",
#                                     "name": "Reset_1c",
#                                     "programming_language": "FBD"
#                                 },
#                                 {
#                                     "type": "FB",
#                                     "name": "Reset_1d",
#                                     "programming_language": "FBD"
#                                 }
#                         ],
#                         [
#                                 {
#                                     "type": "FB",
#                                     "name": "Reset_3",
#                                     "programming_language": "FBD"
#                                 }
#                         ],
#                         [
#                                 {
#                                     "type": "FB",
#                                     "name": "Reset_4",
#                                     "programming_language": "FBD"
#                                 }
#                         ],
#                         [
#                                 {
#                                     "type": "FB",
#                                     "name": "Reset_5",
#                                     "programming_language": "FBD"
#                                 }
#                         ]
#                     ],
#                     "db": {
#                         "type": "GlobalDB",
#                         "name": "Reset_Main_DB",
#                         "programming_language": "DB",
#                         "instanceOfName": "Reset_Main"
#                     }
#                 }
#             ],
# }
#
# schema = config_schema.Schema({
#         config_schema.Optional("Program blocks", default=[]): config_schema.And(list, [config_schema.Or(config_schema.schema_program_block_ob,config_schema.schema_program_block_fb,config_schema.schema_program_block_fc)]),
# })
#
# blocks = schema.validate(data)
#
# for plc_block in blocks['Program blocks']:
#     xml_obj = xml_builder.PlcBlock(plc_block.get('type', PlcType.FB).value, plc_block.get('name'), plc_block.get('number'))
#     xml = xml_obj.build(
#         programming_language=plc_block.get('programming_language'),
#         network_sources=plc_block.get('network_sources', []),
#     )
#     # print(xml)
#     # print()
#     # print()
#
#     db = plc_block.get('db')
#     if db.get('type') == DatabaseType.GLOBAL:
#         xml_obj = xml_builder.Database(
#             db['type'].value,
#             db['name'],
#             db['number']
#         )
#         xml = xml_obj.build(db['programming_language'])
#         print(xml)

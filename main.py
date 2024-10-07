from modules import config_schema, portal
from pathlib import Path

import json
# import wx
import uuid
import tempfile



json_config = Path(r"C:\Users\Chi\Documents\TITUS GLOBAL\Data\configs\HeHeProject.json")
with open(json_config) as file:
    config = json.load(file)
    validated_config = config_schema.validate_config(config)

import clr
from System.IO import DirectoryInfo, FileInfo

clr.AddReference(Path(r"C:/Program Files/Siemens/Automation/Portal V18/PublicAPI/V18/Siemens.Engineering.dll").as_posix())
import Siemens.Engineering as SE

portal.execute(
    SE,
    validated_config,
    {
        "DirectoryInfo": DirectoryInfo,
        "FileInfo": FileInfo,
        "enable_ui": True
    }
)

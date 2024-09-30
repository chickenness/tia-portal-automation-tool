from modules import schema
from pathlib import Path

import json
import wx
import uuid
import tempfile



json_config = Path(r"C:\Users\Chi\Documents\TITUS GLOBAL\Data\configs\HeHeProject.json")
with open(json_config) as file:
    config = json.load(file)

    cleaned_config = schema.clean_config(config, schema.SCHEMA)

print(cleaned_config)

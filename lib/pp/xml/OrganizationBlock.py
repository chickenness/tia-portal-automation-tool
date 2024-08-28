from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from string import Template


@dataclass
class XML:
    Name: str
    Number: int
    ProgrammingLanguage: str
    Blocks: list[SWBlocksCompileUnit]
    MultilingualText: str

@dataclass
class SWBlocksCompileUnit:
    Id: int
    Parts: list[Call]
    Wires: list[Wire]
    ProgrammingLanguage: str

@dataclass
class Call:
    Uid: int
    Name: str
    BlockType: str
    BlockNumber: int
    InstanceUid: int
    ComponentName: str
    DataBlockType: str
    DataBlockNumber: int

@dataclass
class Wire:
    Uid: int
    EnUid: int

@dataclass
class WireB(Wire):
    EnoUid: int

@dataclass
class MultilingualText:
    Id: int
    ItemId: int


TEMPLATE_DIRECTORY: Path    = Path("./lib/pp/xml/Templates/OrganizationBlock/")
TEMPLATES: list[Path]       = [template for template in TEMPLATE_DIRECTORY.iterdir() if template.is_file()] 

xml: dict[str, Template] = {}
for template in TEMPLATES:
    with open(template, 'r') as file:
        xml[template.stem] = Template(file.read())


def build_xml(data: XML) -> str:
    blocks = ""
    for block in data.Blocks:
        blocks += build_sw_blocks_compile_unit(block)

    return xml['XML'].substitute(NAME=data.Name, NUMBER=data.Number, PROGRAMMING_LANGUAGE=data.ProgrammingLanguage, BLOCKS=blocks, MULTILINGUAL_TEXT=data.MultilingualText)

def build_sw_blocks_compile_unit(data: SWBlocksCompileUnit) -> str:
    parts = ""
    for part in data.Parts:
        parts += build_call(part)

    wires = ""
    for wire in data.Wires:
        if isinstance(wire, Wire):
            wires += build_wire(wire)
        if isinstance(wire, WireB):
            wires += build_wire_b(wire)

    return xml['SW.Blocks.CompileUnit'].substitute(ID=data.Id, PARTS=parts, WIRES=wires, PROGRAMMING_LANGUAGE=data.ProgrammingLanguage)

def build_call(data: Call) -> str:
    if data.Uid >= 2 and data.Uid < 123:
        raise ValueError(f"UID Value must be within range: 1; 123-32767. {data.Uid} is not valid.")

    return xml['Call'].substitute(UID=data.Uid, NAME=data.Name, BLOCK_TYPE=data.BlockType, BLOCK_NUMBER=data.BlockNumber, INSTANCE_UID=data.InstanceUid,
                                  COMPONENT_NAME=data.ComponentName, DB_TYPE=data.DataBlockType, DB_NUMBER=data.DataBlockNumber)

def build_wire(data: Wire) -> str:
    return xml['Wire'].substitute(UID=data.Uid, EN_UID=data.EnUid)

def build_wire_b(data: WireB) -> str:
    return xml['Wire_b'].substitute(UID=data.Uid, EN_UID=data.EnUid, ENO_UID=data.EnoUid)

def build_multilingual_text(data: MultilingualText) -> str:
    return xml['MultilingualText'].substitute(MULTILINGUAL_TEXT_ID=data.Id, MULTILINGUAL_TEXT_ITEM_ID=data.ItemId)


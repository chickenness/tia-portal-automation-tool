from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from string import Template


BLOCK_ID_START: int             = 3
BLOCK_ID_SKIP: int              = 5
CALL_ID_START: int              = 21
WIRE_ENO_ID_START: int          = 21
SW_BLOCK_OB: str                = "SW.Blocks.OB"
SW_BLOCK_FB: str                = "SW.Blocks.FB"
COMMON_TEMPLATES: list[Path]    = list(Path("./lib/pp/xml/Templates/common/").iterdir())
OB_TEMPLATES: list[Path]        = list(Path("./lib/pp/xml/Templates/OrganizationBlock/").iterdir())
FB_TEMPLATES: list[Path]        = list(Path("./lib/pp/xml/Templates/FunctionBlock/").iterdir())


@dataclass
class XML:
    BlockType: str
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

@dataclass
class WirePower(Wire):
    EnUid: int

@dataclass
class WireOpen(Wire):
    OpenUid: int
    EnUid: int

@dataclass
class WireEno(Wire):
    EnoUid: int
    EnUid: int

@dataclass
class MultilingualText:
    Id: int
    ItemId: int


def import_xml(addtional_templates: list[Path]) -> dict[str, Template]:
    templates: list[Path] = [file for file in COMMON_TEMPLATES+addtional_templates if file.is_file()]

    xml_templates: dict[str, Template] = {}
    for template in templates:
        with open(template, 'r') as file:
            xml_templates[template.stem] = Template(file.read())

    return xml_templates


def build_xml(data: XML, xml_templates: dict) -> str:
    if not data.Number == 1 and not (data.Number >= 123 and data.Number <= 32767):
        raise ValueError(f"UID Value must be within range: 1; 123-32767. {data.Number} is not valid.")
    blocks = ""
    for block in data.Blocks:
        blocks += build_sw_blocks_compile_unit(block, xml_templates)

    return xml_templates['XML'].substitute(BLOCK_TYPE=data.BlockType, NAME=data.Name, NUMBER=data.Number, PROGRAMMING_LANGUAGE=data.ProgrammingLanguage,
                                 BLOCKS=blocks, MULTILINGUAL_TEXT=data.MultilingualText)

def build_sw_blocks_compile_unit(data: SWBlocksCompileUnit, xml_templates: dict) -> str:
    parts = ""
    for part in data.Parts:
        parts += build_call(part, xml_templates)

    wires = ""
    for wire in data.Wires:
        if type(wire) == WirePower:
            wires += build_wire_power(wire, xml_templates)
        if type(wire) == WireOpen:
            wires += build_wire_open(wire, xml_templates)
        if type(wire) == WireEno:
            wires += build_wire_eno(wire, xml_templates)

    return xml_templates['SW.Blocks.CompileUnit'].substitute(ID=data.Id, PARTS=parts, WIRES=wires, PROGRAMMING_LANGUAGE=data.ProgrammingLanguage)

def build_call(data: Call, xml_templates: dict) -> str:
    return xml_templates['Call'].substitute(UID=data.Uid, NAME=data.Name, BLOCK_TYPE=data.BlockType, BLOCK_NUMBER=data.BlockNumber, INSTANCE_UID=data.InstanceUid,
                                  COMPONENT_NAME=data.ComponentName, DB_TYPE=data.DataBlockType, DB_NUMBER=data.DataBlockNumber)

def build_wire_power(data: WirePower, xml_templates: dict) -> str:
    return xml_templates['WirePower'].substitute(UID=data.Uid, EN_UID=data.EnUid)

def build_wire_open(data: WireOpen, xml_templates: dict) -> str:
    return xml_templates['WireOpen'].substitute(UID=data.Uid, OPEN_CON_UID=data.OpenUid, EN_UID=data.EnUid)

def build_wire_eno(data: WireEno, xml_templates: dict) -> str:
    return xml_templates['Wire_Eno'].substitute(UID=data.Uid, ENO_UID=data.EnoUid, EN_UID=data.EnUid)

def build_multilingual_text(data: MultilingualText, xml_templates: dict) -> str:
    return xml_templates['MultilingualText'].substitute(MULTILINGUAL_TEXT_ID=data.Id, MULTILINGUAL_TEXT_ITEM_ID=data.ItemId)


def save_xml(xml_path: Path, xml_data: str) -> None:
    if xml_path.exists():
        if xml_path.is_dir():
            return
    if xml_path.is_dir():
        return
    with open(xml_path, 'w') as file:
        file.write(xml_data)

def identify_block_type(plc_block_type: str) -> str:
    match plc_block_type:
        case "SW.Blocks.OB" | "OB":
            return SW_BLOCK_OB

        case "SW.Blocks.FB" | "FB":
            return SW_BLOCK_FB

        case _:
            return SW_BLOCK_OB

def generate_instance_network(network: list[dict[str, str]]) -> tuple[list[Call], int]:
    calls: list[Call] = []
    iteration = 0
    for instance in network:
        fb = instance['fb']
        db = instance['db']
        block_type = instance['type']

        part: Call = Call(CALL_ID_START+iteration, fb, block_type, 1, CALL_ID_START+1+iteration, db, fb, iteration+1)
        iteration += 2
        calls.append(part)

    return (calls, iteration)

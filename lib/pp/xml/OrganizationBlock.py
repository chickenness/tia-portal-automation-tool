from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from string import Template


BLOCK_ID_START: int     = 3
BLOCK_ID_SKIP: int      = 5
CALL_ID_START: int      = 21
WIRE_ENO_ID_START: int  = 21

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
    if not data.Number == 1 and not (data.Number >= 123 and data.Number <= 32767):
        raise ValueError(f"UID Value must be within range: 1; 123-32767. {data.Number} is not valid.")
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
        if type(wire) == Wire:
            wires += build_wire(wire)
        if type(wire) == WireB:
            wires += build_wire_b(wire)

    return xml['SW.Blocks.CompileUnit'].substitute(ID=data.Id, PARTS=parts, WIRES=wires, PROGRAMMING_LANGUAGE=data.ProgrammingLanguage)

def build_call(data: Call) -> str:

    return xml['Call'].substitute(UID=data.Uid, NAME=data.Name, BLOCK_TYPE=data.BlockType, BLOCK_NUMBER=data.BlockNumber, INSTANCE_UID=data.InstanceUid,
                                  COMPONENT_NAME=data.ComponentName, DB_TYPE=data.DataBlockType, DB_NUMBER=data.DataBlockNumber)

def build_wire(data: Wire) -> str:
    return xml['Wire'].substitute(UID=data.Uid, EN_UID=data.EnUid)

def build_wire_b(data: WireB) -> str:
    return xml['Wire_b'].substitute(UID=data.Uid, ENO_UID=data.EnoUid, EN_UID=data.EnUid)

def build_multilingual_text(data: MultilingualText) -> str:
    return xml['MultilingualText'].substitute(MULTILINGUAL_TEXT_ID=data.Id, MULTILINGUAL_TEXT_ITEM_ID=data.ItemId)

def generate(name: str, number: int, programming_language: str, networks: dict[int, list[dict[str, str]]], xml_path: Path) -> str:
    save_as_xml: bool = True
    if xml_path.is_dir():
        save_as_xml = False

    blocks: list[SWBlocksCompileUnit] = []

    count_for_id = 0
    for _id, network in networks.items():
        calls: list[Call] = []
        wires: list[Wire] = []
        iteration = 0
        for instance in network:
            fb = instance['fb']
            db = instance['db']
            block_type = instance['type']

            part: Call = Call(CALL_ID_START+iteration, fb, block_type, 1, CALL_ID_START+1+iteration, db, fb, iteration+1)
            iteration += 2
            calls.append(part)

        for i in range(len(calls)):
            uid = CALL_ID_START + iteration + i
            eno = WIRE_ENO_ID_START + (i * 2) - 2
            en = eno + 2
            if i == 0:
                wire: Wire = Wire(uid, 21)
                if len(calls) > 1:
                    print(f"i==0, {i}")
                    print(uid, 21)
            else:
                wire: Wire = WireB(uid, en, eno)
                if len(calls) > 1:
                    print(f"i>=1, {i}")
                    print(uid, eno, en)
            wires.append(wire)
        
        uid = (count_for_id * BLOCK_ID_SKIP) + BLOCK_ID_START
        block: SWBlocksCompileUnit = SWBlocksCompileUnit(uid, calls, wires, programming_language)

        blocks.append(block)
        count_for_id += 1

    uid = (count_for_id * BLOCK_ID_SKIP) + BLOCK_ID_START
    multilingual_text: str = build_multilingual_text(MultilingualText(uid + 5, uid + 6))
    xml: XML = XML(name, number, programming_language, blocks, multilingual_text)

    result: str = build_xml(xml)

    if save_as_xml:
        with open(xml_path.absolute(), 'w') as file:
            file.write(result)
    
    return result

from dataclasses import dataclass
from pathlib import Path
from string import Template


@dataclass
class XML:
    Name: str
    Number: int
    ProgrammingLanguage: str
    Blocks: list

@dataclass
class SWBlocksCompileUnit:
    Id: int
    Parts: list
    Wires: list
    ProgrammingLanguage: str

@dataclass
class Call:
    Uid: int
    Name: str
    BlockType: str
    BlockNumber: int
    InstanceUid: int
    ComponentName: str
    DatabaseType: str
    DatabaseBlockNumber: int

@dataclass
class WireA:
    Uid: int
    EnUid: int

@dataclass
class WireB:
    Uid: int
    EnUid: int
    EnoUid: int


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

    return xml['XML'].substitute(NAME=data.Name, NUMBER=data.Number, PROGRAMMING_LANGUAGE=data.ProgrammingLanguage, BLOCKS=blocks)

def build_sw_blocks_compile_unit(data: SWBlocksCompileUnit) -> str:
    parts = ""
    for part in data.Parts:
        parts += build_call(part)

    wires = ""
    for wire in data.Wires:
        if isinstance(wire, WireA):
            wires += build_wire_a(wire)
        if isinstance(wire, WireB):
            wires += build_wire_b(wire)

    return xml['SW.Blocks.CompileUnit'].substitute(ID=data.Id, PARTS=parts, WIRES=wires, PROGRAMMING_LANGUAGE=data.ProgrammingLanguage)

def build_call(data: Call) -> str:

    return xml['Call'].substitute(UID=data.Uid, NAME=data.Name, BLOCK_TYPE=data.BlockType, BLOCK_NUMBER=data.BlockNumber, INSTANCE_UID=data.InstanceUid,
                                  COMPONENT_NAME=data.ComponentName, DB_TYPE=data.DatabaseType, DB_BLOCK_NUMBER=data.DatabaseBlockNumber)

def build_wire_a(data: WireA) -> str:
    return xml['Wire_a'].substitute(UID=data.Uid, EN_UID=data.EnUid)

def build_wire_b(data: WireB) -> str:
    return xml['Wire_b'].substitute(UID=data.Uid, EN_UID=data.EnUid, ENO_UID=data.EnoUid)

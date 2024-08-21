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
        xml[template.name] = Template(file.read())


def build_xml(data: XML) -> str:
    compile_units = ""
    for block in data.Blocks:
        compile_units += build_sw_blocks_compile_unit(block)

    return xml['XML.xml'].substitute(NAME=data.Name, NUMBER=data.Number, PROGRAMMING_LANGUAGE=data.ProgrammingLanguage, BLOCKS=compile_units)

def build_sw_blocks_compile_unit(data: SWBlocksCompileUnit) -> str:

    return xml['SW.Blocks.CompileUnit.xml'].substitute(ID=data.Id, PARTS=data.Parts, WIRES=data.Wires, PROGRAMMING_LANGUAGE=data.ProgrammingLanguage)

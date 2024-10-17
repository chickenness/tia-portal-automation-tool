from typing import Any
import xml.etree.ElementTree as ET

from modules.config_schema import PlcType, DatabaseType

class XML:
    def __init__(self, block_type: str, name: str, number: int) -> None:
        if block_type in ["OB", "FB", "FC"]:
            self.plc_type = PlcType[block_type]
        else:
            self.plc_type = DatabaseType[block_type]

        self.root = ET.fromstring("<Document />") 
        self.SWBlock = ET.SubElement(self.root, f"SW.Blocks.{block_type}", attrib={'ID': str(0)})

        self.AttributeList = ET.SubElement(self.SWBlock, "AttributeList")
        ET.SubElement(self.AttributeList, "Name").text = name
        self.Number = ET.SubElement(self.AttributeList, "Number")
        self.Number.text = str(number)
        ET.SubElement(self.AttributeList, "Namespace")


    def export(self, root: ET.Element) -> str:
        return ET.tostring(root, encoding='utf-8').decode('utf-8')

class PlcBlock(XML):
    def __init__(self, block_type: str, name: str, number: int) -> None:
        super().__init__(block_type, name, number)

        # Interface
        Interface = ET.SubElement(self.AttributeList, "Interface")
        Sections = ET.SubElement(Interface, "Sections", attrib={"xmlns": "http://www.siemens.com/automation/Openness/SW/Interface/v5"})
        self.InputSection = ET.SubElement(Sections, "Section", attrib={"Name": "Input"})
        TempSection = ET.SubElement(Sections, "Section", attrib={"Name": "Temp"})
        ConstantSection = ET.SubElement(Sections, "Section", attrib={"Name": "Constant"})

        if self.plc_type == PlcType.OB:
            ET.SubElement(self.AttributeList, "SecondaryType").text = "ProgramCycle"
            self.Number.text = "1" if ((number > 1 and number < 123) or number == 0) else str(number)
            ET.SubElement(self.InputSection, "Member", attrib={
                "Name": "Initial_Call",
                "Datatype": "Bool",
                "Informative": "True",
            })
            ET.SubElement(self.InputSection, "Remanence", attrib={
                "Name": "Initial_Call",
                "Datatype": "Bool",
                "Informative": "True",
            })
        if self.plc_type == PlcType.FB:
            self.OutputSection = ET.SubElement(Sections, "Section", attrib={"Name": "Output"})
            InOutSection = ET.SubElement(Sections, "Section", attrib={"Name": "InOut"})
            self.StaticSection = ET.SubElement(Sections, "Section", attrib={"Name": "Static"})


    def build(self, programming_language: str,  network_sources: list[list[dict[str, Any]]]) -> str:
        ET.SubElement(self.AttributeList, "ProgrammingLanguage").text = programming_language

        # fix this part, no issue but make it consistent
        self.generate_object_list(self.SWBlock, network_sources, programming_language)
        
        if self.plc_type == PlcType.FB:
            self.generate_multi_instancedb(network_sources)

        return self.export(self.root)

    def generate_flgnet(self, calls: list[dict[str, Any]]) -> ET.Element:
        root = ET.fromstring("<FlgNet />")
        Parts = ET.SubElement(root, "Parts")
        Wires = ET.SubElement(root, "Wires")

        uid_counter = 0
        # create Parts
        for instance in calls:
            db = instance['db']
            Call = ET.SubElement(Parts, "Call", attrib={"UId": str(21 + uid_counter)})
            CallInfo = ET.SubElement(Call, "CallInfo", attrib={
                "Name": db.get('instanceOfName', instance['name']),
                "BlockType": instance.get('type', PlcType.FB).value,
            })
            Instance = ET.SubElement(CallInfo, "Instance", attrib={
                "Scope": "GlobalVariable" if db.get('type') == DatabaseType.SINGLE else "LocalVariable",
                "UId": str(22 + uid_counter),
            })
            ET.SubElement(Instance, "Component", attrib={"Name": db.get('name', f"{instance['name']}_DB")})
            
            # TODO: implement Parameter for Multi InstanceDB

            uid_counter += 2

        # create Wires
        e = 1
        for i, instance in enumerate(calls):
            Wire = ET.SubElement(Wires, "Wire", attrib={'UId': str(21 + uid_counter + i + e)})
            if i == 0:
                ET.SubElement(Wire, "OpenCon", attrib={'UId': str(21 + uid_counter)})
                # ET.SubElement(Wire, "Powerrail")
                ET.SubElement(Wire, "NameCon", attrib={
                    'UId': str(21 + i),
                    'Name': 'en'
                })
                continue
            ET.SubElement(Wire, "NameCon", attrib={
                'UId': str(21 + (2 * i) - 2),
                'Name': 'eno'
            })
            ET.SubElement(Wire, "NameCon", attrib={
                'UId': str(21 + (2 * i)),
                'Name': 'en'
            })
                

        root.set('xmlns', "http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4")

        return root

    def generate_object_list(self, parent: ET.Element, network_sources: list[list[dict[str, Any]]], programming_language: str) -> ET.Element:
        root = ET.SubElement(parent, "ObjectList")

        id_counter = 0
        for network in network_sources:
            compile_unit = ET.SubElement(root, "SW.Blocks.CompileUnit", attrib={
                "ID": format(3 + id_counter, 'X'),
                "CompositionName": "CompileUnits",
            })
            AttributeList = ET.SubElement(compile_unit, "AttributeList")
            NetworkSource = ET.SubElement(AttributeList, "NetworkSource")
            NetworkSource.append(self.generate_flgnet(network))

            ET.SubElement(AttributeList, "ProgrammingLanguage").text = programming_language

            id_counter += 5

        return root

    def generate_multi_instancedb(self, network_sources: list[list[dict[str, Any]]]):
        for networks in network_sources:
            for instance in networks:
                if not instance.get('db'):
                    continue
                if not instance['db']['type'] == DatabaseType.MULTI:
                    continue
                el = ET.SubElement(self.StaticSection, "Member", attrib={
                    "Name": f"{instance['name']}_Instance",
                    "Datatype": f'"{instance["name"]}"',
                })
                ET.SubElement(ET.SubElement(el, "AttributeList"), "BooleanAttribute", attrib={
                    "Name": "SetPoint",
                    "SystemDefined": "true",
                }).text = "true"


class GlobalDB(XML):
    def __init__(self, block_type: str, name: str, number: int) -> None:
        super().__init__(block_type, name, number)

    def build(self, programming_language: str) -> str:
        ET.SubElement(self.AttributeList, "ProgrammingLanguage").text = programming_language
        ET.SubElement(self.SWBlock, "ObjectList")

        return self.export(self.root)

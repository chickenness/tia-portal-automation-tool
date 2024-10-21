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
    def __init__(self, block_type: str, name: str, number: int, db: dict[str, Any]) -> None:
        super().__init__(block_type, name, number)

        self.db = db

        # Interface
        Interface = ET.SubElement(self.AttributeList, "Interface")
        self.Sections = ET.SubElement(Interface, "Sections", attrib={"xmlns": "http://www.siemens.com/automation/Openness/SW/Interface/v5"})
        self.InputSection = ET.SubElement(self.Sections, "Section", attrib={"Name": "Input"})
        TempSection = ET.SubElement(self.Sections, "Section", attrib={"Name": "Temp"})
        ConstantSection = ET.SubElement(self.Sections, "Section", attrib={"Name": "Constant"})

    def build(self, programming_language: str,  network_sources: list[list[dict[str, Any]]]) -> str:
        ET.SubElement(self.AttributeList, "ProgrammingLanguage").text = programming_language

        ObjectList = ET.SubElement(self.SWBlock, "ObjectList")

        id_counter = 0
        for network in network_sources:
            compile_unit = ET.SubElement(ObjectList, "SW.Blocks.CompileUnit", attrib={
                "ID": format(3 + id_counter, 'X'),
                "CompositionName": "CompileUnits",
            })
            AttributeList = ET.SubElement(compile_unit, "AttributeList")
            NetworkSource = ET.SubElement(AttributeList, "NetworkSource")
            FlgNet = self.create_flgnet(network)
            NetworkSource.append(FlgNet)

            ET.SubElement(AttributeList, "ProgrammingLanguage").text = programming_language

            id_counter += 5

        return self.export(self.root)

    def create_parts(self, FlgNet: ET.Element, calls: list[dict[str, Any]]) -> ET.Element:
        Parts = ET.SubElement(FlgNet, "Parts")

        uids = self.calculate_uids(calls)
        call_uids = uids[0]
        wire_uids: list[int] = []

        for i, instance in enumerate(calls):
            db = instance['db']
            uid = call_uids[i]
            Call = ET.SubElement(Parts, "Call", attrib={"UId": str(uid)})
            CallInfo = ET.SubElement(Call, "CallInfo", attrib={
                "Name": db.get('instanceOfName', instance['name']),
                "BlockType": instance.get('type', PlcType.FB).value,
            })
            Instance = ET.SubElement(CallInfo, "Instance", attrib={
                "Scope": "GlobalVariable" if db.get('type') == DatabaseType.SINGLE else "LocalVariable",
                "UId": str(uid+1),
            })

            if db['type'] == DatabaseType.SINGLE:
                """
				<Instance Scope="GlobalVariable" UId="22">
					<Component Name="Block_DB" />
				</Instance>
                """
                ET.SubElement(Instance, "Component", attrib={"Name": db.get('name', f"{instance['name']}_DB")})



            if db['type'] == DatabaseType.MULTI:
                """
				<Instance Scope="LocalVariable" UId="24">
					<Component Name="Block_1_Instance_1" />
				</Instance>
				<Parameter Name="Gate 1" Section="Input" Type="Bool" />
				<Parameter Name="Gate 2" Section="Input" Type="Bool" />
				<Parameter Name="Result" Section="Output" Type="Bool" />
                """
                ET.SubElement(Instance, "Component", attrib={"Name": db.get('component_name', f"{instance['name']}_Instance")})
                for section in db['sections']:
                    wire_uids.append(uid)
                    for member in section['members']:
                        ET.SubElement(CallInfo, "Parameter", attrib={
                            "Name": member['Name'],
                            "Section": section['name'],
                            "Type": member['Datatype']
                        })
                        wire_uids.append(uid)

        return Parts

    def create_wires(self, FlgNet: ET.Element, calls: list[dict[str, Any]]) -> ET.Element:
        Wires = ET.SubElement(FlgNet, "Wires")


        i = self.calculate_uids(calls)[2]
        count = self.calculate_uids(calls)[1]

        for instance in calls:
            db = instance['db']
            for wire in db.get('wires', []):
                Wire = ET.SubElement(Wires, "Wire", attrib={'UId': str(i+count)})
                ET.SubElement(Wire, "NameCon", attrib={
                    "UId": str(-1),
                    "Name": wire['name']
                })
                match wire['component'].lower():
                    case "opencon":
                        ET.SubElement(Wire, "OpenCon", attrib={
                            'UId': str(i),
                        })
                match wire['connect'].lower():
                    case "opencon":
                        ET.SubElement(Wire, "OpenCon", attrib={
                            'UId': str(i),
                        })
                    case _:
                        elname = "Powerrail"
                i += 1

        # e = 1
    #     for i, instance in enumerate(calls):
    #         Wire = ET.SubElement(Wires, "Wire", attrib={'UId': str(21 + uid_counter + i + e)})
    #         ET.SubElement(Wire, "OpenCon", attrib={'UId': str(21 + uid_counter)})
				#
    #         db = instance['db']
    #         if db['type'] == DatabaseType.SINGLE:
    #             if i == 0:
    #                 # ET.SubElement(Wire, "Powerrail")
    #                 ET.SubElement(Wire, "NameCon", attrib={
    #                     'UId': str(21 + i),
    #                     'Name': 'en'
    #                 })
    #                 continue
    #             ET.SubElement(Wire, "NameCon", attrib={
    #                 'UId': str(21 + (2 * i) - 2),
    #                 'Name': 'eno'
    #             })
    #             ET.SubElement(Wire, "NameCon", attrib={
    #                 'UId': str(21 + (2 * i)),
    #                 'Name': 'en'
    #             })
    #                 
    #         if db['type'] == DatabaseType.MULTI:
    #             """
    #             <Wire UId="32">
				# 	<OpenCon UId="25" />
				# 	<NameCon UId="21" Name="en" />
				# </Wire>
				# <Wire UId="33">
				# 	<OpenCon UId="26" />
				# 	<NameCon UId="21" Name="Gate 1" />
				# </Wire>
				# <Wire UId="34">
				# 	<OpenCon UId="27" />
				# 	<NameCon UId="21" Name="Gate 2" />
				# </Wire>
				# <Wire UId="35">
				# 	<NameCon UId="21" Name="Result" />
				# 	<OpenCon UId="28" />
				# </Wire>
				# <Wire UId="36">
				# 	<NameCon UId="21" Name="eno" />
				# 	<NameCon UId="23" Name="en" />
				# </Wire>
				# <Wire UId="37">
				# 	<OpenCon UId="29" />
				# 	<NameCon UId="23" Name="Gate 1" />
				# </Wire>
				# <Wire UId="38">
				# 	<OpenCon UId="30" />
				# 	<NameCon UId="23" Name="Gate 2" />
				# </Wire>
				# <Wire UId="39">
				# 	<NameCon UId="23" Name="Result" />
				# 	<OpenCon UId="31" />
				# </Wire>
    #             """
    #             pass

        return Wires


    def create_flgnet(self, calls: list[dict[str, Any]]) -> ET.Element:
        root = ET.fromstring("<FlgNet />")
        self.create_parts(root, calls)
        self.create_wires(root, calls)

        root.set('xmlns', "http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4")

        return root



    def calculate_uids(self, calls: list[dict[str, Any]]) -> tuple[list[int], int, int]:
        calls_id_end: int = len(calls) + 21 + 2
        call_uids: list[int] = [i for i in range(21,calls_id_end,2)]
        i = 0
        for c in calls:
            for wire in c['db'].get('wires', []):
                if "opencon" in (v.lower() for v in wire.values()):
                    i += 1

        return (call_uids,i, calls_id_end)




class OB(PlcBlock):
    def __init__(self, name: str, number: int, db: dict[str, Any]) -> None:
        super().__init__("OB", name, number, db)

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


class FB(PlcBlock):
    def __init__(self, name: str, number: int, db: dict[str, Any]) -> None:
        super().__init__("FB", name, number, db)

        self.OutputSection = ET.SubElement(self.Sections, "Section", attrib={"Name": "Output"})
        self.InOutSection = ET.SubElement(self.Sections, "Section", attrib={"Name": "InOut"})
        self.StaticSection = ET.SubElement(self.Sections, "Section", attrib={"Name": "Static"})

    def build(self, programming_language: str, network_sources: list[list[dict[str, Any]]]) -> str:
        super().build(programming_language, network_sources)

        if self.db.get('type') == DatabaseType.MULTI:
            db = self.db
            for section in db['sections']:
                for member in section['members']:
                    match section['name']:
                        case "Input":
                            ET.SubElement(self.InputSection, "Member", attrib={
                                "Name": member['Name'],
                                "Datatype": member['Datatype']
                            })
                        case "Output":
                            ET.SubElement(self.OutputSection, "Member", attrib={
                                "Name": member['Name'],
                                "Datatype": member['Datatype']
                            })

        for networks in network_sources:
            for instance in networks:
                if not instance.get('db'):
                    continue
                if not instance['db']['type'] == DatabaseType.MULTI:
                    continue
                el = ET.SubElement(self.StaticSection, "Member", attrib={
                    "Name": instance.get('db', {}).get('component_name', f"{instance['name']}_Instance"),
                    "Datatype": f'"{instance["name"]}"',
                })
                ET.SubElement(ET.SubElement(el, "AttributeList"), "BooleanAttribute", attrib={
                    "Name": "SetPoint",
                    "SystemDefined": "true",
                }).text = "true"


        return self.export(self.root)




class GlobalDB(XML):
    def __init__(self, block_type: str, name: str, number: int) -> None:
        super().__init__(block_type, name, number)

    def build(self, programming_language: str) -> str:
        ET.SubElement(self.AttributeList, "ProgrammingLanguage").text = programming_language
        ET.SubElement(self.SWBlock, "ObjectList")

        return self.export(self.root)

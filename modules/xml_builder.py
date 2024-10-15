from typing import Any
import xml.etree.ElementTree as ET

from modules.config_schema import PlcType, DatabaseType

INTERFACE_MEMBER = [ {
        '@Accessibility': 'Public',
        '@Datatype': '"Data_Point"',
        '@Informative': False,
        '@Name': 'Data_Point_Instance',
        '@Remanence': 'NonRetain',
        'AttributeList': {
            'BooleanAttribute': [
                { '$': True,
                    '@Informative': False,
                    '@Name': 'ExternalAccessible',
                    '@SystemDefined': True },
                { '$': True,
                    '@Informative': False,
                    '@Name': 'ExternalVisible',
                    '@SystemDefined': True },
                { '$': True,
                    '@Informative': False,
                    '@Name': 'ExternalWritable',
                    '@SystemDefined': True },
                { '$': True,
                    '@Informative': True,
                    '@Name': 'UserVisible',
                    '@SystemDefined': True },
                { '$': False,
                    '@Informative': True,
                    '@Name': 'UserReadOnly',
                    '@SystemDefined': True },
                { '$': True,
                    '@Informative': True,
                    '@Name': 'UserDeletable',
                    '@SystemDefined': True },
                { '$': True,
                    '@Informative': False,
                    '@Name': 'SetPoint',
                    '@SystemDefined': True }
            ]
        },
       'Sections': [
            { 'Section': [
                    { '@Name': 'Input',
                        'Member': [
                            {
                                '@Accessibility': 'Public',
                                '@Datatype': 'Bool',
                                '@Informative': False,
                                '@Name': 'Gate ' '2',
                                '@Remanence': 'NonRetain'
                            },
                            {
                                '@Accessibility': 'Public',
                                '@Datatype': 'Bool',
                                '@Informative': False,
                                '@Name': 'Gate ' '1',
                                '@Remanence': 'NonRetain'
                            }
                        ] },
                    { '@Name': 'Output',
                        'Member': [
                            {
                                '@Accessibility': 'Public',
                                '@Datatype': 'Bool',
                                '@Informative': False,
                                '@Name': 'Open',
                                '@Remanence': 'NonRetain'
                            }
                        ] },
                    { '@Name': 'InOut' },
                    { '@Name': 'Static' }
                ] }
        ]
    } ]

class Interface:
    def __init__(self, member: dict) -> str:
        xml = {
            'Sections': {
                'Section': [
                    {'@Name': 'Input'},
                    {'@Name': 'Output'},
                    {'@Name': 'InOut'},
                    {'@Name': 'Static', 'Member': member},
                    {'@Name': 'Temp'},
                    {'@Name': 'Constant'}
                ]
            }
        }

class XML:
    def __init__(self, block_type: str, name: str, number: int) -> None:
        self.root = ET.fromstring("<Document />") 
        self.SWBlock = ET.SubElement(self.root, f"SW.Blocks.{block_type}", attrib={'ID': str(0)})

        self.AttributeList = ET.SubElement(self.SWBlock, "AttributeList")
        ET.SubElement(self.AttributeList, "Name").text = name
        Number = ET.SubElement(self.AttributeList, "Number")
        Number.text = str(number)
        ET.SubElement(self.AttributeList, "Namespace")

        if block_type == 'OB':
            ET.SubElement(self.AttributeList, "SecondaryType").text = "ProgramCycle"
            Number.text = "1" if ((number > 1 and number < 123) or number == 0) else str(number)

    def export(self, root: ET.Element) -> str:
        return ET.tostring(root, encoding='utf-8').decode('utf-8')

class PlcBlock(XML):
    def build(self, programming_language: str,  network_sources: list[list[dict[str, Any]]]) -> str:
        ET.SubElement(self.AttributeList, "ProgrammingLanguage").text = programming_language

        # fix this part, no issue but make it consistent
        self.generate_object_list(self.SWBlock, network_sources, programming_language)

        return self.export(self.root)

    def generate_flgnet(self, calls: list[dict[str, Any]]) -> ET.Element:
        root = ET.fromstring("<FlgNet />")
        Parts = ET.SubElement(root, "Parts")
        Wires = ET.SubElement(root, "Wires")

        uid_counter = 0
        # create Parts

# <Address Area="DB" Type="Reset_8" BlockNumber="9" BitOffset="0" Informative="true" />
        from pprint import pprint

        for instance in calls:
            db = instance['db']
            Call = ET.SubElement(Parts, "Call", attrib={"UId": str(21 + uid_counter)})
            CallInfo = ET.SubElement(Call, "CallInfo", attrib={
                "Name": db.get('instanceOfName', instance['name']),
                "BlockType": instance.get('type', PlcType.FB).value,
            })
            Instance = ET.SubElement(CallInfo, "Instance", attrib={
                "Scope": "GlobalVariable" if db.get('type') == DatabaseType.INSTANCE else "LocalVariable",
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

class GlobalDB(XML):
    def build(self, programming_language: str) -> str:
        ET.SubElement(self.AttributeList, "ProgrammingLanguage").text = programming_language
        ET.SubElement(self.SWBlock, "ObjectList")

        return self.export(self.root)

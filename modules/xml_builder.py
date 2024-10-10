from typing import Any
import xml.etree.ElementTree as ET

from modules.config_schema import PlcType

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
    def export(self, root: ET.Element) -> str:
        return ET.tostring(root, encoding='utf-8').decode('utf-8')

    def update_element_texts(self, root: ET.Element, elements: dict[str, str]):
        for name, text in elements.items():
            el = root.find(name)
            if el is not None: el.text = text

    def update_attributes(self, root: ET.Element, element: str, attrs: dict[str, str]):
        el = root.find(element)
        if el is None:
            return
        for key, value in attrs.items():
            el.set(key, value)

class PlcBlock(XML):
    def build(self, name: str, number: int, programming_language: str, block_type: str, instances: list[list[dict[str, Any]]]) -> str:
        root = ET.fromstring("<Document />")
        SWBlock = ET.SubElement(root, f"SW.Blocks.{block_type}")

        AttributeList = ET.SubElement(SWBlock, "AttributeList")
        ObjectList = self.generate_object_list(SWBlock, instances, programming_language)

        ET.SubElement(AttributeList, "Name").text = name
        ET.SubElement(AttributeList, "Number").text = str(number)
        ET.SubElement(AttributeList, "ProgrammingLanguage").text = programming_language

        if block_type == 'OB':
            ET.SubElement(AttributeList, "SecondaryType").text = "ProgramCycle"
        
        return self.export(root)

    def generate_flgnet(self, calls: list[dict[str, Any]], db) -> ET.Element:
        root = ET.fromstring("<FlgNet />")
        Parts = ET.SubElement(root, "Parts")
        Wires = ET.SubElement(root, "Wires")

        uid_counter = 0
        # create Parts
        for instance in calls:
            Call = ET.SubElement(Parts, "Call", attrib={"UId": str(21 + uid_counter)})
            CallInfo = ET.SubElement(Call, "CallInfo", attrib={
                "Name": instance.get('name', 'Block_1'),
                "BlockType": instance.get('type', PlcType.FB).value,
            })
            Instance = ET.SubElement(CallInfo, "Instance", attrib={
                "Scope": "LocalVariable",
                "UId": str(22 + uid_counter),
            })
            Component = ET.SubElement(Instance, "Component", attrib={"Name": "PASSIVE"})
            # TODO: implement Parameter for Multi InstanceDB

            uid_counter += 2

        # create Wires
        for i, instance in enumerate(calls):
            Wire = ET.SubElement(Wires, "Wire", attrib={'UId': str(22 + uid_counter + i)})
            if i == 0:
                ET.SubElement(Wire, "OpenCon", attrib={'UId': str(21 + uid_counter)})
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

    def generate_object_list(self, parent: ET.Element, instances: list[list[dict[str, Any]]], programming_language: str) -> ET.Element:
        root = ET.SubElement(parent, "ObjectList")

        id_counter = 0
        for network in instances:
            compile_unit = ET.SubElement(root, "SW.Blocks.CompileUnit", attrib={
                "ID": format(3 + id_counter, 'X'),
                "CompositionName": "CompileUnits",
            })
            AttributeList = ET.SubElement(compile_unit, "AttributeList")
            NetworkSource = ET.SubElement(AttributeList, "NetworkSource")
            NetworkSource.append(self.generate_flgnet(network, {}))

            ET.SubElement(AttributeList, "ProgrammingLanguage").text = programming_language

            id_counter += 5

        return root


import xml.etree.ElementTree as ET

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

class PlcBlock:
    def __init__(self) -> None:
        self.xml = '''<?xml version="1.0" encoding="utf-8"?>
            <Document>
	            <SW.Blocks ID="0">
		            <AttributeList>
			            <Name>default</Name>
			            <Namespace />
			            <Number>0</Number>
			            <ProgrammingLanguage>LAD</ProgrammingLanguage>
		            </AttributeList>
		            <ObjectList>
		            </ObjectList>
	            </SW.Blocks>
            </Document>
            '''        

    def build(self, name: str, number: int, programming_language: str, block_type: str) -> str:
        root = ET.fromstring(self.xml)
        SWBlock = root.find('./SW.Blocks')
        if SWBlock is not None:
            SWBlock.tag = f"SW.Blocks.{block_type}"
        AttributeList = root.find('.//AttributeList')
        if AttributeList is not None:
            self.set_text(AttributeList, 'Name', name)
            self.set_text(AttributeList, 'Number', str(number))
            self.set_text(AttributeList, 'ProgrammingLanguage', programming_language)

        return ET.tostring(root, encoding='utf-8').decode('utf-8')

    def set_text(self, root: ET.Element, name: str, value: str) -> None:
        el = root.find(name)
        if el is not None: el.text = value


def instance(id: str, programming_language: str, parts: str, wires: str) -> str:
    xml = f'''<SW.Blocks.CompileUnit ID="{id}" CompositionName="CompileUnits">'''
    xml += '''<AttributeList>'''
    xml += f'''<ProgrammingLanguage>{programming_language}</ProgrammingLanguage>'''
    xml += '''<NetworkSource>'''
    xml += '''<FlgNet>'''

    xml += '''<Parts>'''
    xml += f'''{parts}'''
    xml += '''</Parts>'''

    xml += '''<Wires>'''
    xml += f'''{wires}'''
    xml += '''</Wires>'''

    xml += '''</FlgNet>'''
    xml += '''</NetworkSource>'''
    xml += '''</AttributeList>'''
    xml += f'''</SW.Blocks.CompileUnit>'''

    return xml

class Part:
    def __init__(self) -> str:
        pass

import xml.etree.ElementTree as ET

def build(interface: str, name: str, number: str, programming_language: str, instances: str, block_type: str) -> str:
    """
    A function to represent a base XML document for a specified block type.

    Attributes:
        interface (str): The interface schema.
        name (str): The name of the program block.
        number (str): The number of the program block.
        programming_language (str): The programming language of the program block.
        instances (str): Network calls or instances of the programming block.
        block_type (str): The type of the block (OB, FB, FC).

    Methods:
        base(interface: str, name: str, number: str, programming_language: str,
                 instances: str, block_type: str) -> str:
            Initializes the Base object and generates an XML document string used for importing program blocks to a plc device.
    """

    xml = '''<?xml version="1.0" encoding="utf-8"?>'''
    xml += '''<Document>'''
    xml += f'''<SW.Blocks.{block_type} ID="0">'''
    xml += '''<AttributeList>'''
    xml += f'''{interface}'''
    xml += '''<MemoryLayout>Optimized</MemoryLayout>'''
    xml += f'''<Name>{name}</Name>'''
    xml += '''<Namespace />'''
    xml += f'''<Number>{number}</Number>'''
    xml += f'''<ProgrammingLanguage>{programming_language}</ProgrammingLanguage>'''
    xml += '''</AttributeList>'''
    xml += '''<ObjectList>'''
    xml += f'''{instances}'''
    xml += '''</ObjectList>'''
    xml += f'''</SW.Blocks.{block_type}>'''
    xml += '''</Document>'''

    return xml

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

class SWBlocksCompileUnit:
    def __init__(self, ID: str, programming_language: str) -> None:
        xml = f'''<SW.Blocks.CompileUnit ID="{ID}" CompositionName="CompileUnits">'''
        xml += '''<AttributeList>'''
        xml += f'''<ProgrammingLanguage>{programming_language}</ProgrammingLanguage>'''
        xml += '''<NetworkSource>'''
        xml += '''<FlgNet>'''

        xml += '''<Parts>'''
        xml += '''</Parts>'''

        xml += '''<Wires>'''
        xml += '''</Wires>'''

        xml += '''</FlgNet>'''
        xml += '''</NetworkSource>'''
        xml += '''</AttributeList>'''
        xml += f'''</SW.Blocks.CompileUnit>'''

class Part:
    def __init__(self) -> str:
        pass

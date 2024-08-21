from dataclasses import dataclass
from string import Template

@dataclass
class XML:
    Name: str
    Number: int
    ProgrammingLanguage: str
    Blocks: list

@dataclass
class SW_Blocks_OB:
    Id: int
    Parts: list
    Wires: list
    ProgrammingLanguage: str


xml = Template("""<?xml version="1.0" encoding="utf-8"?>
<Document>
	<SW.Blocks.OB ID="0">
		<AttributeList>
			<Name>$NAME</Name>
			<Namespace />
			<Number>$NUMBER</Number>
			<ProgrammingLanguage>$PROGRAMMING_LANGUAGE</ProgrammingLanguage>
			<SecondaryType>ProgramCycle</SecondaryType>
		</AttributeList>
		<ObjectList>
			<MultilingualText ID="1" CompositionName="Comment">
				<ObjectList>
					<MultilingualTextItem ID="2" CompositionName="Items">
						<AttributeList>
							<Culture>en-US</Culture>
							<Text />
						</AttributeList>
					</MultilingualTextItem>
				</ObjectList>
			</MultilingualText>
			$BLOCKS
			<MultilingualText ID="D" CompositionName="Title">
				<ObjectList>
					<MultilingualTextItem ID="E" CompositionName="Items">
						<AttributeList>
							<Culture>en-US</Culture>
							<Text>"Main Program Sweep (Cycle)"</Text>
						</AttributeList>
					</MultilingualTextItem>
				</ObjectList>
			</MultilingualText>
		</ObjectList>
	</SW.Blocks.OB>
</Document>
""")

blocks_compile_unit = Template("""<SW.Blocks.CompileUnit ID="$ID" CompositionName="CompileUnits">
	<AttributeList>
		<NetworkSource>
			<FlgNet
				xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v4">
				<Parts>
				    $PARTS
				</Parts>
				<Wires>
					$WIRES
				</Wires>
			</FlgNet>
		</NetworkSource>
		<ProgrammingLanguage>$PROGRAMMING_LANGUAGE</ProgrammingLanguage>
	</AttributeList>
</SW.Blocks.CompileUnit>
""")

blocks_compile_unit_parts = Template("""<Call UId="$CALL_UID">
	<CallInfo Name="$CALL_NAME" BlockType="$BLOCK_TYPE">
		<IntegerAttribute Name="BlockNumber" Informative="true">$BLOCK_NUMBER</IntegerAttribute>
		<Instance Scope="GlobalVariable" UId="$INSTANCE_UID">
			<Component Name="COMPONENT_NAME" />
			<Address Area="DB" Type="$DB_TYPE" BlockNumber="$DB_BLOCK_NUMBER" BitOffset="0" Informative="true" />
		</Instance>
	</CallInfo>
</Call>
""")

blocks_compile_unit_wires_a = Template("""<Wire UId="$WIRE_UID">
	<Powerrail />
	<NameCon UId="$EN_UID" Name="en" />
</Wire>
""")

blocks_compile_unit_wires_b = Template("""<Wire UId="$WIRE_UID">
	<NameCon UId="$ENO_UID" Name="eno" />
	<NameCon UId="$EN_UID" Name="en" />
</Wire>
""")

def build_xml(data: XML) -> str:
    compile_units = ""
    for block in data.Blocks:
        compile_units += build_sw_blocks_ob(block)

    return xml.substitute(NAME=data.Name, NUMBER=data.Number, PROGRAMMING_LANGUAGE=data.ProgrammingLanguage, BLOCKS=compile_units)

def build_sw_blocks_ob(data: SW_Blocks_OB) -> str:

    return blocks_compile_unit.substitute(ID=data.Id, PARTS=data.Parts, WIRES=data.Wires, PROGRAMMING_LANGUAGE=data.ProgrammingLanguage)

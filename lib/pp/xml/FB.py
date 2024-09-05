from . import functions as F, formulas as f
from pathlib import Path


def generate(name: str, number: int, programming_language: str, networks: dict[int, list[dict[str, str]]],
                xml_path: Path) -> str:
    blocks: list[F.SWBlocksCompileUnit] = []

    count_for_id = 0
    for _id, network in networks.items():
        calls, iteration = F.generate_instance_network(network)
        wires: list[F.Wire] = F.generate_wire(calls, iteration, programming_language)
        # for i in range(len(calls)):
        #     uid = f.wire_fb_uid(iteration, i)
        #     eno = f.wire_eno(i)
        #     en = f.wire_en(i)
        #     opencon = f.wire_open(iteration)
        #     if i == 0:
        #         wire: F.Wire = F.WireOpen(uid, opencon, 21)
        #     else:
        #         wire: F.Wire = F.WireEno(uid, eno, en)
        #     wires.append(wire)
        
        uid = f.sw_blocks_objects_uid(count_for_id)
        block: F.SWBlocksCompileUnit = F.SWBlocksCompileUnit(uid, calls, wires, programming_language)

        blocks.append(block)
        count_for_id += 1

    templates = F.import_xml(F.FB_TEMPLATES)
    uid = f.sw_blocks_objects_uid(count_for_id)
    multilingual_text: str = F.build_multilingual_text(F.MultilingualText(uid + 5, uid + 6), templates)
    xml: F.XML = F.XML(F.SW_BLOCK_FB, name, number, programming_language, blocks, multilingual_text)

    result: str = F.build_xml(xml, templates)
    F.save_xml(xml_path, result)

    return result


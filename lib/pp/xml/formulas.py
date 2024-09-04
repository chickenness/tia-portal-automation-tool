from . import functions as F

def sw_blocks_objects_uid(count: int) -> int:
    return (count * F.BLOCK_ID_SKIP) + F.BLOCK_ID_START

def wire_ob_uid(iteration: int, i: int) -> int:
    return F.CALL_ID_START + iteration + i

def wire_fb_uid(iteration: int, i: int) -> int:
    return wire_ob_uid(iteration, i) + 1

def wire_eno(i: int) -> int:
    return F.WIRE_ENO_ID_START + (i * 2) - 2

def wire_en(i: int) -> int:
    return wire_eno(i) + 2

def wire_open(iteration: int) -> int:
    return F.CALL_ID_START + iteration

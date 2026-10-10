"""Hook the glyph draw to use the native 4x Latin pages (tools/font4x.py).

Glyph drawing has one path: 0x14464c builds a sprite block on its stack, with
the source rect at sp+0x24 (top, bottom, left, right, from 0x144950) and the
destination size at sp+0x1c / 0x20 (advance, cell height; flag 0x8000). It then
calls 0x144a30 (page texture for the code) at 0x1447e0 and draws with 0x13c42c.

The jal at 0x1447e0 now goes to `latin_tex`. For a font with 4x pages and a
code that has a 4x slot, it rewrites the caller's source rect to the 4x cell
(4x the original width, left trim 0) and returns the 4x page's texture handle
from the font table (0x64ee8 in segment 1, 0x54 bytes per font, page handles
at +0xC). Destination size is untouched, so text keeps its 1x layout and VWF
advances; the GPU samples 4x texels. Other codes fall through to 0x144a30.

The code and tables are appended to the last load segment (after its BSS, which
becomes explicit zeros in the file). Relocations use the PSP type-A format
(info = type | ofsbase << 8 | addrbase << 16) and are appended to the relocation
segment/section; the hook's existing R_MIPS_26 entry gets addrbase 1.
"""
import json
import os
import struct

import keystone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "work/output/font")
FONTS = [("Font14", 0), ("Font10", 1), ("FontStaff", 2)]
HOOK = 0x1447E0             # jal 0x144a30 inside the glyph draw
PAGE_TEXTURE = 0x144A30
FONT_TABLE = 0x64EE8        # segment-1 offset of the font table
R_26, R_HI16, R_LO16 = 4, 5, 6
SHT_PSPREL = 0x700000A0


def layouts():
    out = []
    for name, idx in FONTS:
        p = os.path.join(FONT_DIR, name + ".4x.json")
        out.append((idx, json.load(open(p)) if os.path.exists(p) else None))
    return out


def data_block(lays):
    """Per-font descriptors (16 bytes) followed by code -> slot+1 byte tables."""
    desc = bytearray(16 * len(lays))
    tables = bytearray()
    for idx, lay in lays:
        if not lay:
            continue
        codes = {int(k): v for k, v in lay["codes"].items()}
        tab = bytearray(max(codes) + 1)
        for code, slot in codes.items():
            assert slot < 255
            tab[code] = slot + 1
        cw4, ch4 = lay["cell4x"]
        struct.pack_into("<HHBBBBB", desc, 16 * idx, len(tab), len(tables), cw4, ch4,
                         lay["cols"], lay["per_page"], lay["first_page"])
        tables += tab
    return bytes(desc), bytes(tables)


def hi_lo(v):
    hi = (v + 0x8000) >> 16
    return hi, v - (hi << 16)


def assemble(code_off, desc_off, tables_off, nfonts):
    """Source for latin_tex; addresses are segment-1 offsets (relocated at load)."""
    dh, dl = hi_lo(desc_off)
    th, tl = hi_lo(tables_off)
    fh, fl = hi_lo(FONT_TABLE)
    src = f"""
    .set noreorder
    sltiu $at, $a0, {nfonts}
    beqz  $at, orig
    sll   $t0, $a0, 4
    lui   $at, {dh}
    addiu $at, $at, {dl}
    addu  $t0, $at, $t0
    lhu   $t1, 0($t0)
    sltu  $at, $a1, $t1
    beqz  $at, orig
    lhu   $t2, 2($t0)
    lui   $at, {th}
    addiu $at, $at, {tl}
    addu  $t3, $at, $t2
    addu  $t3, $t3, $a1
    lbu   $t3, 0($t3)
    beqz  $t3, orig
    addiu $t3, $t3, -1
    lbu   $t4, 7($t0)
    divu  $zero, $t3, $t4
    mflo  $t5
    mfhi  $t6
    lbu   $t4, 6($t0)
    divu  $zero, $t6, $t4
    mflo  $t7
    mfhi  $t8
    lbu   $t4, 5($t0)
    multu $t7, $t4
    mflo  $t9
    sw    $t9, 0x24($sp)
    addu  $t9, $t9, $t4
    sw    $t9, 0x28($sp)
    lbu   $t4, 4($t0)
    multu $t8, $t4
    mflo  $t9
    lw    $t1, 0x2c($sp)
    lw    $t2, 0x30($sp)
    subu  $t2, $t2, $t1
    sll   $t2, $t2, 2
    sw    $t9, 0x2c($sp)
    addu  $t9, $t9, $t2
    sw    $t9, 0x30($sp)
    lbu   $t4, 8($t0)
    addu  $t5, $t5, $t4
    sll   $t5, $t5, 2
    sll   $t1, $a0, 4
    addu  $t2, $a0, $t1
    sll   $t2, $t2, 2
    addu  $t1, $t1, $t2
    lui   $at, {fh}
    addiu $at, $at, {fl}
    addu  $t1, $t1, $at
    addu  $t1, $t1, $t5
    jr    $ra
    lw    $v0, 0xC($t1)
orig:
    j     {PAGE_TEXTURE}
    nop
"""
    ks = keystone.Ks(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 + keystone.KS_MODE_LITTLE_ENDIAN)
    # Assemble at address 0 of a scratch space: the only absolute operand is the
    # j to segment 0, encoded directly; branches are PC-relative.
    code = bytes(ks.asm(src, code_off)[0])
    words = list(struct.unpack(f"<{len(code) // 4}I", code))
    relocs = []
    for n, w in enumerate(words):
        op = w >> 26
        at = code_off + 4 * n
        if op == 2:                                  # j 0x144a30 (segment 0 target)
            words[n] = (w & 0xFC000000) | (PAGE_TEXTURE >> 2)
            relocs.append((at, R_26 | 1 << 8 | 0 << 16))
        elif op == 15:                               # lui $at, hi -> HI16 + following LO16
            relocs.append((at, R_HI16 | 1 << 8 | 1 << 16))
            relocs.append((at + 4, R_LO16 | 1 << 8 | 1 << 16))
            assert words[n + 1] >> 26 == 9           # addiu
    return struct.pack(f"<{len(words)}I", *words), relocs, src


def patch(elf):
    lays = layouts()
    if not any(l for _, l in lays):
        return elf, None
    data = bytearray(elf)
    phoff, = struct.unpack_from("<I", data, 0x1C)
    phnum, = struct.unpack_from("<H", data, 0x2C)
    ph = [list(struct.unpack_from("<8I", data, phoff + 32 * i)) for i in range(phnum)]
    seg1 = ph[1]
    assert seg1[0] == 1 and ph[2][0] == SHT_PSPREL
    _t, s1_off, s1_va, _pa, s1_filesz, s1_memsz, _f, _a = seg1
    ext = (s1_memsz + 15) & ~15                      # segment-1 offset of the extension
    desc, tables = data_block(lays)
    desc_off = ext
    tables_off = ext + len(desc)
    code_off = (tables_off + len(tables) + 15) & ~15
    code, new_relocs, src = assemble(code_off, desc_off, tables_off, len(FONTS))
    payload = desc + tables + bytes(code_off - tables_off - len(tables)) + code
    new_filesz = ext + len(payload)

    # hook: jal latin_tex (target is a segment-1 offset; its R_26 gets addrbase 1)
    old = struct.unpack_from("<I", data, 0xC0 + HOOK)[0]
    assert old == 0x0C000000 | (PAGE_TEXTURE >> 2), hex(old)
    struct.pack_into("<I", data, 0xC0 + HOOK, 0x0C000000 | (code_off >> 2))

    # relocation records: program header 2 and the PSPREL sections cover one blob
    rel_off, rel_size = ph[2][1], ph[2][4]
    rel = bytearray(data[rel_off:rel_off + rel_size])
    hits = [i for i in range(0, len(rel), 8) if struct.unpack_from("<I", rel, i)[0] == HOOK]
    assert len(hits) == 1 and struct.unpack_from("<I", rel, hits[0] + 4)[0] == R_26
    struct.pack_into("<I", rel, hits[0] + 4, R_26 | 0 << 8 | 1 << 16)
    rel += b"".join(struct.pack("<II", o, i) for o, i in new_relocs)

    old_end = s1_off + s1_filesz                      # file end of segment 1 data
    grow = new_filesz - s1_filesz
    out = bytearray(data[:old_end]) + bytes(ext - s1_filesz) + payload
    tail_start = len(out)
    shift = lambda off: off + grow if off >= old_end else off
    # rebuild the tail: [old_end, rel_off) unchanged bytes, new relocations, rest
    out += data[old_end:rel_off]
    new_rel_off = rel_off + grow
    out += rel
    out += data[rel_off + rel_size:]
    rgrow = len(rel) - rel_size
    def move(off):
        if off >= rel_off + rel_size:
            return off + grow + rgrow
        return shift(off)

    seg1[4] = seg1[5] = new_filesz
    ph[2][1] = new_rel_off
    ph[2][4] = len(rel)
    for i, p in enumerate(ph):
        struct.pack_into("<8I", out, phoff + 32 * i, *p)
    shoff, = struct.unpack_from("<I", data, 0x20)
    shnum, = struct.unpack_from("<H", data, 0x30)
    new_shoff = move(shoff)
    struct.pack_into("<I", out, 0x20, new_shoff)
    last_rel = None
    for i in range(shnum):
        h = new_shoff + 40 * i
        sh = list(struct.unpack_from("<10I", out, h))
        if sh[1] == 8 or sh[4] == 0 and sh[5] == 0:
            continue
        if sh[1] == SHT_PSPREL:
            sh[4] = sh[4] + grow
            if sh[4] + sh[5] == new_rel_off + rel_size:
                last_rel = i
                sh[5] += rgrow
        else:
            sh[4] = move(sh[4])
        struct.pack_into("<10I", out, h, *sh)
    assert last_rel is not None, "no PSPREL section ends the relocation blob"
    assert out[s1_off + s1_filesz:s1_off + ext] == bytes(ext - s1_filesz)
    report = {"extension": hex(s1_va + ext), "code": hex(s1_va + code_off), "code_bytes": len(code),
              "tables": len(tables), "relocs_added": len(new_relocs), "segment1_filesz": hex(new_filesz)}
    return bytes(out), report

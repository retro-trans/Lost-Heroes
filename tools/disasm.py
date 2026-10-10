"""Disassemble the decrypted EBOOT (relocatable PRX, file offset = address + 0xC0).

Usage:
    python tools/disasm.py <hex address> [count]          (default 64 instructions)
    python tools/disasm.py --calls <hex address>          (list jal sites calling it)
"""
import os
import struct
import sys

import capstone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELF = os.path.join(ROOT, "work/source/EBOOT.elf")
BASE = 0xC0
TEXT_END = 0x18B754


def load():
    return open(ELF, "rb").read()


def disasm(data, addr, count):
    md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 + capstone.CS_MODE_LITTLE_ENDIAN)
    code = data[BASE + addr:BASE + addr + 4 * count]
    out = []
    for ins in md.disasm(code, addr):
        out.append(f"{ins.address:08x}: {ins.mnemonic:8s} {ins.op_str}")
    return out


def callers(data, target):
    sites = []
    for a in range(0, TEXT_END, 4):
        w = struct.unpack_from("<I", data, BASE + a)[0]
        if w >> 26 == 3 and (w & 0x3FFFFFF) << 2 == target:
            sites.append(a)
    return sites


def main():
    data = load()
    if sys.argv[1] == "--calls":
        for a in callers(data, int(sys.argv[2], 16)):
            print(f"{a:08x}")
        return
    addr = int(sys.argv[1], 16)
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 64
    print("\n".join(disasm(data, addr, count)))


if __name__ == "__main__":
    main()

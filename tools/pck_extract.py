"""List or extract the "2NBF" ALLRES.PCK archive from USRDIR.

Header (16 bytes): magic "2NBF", u32 count, u32 data_start, u32 alignment.
Then `count` entries of 140 bytes: name[128], u32 offset (from data_start),
u32 unused, u32 size.

Usage:
    python tools/pck_extract.py <pck> list
    python tools/pck_extract.py <pck> extract <out_dir> [prefix_filter]
"""
import os
import struct
import sys

ENTRY = 140


def read_table(f):
    head = f.read(16)
    assert head[:4] == b"2NBF", "not a 2NBF archive"
    count, data_start, _align = struct.unpack_from("<III", head, 4)
    table = f.read(count * ENTRY)
    entries = []
    for i in range(count):
        e = table[i * ENTRY:(i + 1) * ENTRY]
        name = e[:128].split(b"\0")[0].decode("ascii")
        offset, _unused, size = struct.unpack_from("<III", e, 128)
        entries.append((name, data_start + offset, size))
    return entries


def main():
    pck, cmd = sys.argv[1], sys.argv[2]
    with open(pck, "rb") as f:
        entries = read_table(f)
        if cmd == "list":
            for name, off, size in entries:
                print(f"{off:10d} {size:10d} {name}")
        elif cmd == "extract":
            out = sys.argv[3]
            prefix = sys.argv[4] if len(sys.argv) > 4 else ""
            n = 0
            for name, off, size in entries:
                if not name.startswith(prefix):
                    continue
                dest = os.path.join(out, name)
                os.makedirs(os.path.dirname(dest) or out, exist_ok=True)
                f.seek(off)
                with open(dest, "wb") as o:
                    o.write(f.read(size))
                n += 1
            print(f"extracted {n} files to {out}")


if __name__ == "__main__":
    main()

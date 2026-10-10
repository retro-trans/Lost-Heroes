"""List or extract files from a PSP UMD ISO (plain ISO9660, 2048-byte sectors).

Usage:
    python tools/iso_extract.py <iso> list
    python tools/iso_extract.py <iso> extract <out_dir>
"""
import os
import struct
import sys

SECTOR = 2048


def read_dir(f, lba, size, prefix=""):
    f.seek(lba * SECTOR)
    data = f.read(size)
    pos = 0
    while pos < len(data):
        rec_len = data[pos]
        if rec_len == 0:
            # Records never cross sector boundaries; skip padding.
            pos = (pos // SECTOR + 1) * SECTOR
            continue
        rec = data[pos:pos + rec_len]
        ext_lba = struct.unpack_from("<I", rec, 2)[0]
        ext_size = struct.unpack_from("<I", rec, 10)[0]
        flags = rec[25]
        name_len = rec[32]
        name = rec[33:33 + name_len]
        pos += rec_len
        if name in (b"\x00", b"\x01"):
            continue
        name = name.decode("ascii", "replace").split(";")[0]
        path = prefix + "/" + name
        if flags & 2:
            yield from read_dir(f, ext_lba, ext_size, path)
        else:
            yield path, ext_lba, ext_size


def entries(f):
    f.seek(16 * SECTOR)
    pvd = f.read(SECTOR)
    assert pvd[1:6] == b"CD001", "not an ISO9660 image"
    root = pvd[156:156 + 34]
    lba = struct.unpack_from("<I", root, 2)[0]
    size = struct.unpack_from("<I", root, 10)[0]
    return list(read_dir(f, lba, size))


def main():
    iso, cmd = sys.argv[1], sys.argv[2]
    with open(iso, "rb") as f:
        items = entries(f)
        if cmd == "list":
            for path, lba, size in items:
                print(f"{lba:8d} {size:12d} {path}")
        elif cmd == "extract":
            out = sys.argv[3]
            for path, lba, size in items:
                dest = os.path.join(out, path.lstrip("/"))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                f.seek(lba * SECTOR)
                with open(dest, "wb") as o:
                    remaining = size
                    while remaining:
                        chunk = f.read(min(remaining, 1 << 20))
                        o.write(chunk)
                        remaining -= len(chunk)
            print(f"extracted {len(items)} files to {out}")


if __name__ == "__main__":
    main()

"""Recursively walk ALLRES.PCK, unpacking nested .cmp (ZIP) and .pck (2NBF)
containers, and yield every leaf file with its virtual path.

Virtual paths join container levels with "::", e.g.
    Graph/STARTUP_pk.cmp::pack.pck::Table/Item/ItemTbl.mbb

Usage:
    python tools/walk_assets.py <ALLRES.PCK> inventory
    python tools/walk_assets.py <ALLRES.PCK> dump <out_dir> <ext>[,<ext>...]
"""
import collections
import hashlib
import io
import os
import struct
import sys
import zipfile

ENTRY = 140


def nbf_entries(data):
    count, data_start, _align = struct.unpack_from("<III", data, 4)
    for i in range(count):
        e = data[16 + i * ENTRY:16 + (i + 1) * ENTRY]
        name = e[:128].split(b"\0")[0].decode("ascii").replace("\\", "/")
        offset, _unused, size = struct.unpack_from("<III", e, 128)
        yield name, data[data_start + offset:data_start + offset + size]


def walk(name, data):
    if data[:4] == b"2NBF":
        for child, blob in nbf_entries(data):
            yield from walk(f"{name}::{child}" if name else child, blob)
    elif data[:4] == b"PK\x03\x04":
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for child in z.namelist():
                yield from walk(f"{name}::{child}", z.read(child))
    else:
        yield name, data


def ext_of(path):
    leaf = path.rsplit("::", 1)[-1]
    return leaf.rsplit(".", 1)[-1].lower() if "." in leaf else ""


def main():
    pck, cmd = sys.argv[1], sys.argv[2]
    with open(pck, "rb") as f:
        root = f.read()
    if cmd == "inventory":
        count = collections.Counter()
        unique = collections.defaultdict(set)
        for path, blob in walk("", root):
            e = ext_of(path)
            count[e] += 1
            unique[e].add(hashlib.md5(blob).hexdigest())
        for e, n in count.most_common():
            print(f"{e:6s} {n:6d} files, {len(unique[e]):6d} unique")
    elif cmd == "dump":
        out, exts = sys.argv[3], set(sys.argv[4].split(","))
        n = 0
        for path, blob in walk("", root):
            if ext_of(path) in exts:
                dest = os.path.join(out, path.replace("::", "/"))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "wb") as o:
                    o.write(blob)
                n += 1
        print(f"dumped {n} files to {out}")


if __name__ == "__main__":
    main()

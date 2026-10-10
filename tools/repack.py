"""Write changed files back into ALLRES.PCK through nested 2NBF/ZIP layers.

changes: {virtual path: new bytes}; virtual paths are walk_assets' "a::b::c".
Containers on the path are rebuilt (2NBF keeps its alignment and entry order;
ZIP members keep their names and compression method); untouched members are
copied byte for byte.

Usage:
    python tools/repack.py --selftest <ALLRES.PCK>     (no-change rebuild == original)
"""
import io
import struct
import sys
import zipfile

ENTRY = 140


def nbf_parse(data):
    count, data_start, align = struct.unpack_from("<III", data, 4)
    entries = []
    for i in range(count):
        e = data[16 + i * ENTRY:16 + (i + 1) * ENTRY]
        name_raw = e[:128]
        offset, unused, size = struct.unpack_from("<III", e, 128)
        entries.append([name_raw, unused, data[data_start + offset:data_start + offset + size]])
    return entries, align, data_start


def align_up(n, a):
    return (n + a - 1) // a * a


def nbf_build(entries, align, magic=b"2NBF"):
    count = len(entries)
    data_start = align_up(16 + count * ENTRY, align)
    table, body = bytearray(), bytearray()
    for name_raw, unused, blob in entries:
        off = len(body)
        table += name_raw + struct.pack("<III", off, unused, len(blob))
        body += blob
        body += b"\0" * (align_up(len(body), align) - len(body))
    head = magic + struct.pack("<III", count, data_start, align) + table
    head += b"\0" * (data_start - len(head))
    return bytes(head + body)


def name_of(name_raw):
    return name_raw.split(b"\0")[0].decode("ascii").replace("\\", "/")


def rebuild(prefix, data, changes):
    """Return data with every change under `prefix` applied (or data unchanged)."""
    if prefix in changes:
        return changes[prefix]
    sub = {k for k in changes if k.startswith(prefix + "::") or not prefix}
    if not sub:
        return data
    if data[:4] == b"2NBF":
        entries, align, data_start = nbf_parse(data)
        dirty = False
        for e in entries:
            child = name_of(e[0])
            path = f"{prefix}::{child}" if prefix else child
            if any(k == path or k.startswith(path + "::") for k in sub):
                e[2] = rebuild(path, e[2], changes)
                dirty = True
        if not dirty:
            return data
        out = nbf_build(entries, align)
        # keep any header padding quirks of the original only if layout identical
        return out
    if data[:4] == b"PK\x03\x04":
        src = zipfile.ZipFile(io.BytesIO(data))
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as dst:
            for info in src.infolist():
                path = f"{prefix}::{info.filename}"
                blob = src.read(info.filename)
                if any(k == path or k.startswith(path + "::") for k in sub):
                    blob = rebuild(path, blob, changes)
                zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                zi.compress_type = info.compress_type
                zi.external_attr = info.external_attr
                dst.writestr(zi, blob)
        return buf.getvalue()
    raise ValueError(f"cannot descend into {prefix}")


def repack_file(src_path, dst_path, changes):
    """Stream-rebuild the outer ALLRES.PCK (too big for a 32-bit process)."""
    with open(src_path, "rb") as f:
        head = f.read(16)
        count, data_start, align = struct.unpack_from("<III", head, 4)
        table = f.read(count * ENTRY)
        new_table = bytearray()
        with open(dst_path, "wb") as out:
            out.write(b"\0" * data_start)
            pos = 0
            for i in range(count):
                e = table[i * ENTRY:(i + 1) * ENTRY]
                name_raw = e[:128]
                offset, unused, size = struct.unpack_from("<III", e, 128)
                f.seek(data_start + offset)
                blob = f.read(size)
                child = name_of(name_raw)
                if any(k == child or k.startswith(child + "::") for k in changes):
                    blob = rebuild(child, blob, changes)
                new_table += name_raw + struct.pack("<III", pos, unused, len(blob))
                out.write(blob)
                pad = align_up(len(blob), align) - len(blob)
                out.write(b"\0" * pad)
                pos += len(blob) + pad
            out.seek(0)
            out.write(head[:4] + struct.pack("<III", count, data_start, align) + new_table)


def selftest(pck):
    import filecmp
    import os
    import walk_assets
    tmp = pck + ".selftest"
    repack_file(pck, tmp, {})
    print("no-change outer rebuild identical:", filecmp.cmp(pck, tmp, shallow=False))
    # nested: rewrite one packed table with its own bytes; leaves must be unchanged
    target = "Event/Dg/N/C01/DG_EVENT_NC010101_pk.cmp::DG_EVENT_NC010101_pk.pck::Table/Event/Dungeon/NC01/MainEventMess0101.mbb"
    outer = target.split("::")[0]
    with open(pck, "rb") as f:
        data = f.read(16)
    entries = None
    import pck_extract
    with open(pck, "rb") as f:
        for name, off, size in pck_extract.read_table(f):
            if name == outer:
                f.seek(off)
                cmp_blob = f.read(size)
    leaves = dict(walk_assets.walk(outer, cmp_blob))
    new_cmp = rebuild(outer, cmp_blob, {target: leaves[target]})
    print("nested rebuild leaves identical:", dict(walk_assets.walk(outer, new_cmp)) == leaves,
          "| cmp size", len(cmp_blob), "->", len(new_cmp))
    os.remove(tmp)


if __name__ == "__main__":
    if sys.argv[1] == "--selftest":
        selftest(sys.argv[2])

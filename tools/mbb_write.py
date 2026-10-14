"""Rebuild TBB1/MTBL message tables with new strings.

Layout (same offsets and strings as the originals, see --selftest; the
originals carry 16-80 bytes of extra trailing padding per block with no
fixed rule, which the game never reads):
  TBB1 header: "TBB1", u32 0x10, u32 block_count, u32 file_size
  u32 block offsets, padded to 16
  each block: tag, u32 0x10, u32 body_size, u32 entry_count,
              u32 entry offsets (relative to body start; 0 = empty, below the table = marker), padded to 16,
              strings as u16 codes + 0x0000 terminator, each padded to 16
Blocks other than MTBL are copied unchanged.

Usage:
    python tools/mbb_write.py --selftest <ALLRES.PCK>
"""
import struct
import sys

import mbb


def pad16(b):
    return b + b"\0" * (-len(b) % 16)


def build_mtbl(strings, declared=None):
    """strings: list of code lists or None (empty slot). declared: the header
    entry count to write (the originals count one entry fewer than they hold)."""
    n = len(strings)
    table_len = len(pad16(b"\0" * (4 * n)))
    offsets, blob = [], b""
    for codes in strings:
        if codes is None:
            offsets.append(0)
            continue
        if isinstance(codes, mbb.Mark):
            offsets.append(codes.value)
            continue
        offsets.append(table_len + len(blob))
        blob += pad16(struct.pack(f"<{len(codes) + 1}H", *codes, 0))
    body = pad16(struct.pack(f"<{n}I", *offsets)) + blob
    return b"MTBL" + struct.pack("<III", 0x10, len(body), n if declared is None else declared) + body


def rebuild(data, replace):
    """replace: {block_index: [codes|None, ...]} for MTBL blocks to rewrite."""
    blocks = []
    for i, tag, off, size, n in mbb.blocks(data):
        if i in replace:
            blocks.append(build_mtbl(replace[i], n))
        else:
            blocks.append(data[off:off + 16 + size])
    count = len(blocks)
    head_len = len(pad16(b"\0" * (16 + 4 * count)))
    offsets, body = [], b""
    for b in blocks:
        offsets.append(head_len + len(body))
        body += pad16(b)
    out = pad16(b"TBB1" + struct.pack("<III", 0x10, count, 0) + struct.pack(f"<{count}I", *offsets)) + body
    return out[:12] + struct.pack("<I", len(out)) + out[16:]


def strings_of(data):
    out = {}
    for i, tag, off, size, n in mbb.blocks(data):
        if tag == "MTBL":
            out[i] = mbb.mtbl_strings(data, off, n)
    return out


def selftest(pck):
    import walk_assets
    root = open(pck, "rb").read()
    ok = bad = 0
    for vpath, blob in walk_assets.walk("", root):
        if blob[:4] == b"TBB1" and b"MTBL" in blob[:0x200]:
            new = rebuild(blob, strings_of(blob))
            same = strings_of(new) == strings_of(blob) and all(
                new[o2 + 16:o2 + 16 + 4 * n2] == blob[o1 + 16:o1 + 16 + 4 * n1]
                for (_, _, o1, _, n1), (_, _, o2, _, n2) in zip(mbb.blocks(blob), mbb.blocks(new)))
            if same:
                ok += 1
            else:
                bad += 1
                if bad <= 5:
                    print("mismatch:", vpath)
    print(f"round-trip same offsets+strings: {ok}, different: {bad}")


if __name__ == "__main__":
    if sys.argv[1] == "--selftest":
        selftest(sys.argv[2])

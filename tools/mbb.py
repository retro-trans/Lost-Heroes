"""Parse TBB1 containers and their MTBL message tables.

TBB1 header: magic "TBB1", u32 header_size (0x10), u32 block_count,
u32 total_size, then block_count u32 offsets to blocks.
Block header: 4-byte tag, u32 0x10, u32 body_size, u32 entry_count.
MTBL body: entry_count u32 offsets (relative to body start) to strings of
u16 glyph codes terminated by 0x0000. Offset 0 means an empty slot.
"""
import struct


def blocks(data):
    if data[:4] != b"TBB1":
        return
    _hsz, count, _total = struct.unpack_from("<III", data, 4)
    for i in range(count):
        off = struct.unpack_from("<I", data, 16 + i * 4)[0]
        tag = data[off:off + 4].decode("ascii", "replace")
        _h, size, n = struct.unpack_from("<III", data, off + 4)
        yield i, tag, off, size, n


class Mark(tuple):
    """An entry offset smaller than the offset table (1, 2, ...) is a marker, not
    a string, and the game relies on it: with the 1 in Table/Enemy/PlayerName.mbb
    the battle name plate picks the right hero; with a real offset there every hero
    showed "Rider 1". Falsy (an empty tuple), so readers treat it as empty;
    mbb_write writes `value` back."""
    def __new__(cls, value):
        obj = super().__new__(cls)
        obj.value = value
        return obj


MARK = Mark(1)


def entry_total(data, off, n):
    """Real number of entries in an MTBL block. The header count n excludes the
    last entry: slot n is a valid offset whenever the offset table has room
    for it before the first string (true for every table in the game)."""
    body = off + 16
    size = struct.unpack_from("<I", data, off + 8)[0]
    offs = [struct.unpack_from("<I", data, body + 4 * j)[0] for j in range(n)]
    nz = [o for o in offs if o >= 4 * (n + 1)]
    last = struct.unpack_from("<I", data, body + 4 * n)[0]
    if nz and 4 * (n + 1) <= min(nz):
        if last and min(nz) <= last < size:
            return n + 1
    elif not nz and last and 4 * (n + 1) <= last < size:
        # every counted entry is empty: the only string is in the extra slot
        # (single-message tables such as NC05/MainEventMess0585 "Something's here!")
        return n + 1
    return n


def mtbl_strings(data, off, n):
    """Return list of strings (each a list of u16 codes) for one MTBL block,
    or None for an empty slot. Includes the uncounted last entry (entry_total)."""
    body = off + 16
    out = []
    total = entry_total(data, off, n)
    for j in range(total):
        rel = struct.unpack_from("<I", data, body + j * 4)[0]
        if rel == 0:
            out.append(None)
            continue
        if rel < 4 * total:
            out.append(Mark(rel))
            continue
        p = body + rel
        codes = []
        while True:
            c = struct.unpack_from("<H", data, p)[0]
            if c == 0:
                break
            codes.append(c)
            p += 2
        out.append(codes)
    return out


def messages(data):
    """Yield (block_index, entry_index, codes) for every MTBL entry."""
    for i, tag, off, _size, n in blocks(data):
        if tag == "MTBL":
            for j, codes in enumerate(mtbl_strings(data, off, n)):
                yield i, j, codes

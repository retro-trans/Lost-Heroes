"""Replace one file inside the UMD ISO image.

If the new file fits in the sectors the old one occupied (up to the next
file's LBA), it is written in place; otherwise it is appended at the end of
the image. The directory record (LBA + size, both byte orders) and the
volume space size in the PVD are updated.

Usage:
    python tools/iso_patch.py <in.iso> <out.iso> <iso path> <new file>
    e.g. ... "/PSP_GAME/USRDIR/ALLRES.PCK" work/output/ALLRES.PCK
"""
import os
import shutil
import struct
import sys

import iso_extract

SECTOR = 2048


def find_record(f, target):
    """Return (record_offset_in_image, lba, size) of the directory record."""
    f.seek(16 * SECTOR)
    pvd = f.read(SECTOR)
    root = pvd[156:156 + 34]
    stack = [("", struct.unpack_from("<I", root, 2)[0], struct.unpack_from("<I", root, 10)[0])]
    while stack:
        prefix, lba, size = stack.pop()
        f.seek(lba * SECTOR)
        data = f.read(size)
        pos = 0
        while pos < len(data):
            n = data[pos]
            if n == 0:
                pos = (pos // SECTOR + 1) * SECTOR
                continue
            rec = data[pos:pos + n]
            name = rec[33:33 + rec[32]]
            if name not in (b"\0", b"\1"):
                name = name.decode("ascii").split(";")[0]
                path = prefix + "/" + name
                elba, esize = struct.unpack_from("<I", rec, 2)[0], struct.unpack_from("<I", rec, 10)[0]
                if rec[25] & 2:
                    stack.append((path, elba, esize))
                elif path.upper() == target.upper():
                    return lba * SECTOR + pos, elba, esize
            pos += n
    raise KeyError(target)


def main():
    src, dst, target, new_file = sys.argv[1:5]
    # Accept "PSP_GAME/..." too: Git Bash rewrites a leading "/" into a Windows path.
    target = "/" + target.replace("\\", "/").lstrip("/")
    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.copyfile(src, dst)
    new_size = os.path.getsize(new_file)
    with open(dst, "r+b") as f:
        rec_off, lba, size = find_record(f, target)
        ends = sorted(e[1] for e in iso_extract.entries(f) if e[1] > lba)
        limit = (ends[0] if ends else lba + (size + SECTOR - 1) // SECTOR) - lba
        f.seek(0, 2)
        image_end = f.tell()
        if (new_size + SECTOR - 1) // SECTOR <= limit:
            new_lba = lba
        else:
            new_lba = (image_end + SECTOR - 1) // SECTOR
        f.seek(new_lba * SECTOR)
        with open(new_file, "rb") as nf:
            shutil.copyfileobj(nf, f, 1 << 20)
        pad = (-f.tell()) % SECTOR
        f.write(b"\0" * pad)
        total_sectors = max(f.tell(), image_end) // SECTOR
        f.seek(rec_off + 2)
        f.write(struct.pack("<I", new_lba) + struct.pack(">I", new_lba))
        f.write(struct.pack("<I", new_size) + struct.pack(">I", new_size))
        f.seek(16 * SECTOR + 80)
        f.write(struct.pack("<I", total_sectors) + struct.pack(">I", total_sectors))
    where = "in place" if new_lba == lba else f"appended at LBA {new_lba}"
    print(f"{target}: {size} -> {new_size} bytes, {where}; volume {total_sectors} sectors")


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: GPL-2.0-or-later
# This file is a port of PPSSPP code (Core/ELF/PrxDecrypter.cpp, ext/libkirk) and is
# licensed under the GNU General Public License, version 2.0 or (at your option) any
# later version, like PPSSPP itself. See docs/licenses/GPL-2.0.txt. The rest of this
# repository is MIT licensed (LICENSE).
"""Decrypt the game's EBOOT.BIN (~PSP, tag 0xD91613F0, PRX type 2) to a plain ELF.

Port of the type-2 path of PPSSPP's Core/ELF/PrxDecrypter.cpp (pspDecryptType2,
expandSeed, decryptKirkHeader) and the KIRK CMD1/CMD7 operations from
ext/libkirk/kirk_engine.c. Only the tag used by Lost Heroes is included; the
SHA-1 over the rebuilt header is checked before decrypting, so a wrong key
fails loudly instead of producing garbage.

Usage:
    python tools/eboot_decrypt.py <EBOOT.BIN> <out.elf>
"""
import hashlib
import struct
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# PrxDecrypter.cpp: g_tagInfo2 { 0xD91613F0, key_D91613F0, 0x5D, 2 }
TAGS = {
    0xD91613F0: (bytes([0xEB, 0xFF, 0x40, 0xD8, 0xB4, 0x1A, 0xE1, 0x66,
                        0x91, 0x3B, 0x8F, 0x64, 0xB6, 0xFC, 0xB7, 0x12]), 0x5D),
}
# kirk_engine.c: keyvault[0x5D] (KIRK CMD4/7 key) and kirk1_key (CMD1 master key)
KEYVAULT = {
    0x5D: bytes([0x11, 0x5A, 0x5D, 0x20, 0xD5, 0x3A, 0x8D, 0xD3,
                 0x9C, 0xC5, 0xAF, 0x41, 0x0F, 0x0F, 0x18, 0x6F]),
}
KIRK1_KEY = bytes([0x98, 0xC9, 0x40, 0x97, 0x5C, 0x1D, 0x10, 0xE8,
                   0x7F, 0xE6, 0x0E, 0xA3, 0xFD, 0x03, 0xA8, 0xBA])


def aes_cbc_decrypt(key, data):
    d = Cipher(algorithms.AES(key), modes.CBC(bytes(16))).decryptor()
    return d.update(bytes(data)) + d.finalize()


def kirk7(data, code):
    return aes_cbc_decrypt(KEYVAULT[code], data)


def expand_seed(seed, code):
    buf = bytearray()
    for i in range(0, 0x90, 0x10):
        block = bytearray(seed)
        block[0] = i // 0x10
        buf += block
    return kirk7(buf, code)


def decrypt(inbuf):
    tag = struct.unpack_from("<I", inbuf, 0xD0)[0]
    if tag not in TAGS:
        raise SystemExit(f"unsupported tag 0x{tag:08X}")
    if any(inbuf[0xD4:0xD4 + 0x58]):
        raise SystemExit("not a type-2 PRX (0xD4..0x12C is not zero)")
    seed, code = TAGS[tag]
    decrypt_size = struct.unpack_from("<i", inbuf, 0xB0)[0]
    xorbuf = expand_seed(seed, code)

    # PRXType2: tag, empty[0x58], id, sha1, kirkHeader, kirkMetadata, prxHeader (0x150)
    t = bytearray(0x150)
    t[0x00:0x04] = inbuf[0xD0:0xD4]
    t[0x5C:0x6C] = inbuf[0x140:0x150]                       # id
    t[0x6C:0x80] = inbuf[0x12C:0x140]                       # sha1
    t[0x80:0xB0] = inbuf[0x80:0xB0]                         # kirk header (part 1)
    t[0xB0:0xC0] = inbuf[0xC0:0xD0]                         # kirk header (part 2)
    t[0xC0:0xD0] = inbuf[0xB0:0xC0]                         # kirk metadata
    t[0xD0:0x150] = inbuf[0x00:0x80]                        # prx header
    t[0x5C:0xBC] = kirk7(t[0x5C:0xBC], code)                # type2.decrypt: kirk7(id, 0x60)

    sha = hashlib.sha1()
    sha.update(t[0x00:0x04])
    sha.update(xorbuf[0x00:0x10])
    sha.update(t[0x04:0x5C])
    sha.update(t[0x5C:0x6C])
    sha.update(t[0x80:0xC0])
    sha.update(t[0xC0:0xD0])
    sha.update(t[0xD0:0x150])
    if sha.digest() != bytes(t[0x6C:0x80]):
        raise SystemExit("SHA-1 check failed (wrong key or tag table)")

    # KIRK CMD1 header (0x90): keys from decryptKirkHeader, metadata at 0x70, mode 1
    header = bytearray(0x90)
    header[0x70:0x80] = t[0xC0:0xD0]
    kh = bytes(a ^ b for a, b in zip(t[0x80:0xC0], xorbuf[0x10:0x50]))
    kh = kirk7(kh, code)
    header[0x00:0x40] = bytes(a ^ b for a, b in zip(kh, xorbuf[0x50:0x90]))
    struct.pack_into("<I", header, 0x60, 1)

    data_size, data_offset = struct.unpack_from("<II", header, 0x70)
    keys = aes_cbc_decrypt(KIRK1_KEY, header[0x00:0x20])
    # In the rebuilt buffer the header sits at 0x40 and is followed by the 0x80-byte
    # prx header, then the file data from 0x150 on.
    body = bytes(header) + bytes(inbuf[0x00:0x80]) + bytes(inbuf[0x150:])
    start = 0x90 + data_offset
    enc = body[start:start + ((data_size + 15) & ~15)]
    out = aes_cbc_decrypt(keys[0x00:0x10], enc)
    return out[:decrypt_size]


def main():
    src, dst = sys.argv[1], sys.argv[2]
    out = decrypt(open(src, "rb").read())
    if out[:4] != b"\x7fELF":
        raise SystemExit(f"decrypted data is not an ELF (starts {out[:8].hex()})")
    open(dst, "wb").write(out)
    print(f"wrote {dst}: {len(out)} bytes (ELF)")


if __name__ == "__main__":
    main()

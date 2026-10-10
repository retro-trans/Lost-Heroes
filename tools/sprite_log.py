"""Log sprite draws (texture object, sprite index, x, y) via a PPSSPP logging breakpoint
on the sprite routine 0x13c42c. Module base 0x08804000 (PPSSPP).

Usage (game running in the isolated PPSSPP):
    python tools/sprite_log.py [seconds]
"""
import asyncio
import json
import sys
import time

from ppsspp_dbg import Dbg

BASE = 0x8804000
SPRITE = 0x13C42C


def collect(d, seconds=2.0):
    d.call("cpu.breakpoint.add", address=BASE + SPRITE, enabled=False, log=True,
           logFormat="SPR {a0} {a1} {[a2+4]} {[a2+8]}")

    async def go():
        out, t0 = set(), time.time()
        while time.time() - t0 < seconds:
            try:
                m = json.loads(await asyncio.wait_for(d.ws.recv(), 0.5))
            except asyncio.TimeoutError:
                continue
            msg = m.get("message", "") if m.get("event") == "log" else ""
            if "SPR " in msg:
                p = msg[msg.index("SPR ") + 4:].split()
                out.add((p[0], int(p[1], 16), int(p[2], 16), int(p[3], 16)))
        return out
    try:
        return d.loop.run_until_complete(go())
    finally:
        d.call("cpu.breakpoint.remove", address=BASE + SPRITE)


if __name__ == "__main__":
    with Dbg() as d:
        for t in sorted(collect(d, float(sys.argv[1]) if len(sys.argv) > 1 else 2.0)):
            print(*t)

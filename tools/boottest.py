"""Boot an ISO in the isolated portable PPSSPP (work/build/ppsspp_test) and screenshot it.

Usage:
    python tools/boottest.py <iso> <out.png> [seconds]
"""
import os
import subprocess
import sys
import time

from ppsspp_dbg import Dbg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, "work/build/ppsspp_test/PPSSPPWindows64.exe")


def launch(iso):
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-Process PPSSPPWindows64 -ErrorAction SilentlyContinue | Stop-Process -Force"])
    time.sleep(2)
    return subprocess.Popen([EXE, os.path.abspath(iso)])


def main():
    iso, shot = sys.argv[1], sys.argv[2]
    wait = float(sys.argv[3]) if len(sys.argv) > 3 else 20
    launch(iso)
    time.sleep(wait)
    with Dbg() as d:
        print(d.call("game.status"))
        th = d.call("hle.thread.list").get("threads", [])
        print("threads:", [(t["name"], t["status"]) for t in th][:12])
    print("window:", Dbg.grab_window(shot))


if __name__ == "__main__":
    main()

import sys, glob, os, json, re
sys.path.insert(0, r"E:\Projects\Lost Heroes\tools")
sys.stdout.reconfigure(encoding="utf-8")
import lua51, speakers
ROOT = r"E:\Projects\Lost Heroes"
names = speakers.speaker_names()
gl = json.load(open(ROOT + r"\work\glossary\names.json", encoding="utf-8"))
jp2en = {e["jp"]: e["en"] for sec in ("heroes", "villains") for e in gl[sec]}
def offset_of(f):
    c = f["consts"]
    if "TextIdOffset" in c:
        i = c.index("TextIdOffset")
        for x in c[i+1:]:
            if isinstance(x, float): return int(x)
    for p in f["protos"]:
        r = offset_of(p)
        if r is not None: return r
room = sys.argv[1]
out = {}
for p in sorted(glob.glob(ROOT + rf"\work\source\flat\Event\Base\{room}\BASE_EVENT_TALK_{room}_pk.cmp\*\Event\Base\{room}\Talk*.bla")):
    nm = os.path.basename(p)
    if nm.startswith("TalkMgr"): continue
    f = lua51.load(open(p, "rb").read())
    off = offset_of(f)
    _t, _o, events = speakers.trace(p)
    for n, sp in events:
        spn = names.get(sp, sp) if isinstance(sp, int) else sp
        out[f"0.{off+n+1}"] = (nm, jp2en.get(spn, spn))
tbl = json.load(open(ROOT + rf"\work\source\text\Table\Event\Base\TalkMess{room}.mbb.json", encoding="utf-8"))
for r in tbl["rows"]:
    s = out.get(r["id"])
    print(r["id"], s, "|", r["jp"].replace("\n", " / ")[:60])

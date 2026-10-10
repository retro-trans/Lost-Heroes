"""Minimal Lua 5.1 bytecode reader for the event scripts (.bla).

Parses function prototypes and replays straight-line register moves to
recover global function calls with their arguments, e.g.
    CharaNameIn(CHARA_NAME.DAISUKE)   MessWinSet(12)

Usage:
    python tools/lua51.py <file.bla>          (prints the call trace)
"""
import struct
import sys


class Reader:
    def __init__(self, data):
        self.d, self.p = data, 0

    def take(self, n):
        b = self.d[self.p:self.p + n]
        self.p += n
        return b

    def u8(self):
        return self.take(1)[0]

    def i32(self):
        return struct.unpack("<i", self.take(4))[0]

    def num(self):
        return struct.unpack("<d", self.take(8))[0]

    def string(self):
        n = struct.unpack("<I", self.take(4))[0]
        return self.take(n)[:-1].decode("latin-1") if n else None


def read_function(r):
    f = {"source": r.string()}
    r.i32(); r.i32()
    f["nups"], f["nparams"], f["vararg"], f["maxstack"] = r.u8(), r.u8(), r.u8(), r.u8()
    f["code"] = [struct.unpack("<I", r.take(4))[0] for _ in range(r.i32())]
    consts = []
    for _ in range(r.i32()):
        t = r.u8()
        consts.append(None if t == 0 else bool(r.u8()) if t == 1 else r.num() if t == 3 else r.string())
    f["consts"] = consts
    f["protos"] = [read_function(r) for _ in range(r.i32())]
    for _ in range(r.i32()):
        r.i32()                                   # lineinfo
    for _ in range(r.i32()):
        r.string(); r.i32(); r.i32()              # locvars
    for _ in range(r.i32()):
        r.string()                                # upvalue names
    return f


def load(data):
    r = Reader(data)
    assert r.take(4) == b"\x1bLua" and r.u8() == 0x51
    r.take(7)
    return read_function(r)


OP = ["MOVE", "LOADK", "LOADBOOL", "LOADNIL", "GETUPVAL", "GETGLOBAL", "GETTABLE",
      "SETGLOBAL", "SETUPVAL", "SETTABLE", "NEWTABLE", "SELF", "ADD", "SUB", "MUL",
      "DIV", "MOD", "POW", "UNM", "NOT", "LEN", "CONCAT", "JMP", "EQ", "LT", "LE",
      "TEST", "TESTSET", "CALL", "TAILCALL", "RETURN", "FORLOOP", "FORPREP",
      "TFORLOOP", "SETLIST", "CLOSE", "CLOSURE", "VARARG"]


def rk(f, regs, x):
    return f["consts"][x - 256] if x >= 256 else regs.get(x)


def calls(f, depth=0, out=None):
    """Yield (depth, func_name, [args]) for each CALL, approximately."""
    out = [] if out is None else out
    regs = {}
    for ins in f["code"]:
        op = OP[ins & 0x3F]
        a = (ins >> 6) & 0xFF
        c = (ins >> 14) & 0x1FF
        b = (ins >> 23) & 0x1FF
        bx = (ins >> 14)
        if op == "LOADK":
            regs[a] = f["consts"][bx]
        elif op == "GETGLOBAL":
            regs[a] = ("G", f["consts"][bx])
        elif op == "MOVE":
            regs[a] = regs.get(b)
        elif op == "GETTABLE":
            base, key = regs.get(b), rk(f, regs, c)
            name = base[1] if isinstance(base, tuple) else "?"
            regs[a] = ("G", f"{name}.{key}")
        elif op == "LOADNIL":
            for i in range(a, b + 1):
                regs[i] = None
        elif op == "LOADBOOL":
            regs[a] = bool(b)
        elif op in ("ADD", "SUB"):
            x, y = rk(f, regs, b), rk(f, regs, c)
            regs[a] = (x + y if op == "ADD" else x - y) if isinstance(x, (int, float)) and isinstance(y, (int, float)) \
                else ("E", f"{fmt(x)}{'+' if op == 'ADD' else '-'}{fmt(y)}")
        elif op == "SELF":
            regs[a + 1] = regs.get(b)
            regs[a] = ("G", f"{fmt(regs.get(b))}:{rk(f, regs, c)}")
        elif op == "CLOSURE":
            regs[a] = ("F", bx)
        elif op == "CALL":
            fn = regs.get(a)
            nargs = (b - 1) if b else 0
            args = [regs.get(a + 1 + i) for i in range(nargs)]
            out.append((depth, fmt(fn), args))
            regs[a] = ("R", fmt(fn))
    for p in f["protos"]:
        calls(p, depth + 1, out)
    return out


def run_globals(f):
    """Execute a straight-line main chunk that only builds constant tables
    (NEWTABLE/SETTABLE/SETLIST/SETGLOBAL); return its globals."""
    regs, g = {}, {}
    for ins in f["code"]:
        op = OP[ins & 0x3F]
        a, c, b, bx = (ins >> 6) & 0xFF, (ins >> 14) & 0x1FF, (ins >> 23) & 0x1FF, ins >> 14
        if op == "LOADK":
            regs[a] = f["consts"][bx]
        elif op == "NEWTABLE":
            regs[a] = {}
        elif op == "SETTABLE":
            if isinstance(regs.get(a), dict):
                regs[a][rk(f, regs, b)] = rk(f, regs, c)
        elif op == "SETLIST":
            t = regs.get(a)
            if isinstance(t, dict):
                base = ((c or 1) - 1) * 50
                for i in range(1, (b or 0) + 1):
                    t[base + i] = regs.get(a + i)
        elif op == "SETGLOBAL":
            g[f["consts"][bx]] = regs.get(a)
        elif op == "GETGLOBAL":
            regs[a] = g.get(f["consts"][bx])
        elif op == "MOVE":
            regs[a] = regs.get(b)
        elif op == "GETTABLE":
            t = regs.get(b)
            regs[a] = t.get(rk(f, regs, c)) if isinstance(t, dict) else None
        elif op == "LOADBOOL":
            regs[a] = bool(b)
    return g


def fmt(v):
    if isinstance(v, tuple):
        return str(v[1])
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return repr(v)


def main():
    f = load(open(sys.argv[1], "rb").read())
    for depth, fn, args in calls(f):
        print("  " * depth + fn + "(" + ", ".join(fmt(x) for x in args) + ")")


if __name__ == "__main__":
    main()

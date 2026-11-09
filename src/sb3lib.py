"""Tiny Scratch 3 (.sb3) builder: write scripts as nested Python calls, get real Scratch blocks."""
import json, hashlib, zipfile, itertools

_ids = itertools.count()
def nid(p="b"):
    return f"{p}{next(_ids)}"

def fmt(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)

class Var:
    def __init__(self, name): self.name = name

class Blk:
    def __init__(self, opcode, inputs=None, fields=None, mutation=None):
        self.opcode, self.inputs, self.fields, self.mutation = opcode, inputs or {}, fields or {}, mutation
        self.note = None

def note(text, block):
    """Attach a Scratch comment to a statement block."""
    block.note = text
    return block

COMMENT_W = 470
def _comment_h(text):
    lines = sum(max(1, -(-len(l) // 62)) for l in text.split("\n"))
    return 44 + 17 * lines

C1 = {"control_if", "control_repeat", "control_forever", "control_repeat_until"}
HATS = {"event_whenflagclicked": 80, "event_whenbroadcastreceived": 80, "control_start_as_clone": 80,
        "procedures_definition": 104}

class Def:
    """Custom block definition (no arguments). warp=True == 'run without screen refresh'."""
    def __init__(self, name, warp=True): self.name, self.warp = name, warp

class Project:
    def __init__(self):
        self.stage_vars, self.stage_lists, self.broadcasts = {}, {}, {}
        self.targets, self.assets, self.monitors = [], {}, []
    def bcast_id(self, name):
        if name not in self.broadcasts: self.broadcasts[name] = nid("bc")
        return self.broadcasts[name]
    def asset(self, data, ext):
        md5 = hashlib.md5(data).hexdigest()
        self.assets[f"{md5}.{ext}"] = data
        return md5
    def save(self, path):
        stage = self.targets[0]
        stage.json["variables"] = {i: [n, v] for n, (i, v) in self.stage_vars.items()}
        stage.json["lists"] = {i: [n, v] for n, (i, v) in self.stage_lists.items()}
        stage.json["broadcasts"] = {i: n for n, i in self.broadcasts.items()}
        proj = {"targets": [t.finish() for t in self.targets], "monitors": self.monitors,
                "extensions": ["pen"], "meta": {"semver": "3.0.0", "vm": "2.3.0", "agent": "sb3lib"}}
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("project.json", json.dumps(proj))
            for name, data in self.assets.items(): z.writestr(name, data)
        return proj

class Target:
    def __init__(self, proj, name, is_stage=False, **props):
        self.proj, self.name, self.is_stage = proj, name, is_stage
        self.vars, self.lists, self.blocks, self.comments = {}, {}, {}, {}
        self.costumes, self.sounds = [], []
        self.script_y = 0
        self.json = {"isStage": is_stage, "name": name, "currentCostume": 0, "volume": 100,
                     "layerOrder": props.pop("layer", 0)}
        if is_stage:
            self.json.update({"tempo": 60, "videoTransparency": 50, "videoState": "on",
                              "textToSpeechLanguage": None})
        else:
            self.json.update({"visible": True, "x": 0, "y": 0, "size": 100, "direction": 90,
                              "draggable": False, "rotationStyle": "all around"})
        self.json.update(props)
        proj.targets.append(self)

    # ---- data ----
    def var(self, name, value=0):
        tbl = self.proj.stage_vars if self.is_stage else self.vars
        tbl[name] = (nid("v"), value); return tbl[name][0]
    def lst(self, name, items=None):
        tbl = self.proj.stage_lists if self.is_stage else self.lists
        tbl[name] = (nid("l"), list(items or [])); return tbl[name][0]
    def var_id(self, name):
        if name in self.vars: return self.vars[name][0]
        if name in self.proj.stage_vars: return self.proj.stage_vars[name][0]
        raise KeyError(f"{self.name}: unknown variable {name}")
    def list_id(self, name):
        if name in self.lists: return self.lists[name][0]
        if name in self.proj.stage_lists: return self.proj.stage_lists[name][0]
        raise KeyError(f"{self.name}: unknown list {name}")

    # ---- assets ----
    def costume(self, name, svg, cx, cy):
        md5 = self.proj.asset(svg.encode(), "svg")
        self.costumes.append({"assetId": md5, "name": name, "md5ext": f"{md5}.svg", "dataFormat": "svg",
                              "bitmapResolution": 1, "rotationCenterX": cx, "rotationCenterY": cy})
    def sound(self, name, wav, rate, count):
        md5 = self.proj.asset(wav, "wav")
        self.sounds.append({"assetId": md5, "name": name, "dataFormat": "wav", "format": "", "rate": rate,
                            "sampleCount": count, "md5ext": f"{md5}.wav"})

    # ---- compiler ----
    def field(self, f):
        if isinstance(f, tuple):
            kind, n = f
            if kind == "var": return [n, self.var_id(n)]
            if kind == "list": return [n, self.list_id(n)]
            if kind == "bc": return [n, self.proj.bcast_id(n)]
        return [f, None]

    def inp(self, spec, parent):
        kind = spec[0]
        if kind in ("n", "t"):
            val, st = spec[1], (4 if kind == "n" else 10)
            dflt = "0" if kind == "n" else ""
            if isinstance(val, Var): return [3, [12, val.name, self.var_id(val.name)], [st, dflt]]
            if isinstance(val, Blk): return [3, self.blk(val, parent), [st, dflt]]
            return [1, [st, fmt(val)]]
        if kind == "b":
            return None if spec[1] is None else [2, self.blk(spec[1], parent)]
        if kind == "s":
            first = self.seq(spec[1], parent)
            return None if first is None else [2, first]
        if kind == "m":
            _, mop, fname, value, plug = spec
            mid = nid()
            self.blocks[mid] = {"opcode": mop, "next": None, "parent": parent, "inputs": {},
                                "fields": {fname: [value, None]}, "shadow": True, "topLevel": False}
            if plug is not None: return [3, self.blk(plug, parent), mid]
            return [1, mid]
        if kind == "c": return [1, [9, spec[1]]]
        if kind == "bc": return [1, [11, spec[1], self.proj.bcast_id(spec[1])]]
        raise ValueError(kind)

    def blk(self, b, parent):
        bid = nid()
        d = {"opcode": b.opcode, "next": None, "parent": parent, "inputs": {}, "fields": {},
             "shadow": False, "topLevel": False}
        self.blocks[bid] = d
        if b.mutation: d["mutation"] = b.mutation
        if b.note: self._notes.append((bid, b.note))
        for k, spec in b.inputs.items():
            r = self.inp(spec, bid)
            if r is not None: d["inputs"][k] = r
        for k, f in b.fields.items(): d["fields"][k] = self.field(f)
        return bid

    def seq(self, stmts, parent):
        first = prev = None
        for st in stmts:
            if st is None: continue
            bid = self.blk(st, prev or parent)
            if prev: self.blocks[prev]["next"] = bid
            else: first = bid
            prev = bid
        return first

    # ---- layout estimate (workspace units) so comments sit beside the blocks they describe ----
    def _sub(self, bid, key):
        v = self.blocks[bid]["inputs"].get(key)
        return v[1] if v and v[0] == 2 else None

    def _chain_h(self, first):
        h, b = 0, first
        while b:
            h += self._h(b); b = self.blocks[b]["next"]
        return h or 24

    def _h(self, bid):
        op = self.blocks[bid]["opcode"]
        if op in HATS: return HATS[op]
        if op in C1: return 52 + self._chain_h(self._sub(bid, "SUBSTACK")) + 32
        if op == "control_if_else":
            return 52 + self._chain_h(self._sub(bid, "SUBSTACK")) + 44 + self._chain_h(self._sub(bid, "SUBSTACK2")) + 32
        return 50

    def _positions(self, first, y, out):
        b = first
        while b:
            out[b] = y
            op = self.blocks[b]["opcode"]
            if op in C1 or op == "control_if_else":
                s1 = self._sub(b, "SUBSTACK")
                if s1: self._positions(s1, y + 52, out)
                if op == "control_if_else":
                    s2 = self._sub(b, "SUBSTACK2")
                    if s2: self._positions(s2, y + 52 + self._chain_h(s1) + 44, out)
            y += self._h(b)
            b = self.blocks[b]["next"]
        return y

    def workspace_comment(self, text, x, y, width=COMMENT_W, height=None):
        cid = nid("c")
        self.comments[cid] = {"blockId": None, "x": x, "y": y, "width": width,
                              "height": height or _comment_h(text) * COMMENT_W // width, "minimized": False,
                              "text": text}

    def script(self, *stmts, comment=None, x=None):
        stmts = list(stmts)
        x = 0 if x is None else x
        self._notes = []
        if isinstance(stmts[0], Def):
            d = stmts.pop(0)
            did, pid = nid(), nid()
            self.blocks[did] = {"opcode": "procedures_definition", "next": None, "parent": None,
                                "inputs": {"custom_block": [1, pid]}, "fields": {}, "shadow": False,
                                "topLevel": True, "x": x, "y": self.script_y}
            self.blocks[pid] = {"opcode": "procedures_prototype", "next": None, "parent": did, "inputs": {},
                                "fields": {}, "shadow": True, "topLevel": False,
                                "mutation": {"tagName": "mutation", "children": [], "proccode": d.name,
                                             "argumentids": "[]", "argumentnames": "[]",
                                             "argumentdefaults": "[]", "warp": "true" if d.warp else "false"}}
            first = self.seq(stmts, did)
            self.blocks[did]["next"] = first
            head = did
        else:
            head = self.seq(stmts, None)
            self.blocks[head].update({"topLevel": True, "x": x, "y": self.script_y})
        pos = {}
        bottom_blocks = self._positions(head, self.script_y, pos)
        notes = ([(head, comment)] if comment else []) + sorted(self._notes, key=lambda n: pos.get(n[0], 0))
        bottom = self.script_y - 10000
        for bid, text in notes:
            cy = max(pos.get(bid, self.script_y), bottom + 14)
            h = _comment_h(text)
            cid = nid("c")
            self.blocks[bid]["comment"] = cid
            self.comments[cid] = {"blockId": bid, "x": x - COMMENT_W - 40, "y": cy, "width": COMMENT_W,
                                  "height": h, "minimized": False, "text": text}
            bottom = cy + h
        self.script_y = max(bottom_blocks, bottom) + 140
        return head

    def _count(self, bid):
        n, seen, stack = 0, set(), [bid]
        while stack:
            b = stack.pop()
            if b in seen or b not in self.blocks: continue
            seen.add(b)
            blk = self.blocks[b]
            if blk.get("shadow"): continue
            if blk["opcode"].startswith(("operator_", "data_itemoflist", "sensing_keypressed",
                                         "data_lengthoflist", "sensing_timer")):
                continue
            n += 1
            if blk["next"]: stack.append(blk["next"])
            for v in blk["inputs"].values():
                if v[0] == 2 and isinstance(v[1], str): stack.append(v[1])
        return n

    def finish(self):
        j = self.json
        if not self.is_stage:
            j["variables"] = {i: [n, v] for n, (i, v) in self.vars.items()}
            j["lists"] = {i: [n, v] for n, (i, v) in self.lists.items()}
            j["broadcasts"] = {}
        j.update({"blocks": self.blocks, "comments": self.comments, "costumes": self.costumes,
                  "sounds": self.sounds})
        return j

# ---------------- block helpers ----------------
V = Var
def num(v): return ("n", v)
def txt(v): return ("t", v)
B = Blk
def _bin(op, a, b): return B(op, {"NUM1": num(a), "NUM2": num(b)})
def add(a, b): return _bin("operator_add", a, b)
def sub(a, b): return _bin("operator_subtract", a, b)
def mul(a, b): return _bin("operator_multiply", a, b)
def div(a, b): return _bin("operator_divide", a, b)
def mod(a, b): return _bin("operator_mod", a, b)
def lt(a, b): return B("operator_lt", {"OPERAND1": txt(a), "OPERAND2": txt(b)})
def gt(a, b): return B("operator_gt", {"OPERAND1": txt(a), "OPERAND2": txt(b)})
def eq(a, b): return B("operator_equals", {"OPERAND1": txt(a), "OPERAND2": txt(b)})
def and_(a, b): return B("operator_and", {"OPERAND1": ("b", a), "OPERAND2": ("b", b)})
def or_(a, b): return B("operator_or", {"OPERAND1": ("b", a), "OPERAND2": ("b", b)})
def not_(a): return B("operator_not", {"OPERAND": ("b", a)})
def mop(op, x): return B("operator_mathop", {"NUM": num(x)}, {"OPERATOR": op})
def floor_(x): return mop("floor", x)
def abs_(x): return mop("abs", x)
def sqrt_(x): return mop("sqrt", x)
def sin_(x): return mop("sin", x)
def cos_(x): return mop("cos", x)
def round_(x): return B("operator_round", {"NUM": num(x)})
def rnd(a, b): return B("operator_random", {"FROM": num(a), "TO": num(b)})
def join(a, b): return B("operator_join", {"STRING1": txt(a), "STRING2": txt(b)})
def letter(i, s): return B("operator_letter_of", {"LETTER": num(i), "STRING": txt(s)})
def item(i, l): return B("data_itemoflist", {"INDEX": num(i)}, {"LIST": ("list", l)})
def length(l): return B("data_lengthoflist", {}, {"LIST": ("list", l)})
def setv(n, v): return B("data_setvariableto", {"VALUE": txt(v)}, {"VARIABLE": ("var", n)})
def chg(n, v): return B("data_changevariableby", {"VALUE": num(v)}, {"VARIABLE": ("var", n)})
def clear_list(l): return B("data_deletealloflist", {}, {"LIST": ("list", l)})
def addto(l, v): return B("data_addtolist", {"ITEM": txt(v)}, {"LIST": ("list", l)})
def replace(l, i, v): return B("data_replaceitemoflist", {"INDEX": num(i), "ITEM": txt(v)}, {"LIST": ("list", l)})
def if_(c, *body): return B("control_if", {"CONDITION": ("b", c), "SUBSTACK": ("s", list(body))})
def ifelse(c, a, b): return B("control_if_else", {"CONDITION": ("b", c), "SUBSTACK": ("s", a), "SUBSTACK2": ("s", b)})
def forever(*body): return B("control_forever", {"SUBSTACK": ("s", list(body))})
def repeat(n, *body): return B("control_repeat", {"TIMES": num(n), "SUBSTACK": ("s", list(body))})
def until(c, *body): return B("control_repeat_until", {"CONDITION": ("b", c), "SUBSTACK": ("s", list(body))})
def wait(t): return B("control_wait", {"DURATION": num(t)})
def wait_until(c): return B("control_wait_until", {"CONDITION": ("b", c)})
def stop_all(): return B("control_stop", {}, {"STOP_OPTION": "all"}, {"tagName": "mutation", "children": [], "hasnext": "false"})
def stop_script(): return B("control_stop", {}, {"STOP_OPTION": "this script"}, {"tagName": "mutation", "children": [], "hasnext": "false"})
def key(k): return B("sensing_keypressed", {"KEY_OPTION": ("m", "sensing_keyoptions", "KEY_OPTION", k, None)})
def timer(): return B("sensing_timer")
def flag(): return B("event_whenflagclicked")
def recv(n): return B("event_whenbroadcastreceived", {}, {"BROADCAST_OPTION": ("bc", n)})
def bcast(n): return B("event_broadcast", {"BROADCAST_INPUT": ("bc", n)})
def bcastw(n): return B("event_broadcastandwait", {"BROADCAST_INPUT": ("bc", n)})
def gotoxy(x, y): return B("motion_gotoxy", {"X": num(x), "Y": num(y)})
def show(): return B("looks_show")
def hide(): return B("looks_hide")
def costume(name, plug=None): return B("looks_switchcostumeto", {"COSTUME": ("m", "looks_costume", "COSTUME", name, plug)})
def setsize(s): return B("looks_setsizeto", {"SIZE": num(s)})
def front(): return B("looks_gotofrontback", {}, {"FRONT_BACK": "front"})
def backward(n): return B("looks_goforwardbackwardlayers", {"NUM": num(n)}, {"FORWARD_BACKWARD": "backward"})
def seteffect(e, v): return B("looks_seteffectto", {"VALUE": num(v)}, {"EFFECT": e})
def cleareffects(): return B("looks_cleargraphiceffects")
def play(s): return B("sound_play", {"SOUND_MENU": ("m", "sound_sounds_menu", "SOUND_MENU", s, None)})
def clone(): return B("control_create_clone_of", {"CLONE_OPTION": ("m", "control_create_clone_of_menu", "CLONE_OPTION", "_myself_", None)})
def as_clone(): return B("control_start_as_clone")
def pen_clear(): return B("pen_clear")
def pd(): return B("pen_penDown")
def pu(): return B("pen_penUp")
def pen_size(s): return B("pen_setPenSizeTo", {"SIZE": num(s)})
def pen_color(hexc): return B("pen_setPenColorToColor", {"COLOR": ("c", hexc)})
def pen_param(p, v): return B("pen_setPenColorParamTo", {"COLOR_PARAM": ("m", "pen_menu_colorParam", "colorParam", p, None), "VALUE": num(v)})
def call(name): return B("procedures_call", {}, {}, {"tagName": "mutation", "children": [], "proccode": name, "argumentids": "[]", "warp": "true"})
def line(x0, y0, x1, y1): return [gotoxy(x0, y0), pd(), gotoxy(x1, y1), pu()]
def dot(x, y): return [gotoxy(x, y), pd(), pu()]

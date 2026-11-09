"""Tiny Scratch 3 (.sb3) builder: write scripts as nested Python calls, get real Scratch blocks.

HOW IT WORKS
A Scratch project file (.sb3) is a zip holding project.json (every sprite, variable and block)
plus the costume pictures and sounds. In project.json each block is an entry with an ID, its
"opcode" (which block it is, like "motion_gotoxy"), its inputs (the slots you type in or drop
reporters into), its fields (drop-down menus), and the IDs of the block above and below it.

Here a script is written as nested Python calls, for example
    if_(gt(V("health"), 0), setv("health", 0))
Each helper at the bottom of this file returns a Block object. Target.script() then turns the
nested Block objects into project.json entries (the "compiler" section), and estimates where
each block will sit on screen so comments can be placed beside the blocks they explain.
"""
import json, hashlib, zipfile, itertools

# One counter for the whole project, so every ID is unique: "b0", "b1", "v2", "c3"...
_id_counter = itertools.count()
def new_id(prefix="b"):
    return f"{prefix}{next(_id_counter)}"

def format_value(value):
    """A value as Scratch stores it in a typed-in slot: true/false, and 3 instead of 3.0."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)

class Var:
    """A variable reporter (the round orange block), used inside other blocks: V("health")."""
    def __init__(self, name): self.name = name

class Block:
    """One block before it is compiled: its opcode, inputs, fields and an optional mutation
    (extra settings some blocks need, like a custom block's name)."""
    def __init__(self, opcode, inputs=None, fields=None, mutation=None):
        self.opcode, self.inputs, self.fields, self.mutation = opcode, inputs or {}, fields or {}, mutation
        self.note = None

def note(text, block):
    """Attach a Scratch comment to a statement block."""
    block.note = text
    return block

COMMENT_WIDTH = 470
def _comment_height(text):
    """Roughly how tall a comment box must be to show its text (about 62 characters a line)."""
    line_count = sum(max(1, -(-len(text_line) // 62)) for text_line in text.split("\n"))
    return 44 + 17 * line_count

# Blocks shaped like a C with one gap for other blocks, and the height of each kind of hat block.
C_SHAPED_BLOCKS = {"control_if", "control_repeat", "control_forever", "control_repeat_until"}
HAT_HEIGHTS = {"event_whenflagclicked": 80, "event_whenbroadcastreceived": 80, "control_start_as_clone": 80,
               "procedures_definition": 104}

class Def:
    """Custom block definition (no arguments). warp=True == 'run without screen refresh'."""
    def __init__(self, name, warp=True): self.name, self.warp = name, warp

class Project:
    def __init__(self):
        self.stage_vars, self.stage_lists, self.broadcasts = {}, {}, {}
        self.targets, self.assets, self.monitors = [], {}, []

    def bcast_id(self, name):
        if name not in self.broadcasts: self.broadcasts[name] = new_id("bc")
        return self.broadcasts[name]

    def asset(self, data, extension):
        """Store a picture or sound. Its file name is its MD5 fingerprint, as Scratch expects."""
        md5 = hashlib.md5(data).hexdigest()
        self.assets[f"{md5}.{extension}"] = data
        return md5

    def save(self, path):
        stage = self.targets[0]
        stage.json["variables"] = {variable_id: [name, value] for name, (variable_id, value) in self.stage_vars.items()}
        stage.json["lists"] = {list_id: [name, items] for name, (list_id, items) in self.stage_lists.items()}
        stage.json["broadcasts"] = {broadcast_id: name for name, broadcast_id in self.broadcasts.items()}
        project_json = {"targets": [target.finish() for target in self.targets], "monitors": self.monitors,
                        "extensions": ["pen"], "meta": {"semver": "3.0.0", "vm": "2.3.0", "agent": "sb3lib"}}
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as project_zip:
            project_zip.writestr("project.json", json.dumps(project_json))
            for name, data in self.assets.items(): project_zip.writestr(name, data)
        return project_json

class Target:
    """A sprite, or the stage (is_stage=True)."""
    def __init__(self, project, name, is_stage=False, **properties):
        self.project, self.name, self.is_stage = project, name, is_stage
        self.vars, self.lists, self.blocks, self.comments = {}, {}, {}, {}
        self.costumes, self.sounds = [], []
        self.script_y = 0
        self.json = {"isStage": is_stage, "name": name, "currentCostume": 0, "volume": 100,
                     "layerOrder": properties.pop("layer", 0)}
        if is_stage:
            self.json.update({"tempo": 60, "videoTransparency": 50, "videoState": "on",
                              "textToSpeechLanguage": None})
        else:
            self.json.update({"visible": True, "x": 0, "y": 0, "size": 100, "direction": 90,
                              "draggable": False, "rotationStyle": "all around"})
        self.json.update(properties)
        project.targets.append(self)

    # ---- data ----
    def var(self, name, value=0):
        """Make a variable: for all sprites if this is the stage, otherwise for this sprite only."""
        table = self.project.stage_vars if self.is_stage else self.vars
        table[name] = (new_id("v"), value); return table[name][0]
    def lst(self, name, items=None):
        """Make a list (for all sprites if this is the stage)."""
        table = self.project.stage_lists if self.is_stage else self.lists
        table[name] = (new_id("l"), list(items or [])); return table[name][0]
    def var_id(self, name):
        if name in self.vars: return self.vars[name][0]
        if name in self.project.stage_vars: return self.project.stage_vars[name][0]
        raise KeyError(f"{self.name}: unknown variable {name}")
    def list_id(self, name):
        if name in self.lists: return self.lists[name][0]
        if name in self.project.stage_lists: return self.project.stage_lists[name][0]
        raise KeyError(f"{self.name}: unknown list {name}")

    # ---- assets ----
    def costume(self, name, svg, center_x, center_y):
        md5 = self.project.asset(svg.encode(), "svg")
        self.costumes.append({"assetId": md5, "name": name, "md5ext": f"{md5}.svg", "dataFormat": "svg",
                              "bitmapResolution": 1, "rotationCenterX": center_x, "rotationCenterY": center_y})
    def sound(self, name, wav, rate, count):
        md5 = self.project.asset(wav, "wav")
        self.sounds.append({"assetId": md5, "name": name, "dataFormat": "wav", "format": "", "rate": rate,
                            "sampleCount": count, "md5ext": f"{md5}.wav"})

    # ---- compiler: Block objects -> project.json entries ----
    def field(self, field_value):
        """A drop-down field. Variables, lists and broadcasts also need their ID."""
        if isinstance(field_value, tuple):
            kind, name = field_value
            if kind == "var": return [name, self.var_id(name)]
            if kind == "list": return [name, self.list_id(name)]
            if kind == "bc": return [name, self.project.bcast_id(name)]
        return [field_value, None]

    def compile_input(self, spec, parent_id):
        """One input slot. spec[0] says what kind of slot it is:
        "n" number, "t" text, "b" boolean (hexagon), "s" a stack of blocks (inside a C block),
        "m" a menu (like the costume menu), "c" a color, "bc" a broadcast."""
        kind = spec[0]
        if kind in ("n", "t"):
            value, shadow_type = spec[1], (4 if kind == "n" else 10)
            default_value = "0" if kind == "n" else ""
            if isinstance(value, Var): return [3, [12, value.name, self.var_id(value.name)], [shadow_type, default_value]]
            if isinstance(value, Block): return [3, self.compile_block(value, parent_id), [shadow_type, default_value]]
            return [1, [shadow_type, format_value(value)]]
        if kind == "b":
            return None if spec[1] is None else [2, self.compile_block(spec[1], parent_id)]
        if kind == "s":
            first_id = self.compile_stack(spec[1], parent_id)
            return None if first_id is None else [2, first_id]
        if kind == "m":
            _, menu_opcode, field_name, value, plug = spec
            menu_id = new_id()
            self.blocks[menu_id] = {"opcode": menu_opcode, "next": None, "parent": parent_id, "inputs": {},
                                    "fields": {field_name: [value, None]}, "shadow": True, "topLevel": False}
            if plug is not None: return [3, self.compile_block(plug, parent_id), menu_id]
            return [1, menu_id]
        if kind == "c": return [1, [9, spec[1]]]
        if kind == "bc": return [1, [11, spec[1], self.project.bcast_id(spec[1])]]
        raise ValueError(kind)

    def compile_block(self, block, parent_id):
        block_id = new_id()
        entry = {"opcode": block.opcode, "next": None, "parent": parent_id, "inputs": {}, "fields": {},
                 "shadow": False, "topLevel": False}
        self.blocks[block_id] = entry
        if block.mutation: entry["mutation"] = block.mutation
        if block.note: self._notes.append((block_id, block.note))
        for input_name, spec in block.inputs.items():
            compiled = self.compile_input(spec, block_id)
            if compiled is not None: entry["inputs"][input_name] = compiled
        for field_name, field_value in block.fields.items(): entry["fields"][field_name] = self.field(field_value)
        return block_id

    def compile_stack(self, statements, parent_id):
        """Blocks stacked one under the other. Returns the ID of the top one."""
        first_id = previous_id = None
        for statement in statements:
            if statement is None: continue
            block_id = self.compile_block(statement, previous_id or parent_id)
            if previous_id: self.blocks[previous_id]["next"] = block_id
            else: first_id = block_id
            previous_id = block_id
        return first_id

    # ---- layout estimate (workspace units) so comments sit beside the blocks they describe ----
    def _inner_stack(self, block_id, input_name):
        """The first block inside a C block's gap (SUBSTACK, or SUBSTACK2 for 'else')."""
        compiled = self.blocks[block_id]["inputs"].get(input_name)
        return compiled[1] if compiled and compiled[0] == 2 else None

    def _stack_height(self, first_id):
        height, block_id = 0, first_id
        while block_id:
            height += self._block_height(block_id); block_id = self.blocks[block_id]["next"]
        return height or 24

    def _block_height(self, block_id):
        opcode = self.blocks[block_id]["opcode"]
        if opcode in HAT_HEIGHTS: return HAT_HEIGHTS[opcode]
        if opcode in C_SHAPED_BLOCKS: return 52 + self._stack_height(self._inner_stack(block_id, "SUBSTACK")) + 32
        if opcode == "control_if_else":
            return (52 + self._stack_height(self._inner_stack(block_id, "SUBSTACK")) + 44
                    + self._stack_height(self._inner_stack(block_id, "SUBSTACK2")) + 32)
        return 50

    def _positions(self, first_id, y, positions):
        """Fill positions[block_id] = estimated y of every block in a stack. Returns the y below it."""
        block_id = first_id
        while block_id:
            positions[block_id] = y
            opcode = self.blocks[block_id]["opcode"]
            if opcode in C_SHAPED_BLOCKS or opcode == "control_if_else":
                first_inside = self._inner_stack(block_id, "SUBSTACK")
                if first_inside: self._positions(first_inside, y + 52, positions)
                if opcode == "control_if_else":
                    first_in_else = self._inner_stack(block_id, "SUBSTACK2")
                    if first_in_else:
                        self._positions(first_in_else, y + 52 + self._stack_height(first_inside) + 44, positions)
            y += self._block_height(block_id)
            block_id = self.blocks[block_id]["next"]
        return y

    def workspace_comment(self, text, canvas_x, canvas_y, width=COMMENT_WIDTH, height=None):
        """A comment that floats on its own (not attached to a block), like the Stage guide."""
        comment_id = new_id("c")
        self.comments[comment_id] = {"blockId": None, "x": canvas_x, "y": canvas_y, "width": width,
                                     "height": height or _comment_height(text) * COMMENT_WIDTH // width,
                                     "minimized": False, "text": text}

    def script(self, *statements, comment=None, canvas_x=None):
        """Add one script: a hat block (or Def(...) for a custom block) and the blocks under it.
        comment = a header comment for the whole script. Scripts are stacked down the page;
        canvas_x moves a script to the right in the code area (0 = the default column)."""
        statements = list(statements)
        canvas_x = 0 if canvas_x is None else canvas_x
        self._notes = []
        if isinstance(statements[0], Def):
            definition = statements.pop(0)
            definition_id, prototype_id = new_id(), new_id()
            self.blocks[definition_id] = {"opcode": "procedures_definition", "next": None, "parent": None,
                                          "inputs": {"custom_block": [1, prototype_id]}, "fields": {},
                                          "shadow": False, "topLevel": True, "x": canvas_x, "y": self.script_y}
            self.blocks[prototype_id] = {
                "opcode": "procedures_prototype", "next": None, "parent": definition_id, "inputs": {},
                "fields": {}, "shadow": True, "topLevel": False,
                "mutation": {"tagName": "mutation", "children": [], "proccode": definition.name,
                             "argumentids": "[]", "argumentnames": "[]",
                             "argumentdefaults": "[]", "warp": "true" if definition.warp else "false"}}
            first_id = self.compile_stack(statements, definition_id)
            self.blocks[definition_id]["next"] = first_id
            head_id = definition_id
        else:
            head_id = self.compile_stack(statements, None)
            self.blocks[head_id].update({"topLevel": True, "x": canvas_x, "y": self.script_y})
        positions = {}
        blocks_bottom = self._positions(head_id, self.script_y, positions)
        notes = ([(head_id, comment)] if comment else []) + sorted(self._notes, key=lambda note_entry: positions.get(note_entry[0], 0))
        # Place the comments down the left of the script, each one level with its block,
        # pushed down if it would overlap the comment above it.
        comments_bottom = self.script_y - 10000
        for block_id, text in notes:
            comment_y = max(positions.get(block_id, self.script_y), comments_bottom + 14)
            height = _comment_height(text)
            comment_id = new_id("c")
            self.blocks[block_id]["comment"] = comment_id
            self.comments[comment_id] = {"blockId": block_id, "x": canvas_x - COMMENT_WIDTH - 40, "y": comment_y,
                                         "width": COMMENT_WIDTH, "height": height, "minimized": False, "text": text}
            comments_bottom = comment_y + height
        self.script_y = max(blocks_bottom, comments_bottom) + 140
        return head_id

    def finish(self):
        """This target's entry in project.json."""
        target_json = self.json
        if not self.is_stage:
            target_json["variables"] = {variable_id: [name, value] for name, (variable_id, value) in self.vars.items()}
            target_json["lists"] = {list_id: [name, items] for name, (list_id, items) in self.lists.items()}
            target_json["broadcasts"] = {}
        target_json.update({"blocks": self.blocks, "comments": self.comments, "costumes": self.costumes,
                            "sounds": self.sounds})
        return target_json

# ---------------- block helpers ----------------
# Each returns a Block. In the input specs: num(...) = a number slot, txt(...) = a text slot,
# ("b", ...) = a hexagon slot, ("s", [...]) = the blocks inside a C block, ("m", ...) = a menu.
V = Var
def num(value): return ("n", value)
def txt(value): return ("t", value)
def _two_numbers(opcode, first, second): return Block(opcode, {"NUM1": num(first), "NUM2": num(second)})
def add(first, second): return _two_numbers("operator_add", first, second)
def sub(first, second): return _two_numbers("operator_subtract", first, second)
def mul(first, second): return _two_numbers("operator_multiply", first, second)
def div(first, second): return _two_numbers("operator_divide", first, second)
def mod(first, second): return _two_numbers("operator_mod", first, second)
def lt(first, second): return Block("operator_lt", {"OPERAND1": txt(first), "OPERAND2": txt(second)})
def gt(first, second): return Block("operator_gt", {"OPERAND1": txt(first), "OPERAND2": txt(second)})
def eq(first, second): return Block("operator_equals", {"OPERAND1": txt(first), "OPERAND2": txt(second)})
def and_(first, second): return Block("operator_and", {"OPERAND1": ("b", first), "OPERAND2": ("b", second)})
def or_(first, second): return Block("operator_or", {"OPERAND1": ("b", first), "OPERAND2": ("b", second)})
def not_(condition): return Block("operator_not", {"OPERAND": ("b", condition)})
def math_op(operation, value): return Block("operator_mathop", {"NUM": num(value)}, {"OPERATOR": operation})
def floor_(value): return math_op("floor", value)
def abs_(value): return math_op("abs", value)
def sqrt_(value): return math_op("sqrt", value)
def sin_(value): return math_op("sin", value)
def cos_(value): return math_op("cos", value)
def round_(value): return Block("operator_round", {"NUM": num(value)})
def rnd(low, high): return Block("operator_random", {"FROM": num(low), "TO": num(high)})
def join(first, second): return Block("operator_join", {"STRING1": txt(first), "STRING2": txt(second)})
def letter(position, text): return Block("operator_letter_of", {"LETTER": num(position), "STRING": txt(text)})
def item(index, list_name): return Block("data_itemoflist", {"INDEX": num(index)}, {"LIST": ("list", list_name)})
def length(list_name): return Block("data_lengthoflist", {}, {"LIST": ("list", list_name)})
def setv(name, value): return Block("data_setvariableto", {"VALUE": txt(value)}, {"VARIABLE": ("var", name)})
def chg(name, value): return Block("data_changevariableby", {"VALUE": num(value)}, {"VARIABLE": ("var", name)})
def clear_list(list_name): return Block("data_deletealloflist", {}, {"LIST": ("list", list_name)})
def addto(list_name, value): return Block("data_addtolist", {"ITEM": txt(value)}, {"LIST": ("list", list_name)})
def replace(list_name, index, value):
    return Block("data_replaceitemoflist", {"INDEX": num(index), "ITEM": txt(value)}, {"LIST": ("list", list_name)})
def if_(condition, *body): return Block("control_if", {"CONDITION": ("b", condition), "SUBSTACK": ("s", list(body))})
def ifelse(condition, if_body, else_body):
    return Block("control_if_else", {"CONDITION": ("b", condition), "SUBSTACK": ("s", if_body), "SUBSTACK2": ("s", else_body)})
def forever(*body): return Block("control_forever", {"SUBSTACK": ("s", list(body))})
def repeat(times, *body): return Block("control_repeat", {"TIMES": num(times), "SUBSTACK": ("s", list(body))})
def until(condition, *body): return Block("control_repeat_until", {"CONDITION": ("b", condition), "SUBSTACK": ("s", list(body))})
def wait(seconds): return Block("control_wait", {"DURATION": num(seconds)})
def wait_until(condition): return Block("control_wait_until", {"CONDITION": ("b", condition)})
def stop_all(): return Block("control_stop", {}, {"STOP_OPTION": "all"}, {"tagName": "mutation", "children": [], "hasnext": "false"})
def stop_script():
    return Block("control_stop", {}, {"STOP_OPTION": "this script"},
                 {"tagName": "mutation", "children": [], "hasnext": "false"})
def key(key_name): return Block("sensing_keypressed", {"KEY_OPTION": ("m", "sensing_keyoptions", "KEY_OPTION", key_name, None)})
def timer(): return Block("sensing_timer")
def flag(): return Block("event_whenflagclicked")
def recv(name): return Block("event_whenbroadcastreceived", {}, {"BROADCAST_OPTION": ("bc", name)})
def bcast(name): return Block("event_broadcast", {"BROADCAST_INPUT": ("bc", name)})
def bcastw(name): return Block("event_broadcastandwait", {"BROADCAST_INPUT": ("bc", name)})
def gotoxy(stage_x, stage_y): return Block("motion_gotoxy", {"X": num(stage_x), "Y": num(stage_y)})
def show(): return Block("looks_show")
def hide(): return Block("looks_hide")
def costume(name, plug=None): return Block("looks_switchcostumeto", {"COSTUME": ("m", "looks_costume", "COSTUME", name, plug)})
def setsize(size): return Block("looks_setsizeto", {"SIZE": num(size)})
def front(): return Block("looks_gotofrontback", {}, {"FRONT_BACK": "front"})
def backward(layers): return Block("looks_goforwardbackwardlayers", {"NUM": num(layers)}, {"FORWARD_BACKWARD": "backward"})
def seteffect(effect, value): return Block("looks_seteffectto", {"VALUE": num(value)}, {"EFFECT": effect})
def cleareffects(): return Block("looks_cleargraphiceffects")
def play(sound_name): return Block("sound_play", {"SOUND_MENU": ("m", "sound_sounds_menu", "SOUND_MENU", sound_name, None)})
def clone(): return Block("control_create_clone_of", {"CLONE_OPTION": ("m", "control_create_clone_of_menu", "CLONE_OPTION", "_myself_", None)})
def as_clone(): return Block("control_start_as_clone")
def pen_clear(): return Block("pen_clear")
def pen_down(): return Block("pen_penDown")
def pen_up(): return Block("pen_penUp")
def pen_size(size): return Block("pen_setPenSizeTo", {"SIZE": num(size)})
def pen_color(hex_color): return Block("pen_setPenColorToColor", {"COLOR": ("c", hex_color)})
def pen_param(parameter, value):
    return Block("pen_setPenColorParamTo", {"COLOR_PARAM": ("m", "pen_menu_colorParam", "colorParam", parameter, None),
                                           "VALUE": num(value)})
def call(name, warp=True):
    """Use a custom block. warp must match its Def(...): True = 'run without screen refresh'."""
    return Block("procedures_call", {}, {}, {"tagName": "mutation", "children": [], "proccode": name,
                                             "argumentids": "[]", "warp": "true" if warp else "false"})
def line(start_x, start_y, end_x, end_y): return [gotoxy(start_x, start_y), pen_down(), gotoxy(end_x, end_y), pen_up()]
def dot(stage_x, stage_y): return [gotoxy(stage_x, stage_y), pen_down(), pen_up()]

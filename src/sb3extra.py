from sb3lib import *
from sb3lib import B

def strlen(s): return B("operator_length", {"STRING": txt(s)})
def delete_clone(): return B("control_delete_this_clone")
def itemnum(v, l): return B("data_itemnumoflist", {"ITEM": txt(v)}, {"LIST": ("list", l)})
def show_list(l): return B("data_showlist", {}, {"LIST": ("list", l)})
def hide_list(l): return B("data_hidelist", {}, {"LIST": ("list", l)})
def stop_script(): return B("control_stop", {}, {"STOP_OPTION": "this script"},
                            {"tagName": "mutation", "children": [], "hasnext": "false"})
def call(name, warp=True):
    return B("procedures_call", {}, {}, {"tagName": "mutation", "children": [], "proccode": name,
                                         "argumentids": "[]", "warp": "true" if warp else "false"})
def joins(*parts):
    """join(a, join(b, join(c, ...))) — Scratch's join only takes two pieces."""
    out = parts[-1]
    for p in reversed(parts[:-1]):
        out = join(p, out)
    return out
def set_sound_effect(effect, value):
    return B("sound_seteffectto", {"VALUE": num(value)}, {"EFFECT": effect})
def backdrop(name): return B("looks_switchbackdropto", {"BACKDROP": ("m", "looks_backdrops", "BACKDROP", name, None)})
def stop_sounds(): return B("sound_stopallsounds")
def play_until_done(s): return B("sound_playuntildone", {"SOUND_MENU": ("m", "sound_sounds_menu", "SOUND_MENU", s, None)})
def go_back(): return B("looks_gotofrontback", {}, {"FRONT_BACK": "back"})
def go_forward(n): return B("looks_goforwardbackwardlayers", {"NUM": num(n)}, {"FORWARD_BACKWARD": "forward"})
def change_effect(effect, v): return B("looks_changeeffectby", {"CHANGE": num(v)}, {"EFFECT": effect})
def change_size(v): return B("looks_changesizeby", {"CHANGE": num(v)})
def change_x(v): return B("motion_changexby", {"DX": num(v)})
def change_y(v): return B("motion_changeyby", {"DY": num(v)})
def set_x(v): return B("motion_setx", {"X": num(v)})
def set_y(v): return B("motion_sety", {"Y": num(v)})
def xpos(): return B("motion_xposition")
def ypos(): return B("motion_yposition")
def mouse_x(): return B("sensing_mousex")
def mouse_y(): return B("sensing_mousey")
def mouse_down(): return B("sensing_mousedown")
def tan_(x): return B("operator_mathop", {"NUM": num(x)}, {"OPERATOR": "tan"})
def set_volume(v): return B("sound_setvolumeto", {"VOLUME": num(v)})
def play_named(default, plug):
    """play sound (whose name is worked out by a reporter block, e.g. join)."""
    return B("sound_play", {"SOUND_MENU": ("m", "sound_sounds_menu", "SOUND_MENU", default, plug)})
def play_until_done_named(default, plug):
    return B("sound_playuntildone", {"SOUND_MENU": ("m", "sound_sounds_menu", "SOUND_MENU", default, plug)})

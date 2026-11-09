"""More block helpers, on top of sb3lib: text length, clones, list monitors, sounds, backdrops,
layers, motion, the mouse and tan. every part of the game (src/game/) imports everything from here (and sb3lib with it)."""
from sb3lib import *
from sb3lib import Block

def strlen(text): return Block("operator_length", {"STRING": txt(text)})
def delete_clone(): return Block("control_delete_this_clone")
def itemnum(value, list_name): return Block("data_itemnumoflist", {"ITEM": txt(value)}, {"LIST": ("list", list_name)})
def show_list(list_name): return Block("data_showlist", {}, {"LIST": ("list", list_name)})
def hide_list(list_name): return Block("data_hidelist", {}, {"LIST": ("list", list_name)})
def joins(*parts):
    """join(a, join(b, join(c, ...))) — Scratch's join only takes two pieces."""
    joined = parts[-1]
    for part in reversed(parts[:-1]):
        joined = join(part, joined)
    return joined
def set_sound_effect(effect, value):
    return Block("sound_seteffectto", {"VALUE": num(value)}, {"EFFECT": effect})
def backdrop(name): return Block("looks_switchbackdropto", {"BACKDROP": ("m", "looks_backdrops", "BACKDROP", name, None)})
def stop_sounds(): return Block("sound_stopallsounds")
def play_until_done(sound_name):
    return Block("sound_playuntildone", {"SOUND_MENU": ("m", "sound_sounds_menu", "SOUND_MENU", sound_name, None)})
def go_back(): return Block("looks_gotofrontback", {}, {"FRONT_BACK": "back"})
def go_forward(layers): return Block("looks_goforwardbackwardlayers", {"NUM": num(layers)}, {"FORWARD_BACKWARD": "forward"})
def change_effect(effect, amount): return Block("looks_changeeffectby", {"CHANGE": num(amount)}, {"EFFECT": effect})
def change_size(amount): return Block("looks_changesizeby", {"CHANGE": num(amount)})
def change_x(amount): return Block("motion_changexby", {"DX": num(amount)})
def change_y(amount): return Block("motion_changeyby", {"DY": num(amount)})
def set_x(stage_x): return Block("motion_setx", {"X": num(stage_x)})
def set_y(stage_y): return Block("motion_sety", {"Y": num(stage_y)})
def xpos(): return Block("motion_xposition")
def ypos(): return Block("motion_yposition")
def mouse_x(): return Block("sensing_mousex")
def mouse_y(): return Block("sensing_mousey")
def mouse_down(): return Block("sensing_mousedown")
def tan_(angle): return Block("operator_mathop", {"NUM": num(angle)}, {"OPERATOR": "tan"})
def set_volume(volume): return Block("sound_setvolumeto", {"VOLUME": num(volume)})
def play_named(default, plug):
    """play sound (whose name is worked out by a reporter block, e.g. join)."""
    return Block("sound_play", {"SOUND_MENU": ("m", "sound_sounds_menu", "SOUND_MENU", default, plug)})
def play_until_done_named(default, plug):
    return Block("sound_playuntildone", {"SOUND_MENU": ("m", "sound_sounds_menu", "SOUND_MENU", default, plug)})

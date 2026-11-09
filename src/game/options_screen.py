"""The options menu's sprites: the panel and its knobs, switches and words."""
from sb3extra import *
from game.config import *
import pictures.options_menu
from game.stage import project

options_up = eq(V("options open"), 1)
options_panel = Target(project, "Options Panel", layer=23, visible=False)
options_panel.costume("options title", pictures.options_menu.OPTIONS_TITLE, 240, 180)
options_panel.costume("options paused", pictures.options_menu.OPTIONS_PAUSED, 240, 180)
options_panel.script(flag(), gotoxy(0, 0), hide())
options_panel.script(recv(DRAW_OPTIONS_PANEL),
          ifelse(options_up,
                 [ifelse(eq(V("options from game"), 1), [costume("options paused")], [costume("options title")]),
                  show(), front()],
                 [hide()]),
          comment="OPTIONS PANEL: the box, the labels and the slider tracks. From the\n"
                  "game it says PAUSED and the level select is switched off.")

ROW_Y = pictures.options_menu.OPTION_ROW_Y
TRACK_LEFT, TRACK_RIGHT = pictures.options_menu.TRACK_LEFT, pictures.options_menu.TRACK_RIGHT
options_widgets = Target(project, "Options Widgets", layer=24, visible=False)
options_widgets.costume("row highlight", pictures.options_menu.ROW_HIGHLIGHT, 190, 13)
options_widgets.costume("knob", pictures.options_menu.KNOB, 10, 10)
options_widgets.costume("switch on", pictures.options_menu.TOGGLE_ON, 28, 11)
options_widgets.costume("switch off", pictures.options_menu.TOGGLE_OFF, 28, 11)
for difficulty_name in pictures.options_menu.DIFFICULTY_COLORS:
    options_widgets.costume(f"difficulty {difficulty_name}", pictures.options_menu.difficulty_word(difficulty_name), 50, 11)
for name in ["is clone", "widget role"]:
    options_widgets.var(name)
options_widgets.script(flag(), hide(), setv("is clone", 0), setv("widget role", 0), repeat(7, chg("widget role", 1), clone()),
          comment="Seven clones, one per 'widget role':\n"
                  "1 the highlight on the chosen row, 2 turn speed knob,\n"
                  "3 mouse steering switch, 4 sensitivity knob, 5 field of view knob,\n6 music switch, "
                  "7 the difficulty word.")
options_widgets.script(as_clone(), setv("is clone", 1))

def knob_at(setting, low, high, stage_y):
    """Slide the knob along the track: (setting - low) / (high - low) of the way across."""
    return [costume("knob"), gotoxy(add(TRACK_LEFT, mul(TRACK_RIGHT - TRACK_LEFT, div(sub(V(setting), low), high - low))), stage_y)]

def switch_at(setting, stage_y):
    return [ifelse(eq(V(setting), 1), [costume("switch on")], [costume("switch off")]), gotoxy(40, stage_y)]

options_widgets.script(recv(DRAW_OPTIONS_HIGHLIGHT), if_(eq(V("widget role"), 1),
    ifelse(options_up,
           [costume("row highlight"), gotoxy(0, sub(ROW_Y[0], mul(sub(V("options row"), 1), pictures.options_menu.OPTION_ROW_STEP))),
            show(), front()],
           [hide()])),
    comment="DRAW OPTIONS HIGHLIGHT: the see-through box on the chosen row.\n"
            "It has its own broadcast, sent BEFORE 'draw options widgets', so it\n"
            "always goes to the front first and the knobs, switches and words end\n"
            "up on top of it. Why not in the widgets script? Scratch runs a sprite's\n"
            "clones in their layer order, so clones that all 'go to front' swap\n"
            "places every frame, and the box would cover the words every other\n"
            "frame (a flicker).")

options_widgets.script(recv(DRAW_OPTIONS_WIDGETS), if_(and_(eq(V("is clone"), 1), gt(V("widget role"), 1)),
    ifelse(options_up,
           [if_(eq(V("widget role"), 2), *knob_at("turn speed", 1, 10, ROW_Y[0])),
            if_(eq(V("widget role"), 3), *switch_at("mouse steering", ROW_Y[1])),
            if_(eq(V("widget role"), 4), *knob_at("mouse sensitivity", 1, 10, ROW_Y[2])),
            if_(eq(V("widget role"), 5), *knob_at("field of view", MIN_FOV, MAX_FOV, ROW_Y[3])),
            if_(eq(V("widget role"), 6), *switch_at("music is on", ROW_Y[4])),
            if_(eq(V("widget role"), 7),
                note("The difficulty word: costume 'difficulty easy', 'difficulty normal'\n"
                     "or 'difficulty hard', picked by name from the 'difficulty names' list.",
                     costume("difficulty normal", join("difficulty ", item(V("difficulty"), "difficulty names")))),
                gotoxy(sum(pictures.options_menu.DIFFICULTY_ARROWS_X) / 2, ROW_Y[5]),
                note("Paused during a game, difficulty can't change, so the word is faded.",
                     ifelse(eq(V("options from game"), 1), [seteffect("GHOST", 50)], [seteffect("GHOST", 0)]))),
            show(), front()],
           [hide()])),
    comment="DRAW OPTIONS WIDGETS: each clone shows its own setting.")

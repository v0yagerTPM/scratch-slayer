"""The options menu's logic: reading the keys and mouse, changing settings."""
from sb3extra import *
from game.config import *
import pictures.options_menu
from game.engine.sprite import engine

ROW_Y, ROW_STEP = pictures.options_menu.OPTION_ROW_Y, pictures.options_menu.OPTION_ROW_STEP
OPTION_ROW_COUNT = len(ROW_Y)   # 7. The last two rows (difficulty, start level) are title-screen only.
TRACK_LEFT, TRACK_RIGHT = pictures.options_menu.TRACK_LEFT, pictures.options_menu.TRACK_RIGHT
DIFFICULTY_MIDDLE_X = sum(pictures.options_menu.DIFFICULTY_ARROWS_X) / 2
LEVEL_MIDDLE_X = sum(pictures.options_menu.LEVEL_ARROWS_X) / 2
def clamp(var, low, high):
    return [if_(lt(V(var), low), setv(var, low)), if_(gt(V(var), high), setv(var, high))]

engine.script(Def("options menu", warp=False),
    note("OPEN: remember which screen was showing (the title, or the game if\n"
         "you pressed P), and wait until you let go of the key that opened it.",
         setv("screen before options", V("screen showing"))),
    ifelse(eq(V("screen showing"), NONE), [setv("options from game", 1)], [setv("options from game", 0)]),
    setv("options open", 1), setv("screen showing", OPTIONS), setv("options row", 1),
    setv("mouse was down", 1), setv("change repeat timer", 0), play("menu click"),
    wait_until(not_(or_(key("o"), key("p")))),
    note("ONE MENU FRAME per pass: read the keys and mouse, then redraw.\n"
         "Plain broadcasts run in the order they're sent: panel, then the\n"
         "highlight on the chosen row, then the sliders and switches on top,\n"
         "then the numbers on top of those.",
         until(eq(V("options open"), 0),
               call("handle options input"), call("copy numbers to HUD"),
               bcast(DRAW_OPTIONS_PANEL), bcast(DRAW_OPTIONS_HIGHLIGHT), bcast(DRAW_OPTIONS_WIDGETS),
               bcast(DRAW_NUMBERS))),
    note("CLOSE: wait for the key to be let go (so the game doesn't pause again\n"
         "straight away), put the old screen back and hide the menu.",
         wait_until(not_(or_(key("o"), key("p"))))),
    setv("screen showing", V("screen before options")), play("menu click"),
    bcast(DRAW_OPTIONS_PANEL), bcast(DRAW_OPTIONS_HIGHLIGHT), bcast(DRAW_OPTIONS_WIDGETS), bcast(DRAW_NUMBERS),
    call("update camera"),
    note("Restart the level clock's frame timing, so time spent paused\n"
         "doesn't count toward your level time.",
         setv("time at last frame", timer())),
    comment="OPTIONS MENU: O on the title screen, P during the game.\n"
            "Runs one menu frame per screen refresh until you close it.")

engine.script(Def("handle options input"),
    note("CLOSE with O or P.",
         if_(or_(key("o"), key("p")), setv("options open", 0))),
    setv("last options row", V("options row")),
    note("UP / DOWN (or W / S) pick a row, once per key press. From the game\n"
         "the last two rows (difficulty, start level) can't be picked.",
         ifelse(or_(key("up arrow"), key("w")),
                [if_(eq(V("up key was held"), 0), chg("options row", -1)), setv("up key was held", 1)],
                [setv("up key was held", 0)])),
    ifelse(or_(key("down arrow"), key("s")),
           [if_(eq(V("down key was held"), 0), chg("options row", 1)), setv("down key was held", 1)],
           [setv("down key was held", 0)]),
    if_(lt(V("options row"), 1), setv("options row", 1)),
    if_(gt(V("options row"), sub(OPTION_ROW_COUNT, mul(2, V("options from game")))),
        setv("options row", sub(OPTION_ROW_COUNT, mul(2, V("options from game"))))),
    note("LEFT / RIGHT (or A / D) change the value. Holding the key repeats the\n"
         "change every 5 frames, like a keyboard does.",
         setv("change direction", 0)),
    if_(or_(key("left arrow"), key("a")), setv("change direction", -1)),
    if_(or_(key("right arrow"), key("d")), setv("change direction", 1)),
    ifelse(eq(V("change direction"), 0), [setv("change repeat timer", 0)],
           [ifelse(gt(V("change repeat timer"), 0), [chg("change repeat timer", -1), setv("change direction", 0)],
                   [setv("change repeat timer", 5)])]),
    if_(not_(eq(V("change direction"), 0)),
        note("Row 1 turn speed, 2 mouse steering (on/off), 3 mouse sensitivity,\n"
             "4 field of view (2 degrees a step), 5 music (on/off), 6 difficulty,\n"
             "7 start level.",
             if_(eq(V("options row"), 1), chg("turn speed", V("change direction")))),
        if_(eq(V("options row"), 2), setv("mouse steering", sub(1, V("mouse steering")))),
        if_(eq(V("options row"), 3), chg("mouse sensitivity", V("change direction"))),
        if_(eq(V("options row"), 4), chg("field of view", mul(2, V("change direction")))),
        if_(eq(V("options row"), 5), setv("music is on", sub(1, V("music is on"))), bcast(APPLY_MUSIC)),
        if_(eq(V("options row"), 6), chg("difficulty", V("change direction"))),
        if_(eq(V("options row"), 7), chg("start level choice", V("change direction"))),
        play("menu click")),
    note("MOUSE: hold the button down on a row to pick it. On a slider, the\n"
         "knob jumps to the mouse (so you can drag it). A click on a switch\n"
         "flips it; on the difficulty and level rows, left half = down,\n"
         f"right half = up. Rows are {ROW_STEP} pixels apart.",
         ifelse(mouse_down(),
                [setv("mouse row", add(round_(div(sub(ROW_Y[0], mouse_y()), ROW_STEP)), 1)),
                 if_(and_(and_(gt(V("mouse row"), 0),
                               lt(V("mouse row"), sub(OPTION_ROW_COUNT + 1, mul(2, V("options from game"))))),
                          lt(abs_(sub(mouse_y(), sub(ROW_Y[0], mul(sub(V("mouse row"), 1), ROW_STEP)))), 13)),
                     setv("options row", V("mouse row")),
                     setv("slider fraction", div(sub(mouse_x(), TRACK_LEFT), TRACK_RIGHT - TRACK_LEFT)),
                     if_(lt(V("slider fraction"), 0), setv("slider fraction", 0)),
                     if_(gt(V("slider fraction"), 1), setv("slider fraction", 1)),
                     if_(gt(mouse_x(), TRACK_LEFT - 15),
                         if_(eq(V("mouse row"), 1), setv("turn speed", add(1, round_(mul(9, V("slider fraction")))))),
                         if_(eq(V("mouse row"), 3), setv("mouse sensitivity", add(1, round_(mul(9, V("slider fraction")))))),
                         if_(eq(V("mouse row"), 4), setv("field of view", add(MIN_FOV, mul(2, round_(mul((MAX_FOV - MIN_FOV) / 2, V("slider fraction")))))))),
                     if_(eq(V("mouse was down"), 0),
                         if_(eq(V("mouse row"), 2), setv("mouse steering", sub(1, V("mouse steering")))),
                         if_(eq(V("mouse row"), 5), setv("music is on", sub(1, V("music is on"))), bcast(APPLY_MUSIC)),
                         if_(eq(V("mouse row"), 6),
                             ifelse(lt(mouse_x(), DIFFICULTY_MIDDLE_X), [chg("difficulty", -1)], [chg("difficulty", 1)])),
                         if_(eq(V("mouse row"), 7),
                             ifelse(lt(mouse_x(), LEVEL_MIDDLE_X), [chg("start level choice", -1)],
                                    [chg("start level choice", 1)])),
                         play("menu click"))),
                 setv("mouse was down", 1)],
                [setv("mouse was down", 0)])),
    note("Keep every setting inside its range.",
         *clamp("turn speed", 1, 10)[:1]), *clamp("turn speed", 1, 10)[1:],
    *clamp("mouse sensitivity", 1, 10), *clamp("field of view", MIN_FOV, MAX_FOV),
    if_(lt(V("difficulty"), 1), setv("difficulty", 1)),
    if_(gt(V("difficulty"), length("difficulty names")), setv("difficulty", length("difficulty names"))),
    if_(lt(V("start level choice"), 1), setv("start level choice", 1)),
    if_(gt(V("start level choice"), V("highest level reached")), setv("start level choice", V("highest level reached"))),
    if_(not_(eq(V("options row"), V("last options row"))), play("menu click")),
    comment="HANDLE OPTIONS INPUT: one frame of the options menu.")

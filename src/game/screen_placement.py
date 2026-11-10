"""Helpers shared by monsters, items, barrels and projectiles: how far away the player
is, where something appears on screen, and which explosions are close."""
from sb3extra import *
from game.config import *
from game.stage import HUD_SLOTS

# How many layers the HUD takes at the front: the Weapon, Crosshair, HUD, Arms Panel, Boss Bar,
# Message and Screens sprites, plus the Digits sprite and its 3 clones per number slot.
HUD_LAYERS = 8 + HUD_SLOTS * 3

def offset_from_player(x_var, y_var):
    return [setv("offset x from player", sub(V(x_var), V("player x"))),
            setv("offset y from player", sub(V(y_var), V("player y"))),
            setv("distance to player", sqrt_(add(mul(V("offset x from player"), V("offset x from player")),
                                                 mul(V("offset y from player"), V("offset y from player")))))]

def place_on_screen(when_visible, what, size=None, height=-180):
    """size = sprite size at depth 1 (default 225%); height = screen y at depth 1 (-180 = the floor)."""
    size = size if size is not None else 225
    return [
        note(f"PLACE ON SCREEN: turn the {what}'s map position into camera\n"
             "coordinates. 'sideways in view' = how far left/right of the\n"
             "crosshair, 'depth in view' = how far in front of you.",
             setv("sideways in view", mul(V("projection factor"),
                                           sub(mul(V("look direction y"), V("offset x from player")),
                                               mul(V("look direction x"), V("offset y from player")))))),
        setv("depth in view", mul(V("projection factor"),
                                  add(mul(sub(0, V("camera plane y")), V("offset x from player")),
                                      mul(V("camera plane x"), V("offset y from player"))))),
        note("Behind you (or right on top of you)? Then hide.",
             ifelse(gt(V("depth in view"), 0.4),
                    [note("Perspective: divide sideways by depth to get the screen x, then\n"
                          "find which wall column that x is in.",
                          setv("screen x", mul(240, div(V("sideways in view"), V("depth in view"))))),
                     setv("screen column index", floor_(div(add(V("screen x"), 240), STRIPE_WIDTH))),
                     note("Hide if off the screen, or if the wall in that column is closer\n"
                          "than we are (we're behind a wall).",
                          ifelse(or_(or_(lt(V("screen column index"), 0), gt(V("screen column index"), RAY_COUNT - 1)),
                                     lt(item(add(V("screen column index"), 1), "wall distance per column"),
                                        V("depth in view"))),
                                 [hide()],
                                 [note("Visible: farther = smaller and closer to the horizon. Layers:\n"
                                       "go to front, then back by 2 x depth, so near things cover far ones.\n"
                                       f"Also back past the {HUD_LAYERS} layers of the HUD (weapon, boss bar,\n"
                                       "numbers...), so the world can never cover the HUD, even in a frame\n"
                                       "where the HUD went to the front first.",
                                       setsize(div(size, V("depth in view")))),
                                  gotoxy(V("screen x"), div(height, V("depth in view"))), show(),
                                  front(), backward(add(HUD_LAYERS, round_(mul(V("depth in view"), 2)))),
                                  *when_visible]))],
                    [hide()]))]

def explosion_scan(x_var, y_var, *for_each_close_blast):
    """Loop over this frame's explosions; for each one, measure 'distance to blast' and run the blocks."""
    return [setv("explosion number", 1),
            repeat(length("explosion x"),
                   setv("distance to blast", sqrt_(add(
                       mul(sub(item(V("explosion number"), "explosion x"), V(x_var)),
                           sub(item(V("explosion number"), "explosion x"), V(x_var))),
                       mul(sub(item(V("explosion number"), "explosion y"), V(y_var)),
                           sub(item(V("explosion number"), "explosion y"), V(y_var)))))),
                   *for_each_close_blast, chg("explosion number", 1))]

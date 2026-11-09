"""The raycaster: drawing the 3D view with the pen, one stripe per screen column."""
from sb3extra import *
from game.config import *
from game.engine.sprite import engine

ceiling = [
    note("CEILING: 6 wide horizontal pen lines from the top of the screen down\n"
         "to the middle. Each band is a little brighter, which fakes depth.",
         setv("shading band number", 0)),
    pen_color("#ff0000"), pen_param("color", V("ceiling hue")),
    pen_param("saturation", V("ceiling saturation")), pen_size(31),
    repeat(6, pen_param("brightness", add(10, mul(V("shading band number"), 2))),
           *line(-240, sub(165, mul(V("shading band number"), 30)), 240, sub(165, mul(V("shading band number"), 30))),
           chg("shading band number", 1))]
floor_bands = [
    note("FLOOR: the same trick from the middle down, getting brighter toward\nyour feet.",
         setv("shading band number", 0)),
    pen_color("#ff0000"), pen_param("color", V("floor hue")), pen_param("saturation", V("floor saturation")),
    repeat(6, pen_param("brightness", add(14, mul(V("shading band number"), 6))),
           *line(-240, sub(-15, mul(V("shading band number"), 30)), 240, sub(-15, mul(V("shading band number"), 30))),
           chg("shading band number", 1))]

ray = [
    note("RAY DIRECTION: 'ray screen position' goes from -1 (left edge) to +1\n"
         "(right edge). The ray points along the look direction, bent\n"
         "sideways by that much of the camera plane.",
         setv("ray screen position", sub(div(mul(2, V("ray column")), RAY_COUNT), 1))),
    setv("ray direction x", add(V("look direction x"), mul(V("camera plane x"), V("ray screen position")))),
    setv("ray direction y", add(V("look direction y"), mul(V("camera plane y"), V("ray screen position")))),
    note("The ray starts in the square you are standing in.",
         setv("ray square x", floor_(V("player x")))), setv("ray square y", floor_(V("player y"))),
    note("SETUP FOR DDA ('digital differential analysis'):\n"
         "'distance between x lines' = how far the ray travels to cross from\n"
         "one vertical grid line to the next (same idea for y). A huge number\n"
         "stands in for 'never' when the ray runs exactly along an axis.",
         ifelse(lt(abs_(V("ray direction x")), 0.00001), [setv("distance between x lines", 100000)],
                [setv("distance between x lines", abs_(div(1, V("ray direction x"))))])),
    ifelse(lt(abs_(V("ray direction y")), 0.00001), [setv("distance between y lines", 100000)],
           [setv("distance between y lines", abs_(div(1, V("ray direction y"))))]),
    note("'ray step x' is -1 if the ray goes left, +1 if it goes right.\n"
         "'distance to next x line' = distance from you to the FIRST vertical\n"
         "grid line the ray crosses. Same for y.",
         ifelse(lt(V("ray direction x"), 0),
                [setv("ray step x", -1),
                 setv("distance to next x line", mul(sub(V("player x"), V("ray square x")), V("distance between x lines")))],
                [setv("ray step x", 1),
                 setv("distance to next x line", mul(sub(add(V("ray square x"), 1), V("player x")), V("distance between x lines")))])),
    ifelse(lt(V("ray direction y"), 0),
           [setv("ray step y", -1),
            setv("distance to next y line", mul(sub(V("player y"), V("ray square y")), V("distance between y lines")))],
           [setv("ray step y", 1),
            setv("distance to next y line", mul(sub(add(V("ray square y"), 1), V("player y")), V("distance between y lines")))]),
    setv("letter hit", 0), setv("ray steps taken", 0),
    note("DDA LOOP: hop square by square, always crossing whichever grid line\n"
         "is closer, until the square we land in isn't floor (0).\n"
         "Barrels (E) are skipped: they are drawn as sprites, not walls.\n"
         f"'hit side' 0 = hit an east/west face, 1 = a north/south face.\n"
         "Stop after 'max ray steps' steps (set per level): very far walls are\n"
         "black anyway, and big levels stay fast.",
         until(or_(and_(not_(eq(V("letter hit"), 0)), not_(eq(V("letter hit"), "E"))),
                   gt(V("ray steps taken"), V("max ray steps"))),
               ifelse(lt(V("distance to next x line"), V("distance to next y line")),
                      [chg("distance to next x line", V("distance between x lines")), chg("ray square x", V("ray step x")),
                       setv("hit side", 0)],
                      [chg("distance to next y line", V("distance between y lines")), chg("ray square y", V("ray step y")),
                       setv("hit side", 1)]),
               setv("letter hit", map_letter_at(V("ray square x"), V("ray square y"))), chg("ray steps taken", 1))),
    note("WALL DISTANCE: undo the last hop to get the distance to the wall.\n"
         "This is measured straight ahead (not along the ray), which stops\n"
         "the 'fish-eye' bulge you'd get otherwise.",
         ifelse(eq(V("hit side"), 0), [setv("wall distance", sub(V("distance to next x line"), V("distance between x lines")))],
                [setv("wall distance", sub(V("distance to next y line"), V("distance between y lines")))])),
    if_(lt(V("wall distance"), 0.05), setv("wall distance", 0.05)),
    note("Save the distance for this column. Monsters and items read it to\nknow if a wall is in front of them.",
         replace("wall distance per column", add(V("ray column"), 1), V("wall distance"))),
    note("STRIPE HEIGHT: a wall twice as far away looks half as tall.",
         setv("wall stripe height", div(360, V("wall distance")))),
    if_(gt(V("wall stripe height"), 720), setv("wall stripe height", 720)),
    note("SPOT ALONG WALL (0 to 1): exactly where on the wall's face the ray hit.\n"
         "Used to draw the dark seams between wall panels, door frames and\n"
         "the switch.",
         ifelse(eq(V("hit side"), 0),
                [setv("spot along wall", add(V("player y"), mul(V("wall distance"), V("ray direction y"))))],
                [setv("spot along wall", add(V("player x"), mul(V("wall distance"), V("ray direction x"))))])),
    setv("spot along wall", sub(V("spot along wall"), floor_(V("spot along wall")))),
    note("WALL COLOR: find the letter in 'wall letters', then use the same item\n"
         "number in 'wall hues', 'wall saturations', 'wall brightnesses'.\n"
         "Farther = darker. North/south faces are darker too, which makes\n"
         "corners easy to see.",
         setv("wall type number", itemnum(V("letter hit"), "wall letters"))),
    setv("wall style", item(V("wall type number"), "wall styles")),
    note("SECRET WALLS (style 4) borrow the colors of the wall digit named in\n"
         "'level secret wall looks' for this level. Their style stays 4, so\n"
         "they get no seams: that's the clue for sharp-eyed players.",
         if_(eq(V("wall style"), 4),
             setv("wall type number", itemnum(item(V("current level"), "level secret wall looks"), "wall letters")))),
    pen_color("#ff0000"),
    pen_param("color", item(V("wall type number"), "wall hues")),
    pen_param("saturation", item(V("wall type number"), "wall saturations")),
    setv("stripe brightness", sub(sub(item(V("wall type number"), "wall brightnesses"),
                                      mul(V("wall distance"), V("light falloff"))), mul(V("hit side"), 12))),
    note("Darker edges: thin seams on plain walls (style 0), a thick frame on\ndoors (style 1) and skull doors (style 5).",
         if_(and_(eq(V("wall style"), 0), or_(lt(V("spot along wall"), 0.05), gt(V("spot along wall"), 0.95))),
             chg("stripe brightness", -18))),
    if_(and_(or_(eq(V("wall style"), 1), eq(V("wall style"), 5)),
             or_(lt(V("spot along wall"), 0.1), gt(V("spot along wall"), 0.9))),
        chg("stripe brightness", -28)),
    pen_param("brightness", V("stripe brightness")),
    note("DRAW the stripe: a vertical pen line centered on the horizon.",
         setv("stripe screen x", add(-240 + STRIPE_WIDTH / 2, mul(V("ray column"), STRIPE_WIDTH)))),
    *line(V("stripe screen x"), div(V("wall stripe height"), 2), V("stripe screen x"), div(V("wall stripe height"), -2)),
    note("DOORS (style 1 and 5): draw a darker band across the middle.",
         if_(and_(or_(eq(V("wall style"), 1), eq(V("wall style"), 5)),
                  and_(not_(lt(V("spot along wall"), 0.1)), not_(gt(V("spot along wall"), 0.9)))),
             pen_param("brightness", sub(V("stripe brightness"), 24)),
             *line(V("stripe screen x"), mul(V("wall stripe height"), 0.07),
                   V("stripe screen x"), mul(V("wall stripe height"), -0.07)))),
    note("EXIT SWITCH (style 2 = off, 3 = on): a dark box with a glowing light\n"
         "inside. Hue = (style - 2) x 33, so red (0) when off, green (33) when on.",
         if_(and_(and_(gt(V("wall style"), 1), lt(V("wall style"), 4)),
                  and_(gt(V("spot along wall"), 0.36), lt(V("spot along wall"), 0.64))),
             pen_param("brightness", sub(V("stripe brightness"), 30)),
             *line(V("stripe screen x"), mul(V("wall stripe height"), 0.13),
                   V("stripe screen x"), mul(V("wall stripe height"), -0.13)),
             if_(and_(gt(V("spot along wall"), 0.4), lt(V("spot along wall"), 0.6)),
                 pen_param("color", mul(sub(V("wall style"), 2), 33)), pen_param("saturation", 95),
                 pen_param("brightness", sub(95, mul(V("wall distance"), 3))),
                 *line(V("stripe screen x"), mul(V("wall stripe height"), 0.09),
                       V("stripe screen x"), mul(V("wall stripe height"), -0.09))))),
    note("SKULL DOOR (style 5): two glowing red eyes above the middle band.",
         if_(and_(eq(V("wall style"), 5),
                  or_(and_(gt(V("spot along wall"), 0.3), lt(V("spot along wall"), 0.42)),
                      and_(gt(V("spot along wall"), 0.58), lt(V("spot along wall"), 0.7)))),
             pen_param("color", 0), pen_param("saturation", 95),
             pen_param("brightness", sub(95, mul(V("wall distance"), 3))),
             *line(V("stripe screen x"), mul(V("wall stripe height"), 0.24),
                   V("stripe screen x"), mul(V("wall stripe height"), 0.16)))),
    chg("ray column", 1),
]

SQUARE = V("minimap square size")
minimap = [
    note("MINIMAP: one dot per wall square in the top-left corner, in the wall's\n"
         "own color. 'minimap square size' shrinks the dots for bigger maps.",
         setv("map row", 0)),
    repeat(V("map height"), setv("map column", 0),
           repeat(V("map width"), setv("minimap letter", map_letter_at(V("map column"), V("map row"))),
                  if_(and_(not_(eq(V("minimap letter"), 0)), not_(eq(V("minimap letter"), "E"))),
                      setv("wall type number", itemnum(V("minimap letter"), "wall letters")),
                      if_(eq(V("minimap letter"), "S"),
                          setv("wall type number",
                               itemnum(item(V("current level"), "level secret wall looks"), "wall letters"))),
                      pen_color("#ff0000"), pen_param("color", item(V("wall type number"), "wall hues")),
                      pen_param("saturation", item(V("wall type number"), "wall saturations")),
                      pen_param("brightness", 78),
                      *dot(add(-236, mul(V("map column"), SQUARE)), sub(176, mul(V("map row"), SQUARE)))),
                  chg("map column", 1)),
           chg("map row", 1)),
    note("You: a green dot with two yellow lines showing your field of view.",
         setv("minimap player x", add(-236, mul(sub(V("player x"), 0.5), SQUARE)))),
    setv("minimap player y", sub(176, mul(sub(V("player y"), 0.5), SQUARE))),
    pen_color("#ffe14d"), pen_size(1),
    *line(V("minimap player x"), V("minimap player y"),
          add(V("minimap player x"), mul(add(V("look direction x"), V("camera plane x")), 14)),
          sub(V("minimap player y"), mul(add(V("look direction y"), V("camera plane y")), 14))),
    *line(V("minimap player x"), V("minimap player y"),
          add(V("minimap player x"), mul(sub(V("look direction x"), V("camera plane x")), 14)),
          sub(V("minimap player y"), mul(sub(V("look direction y"), V("camera plane y")), 14))),
    pen_color("#40ff40"), pen_size(5), *dot(V("minimap player x"), V("minimap player y")),
]

engine.script(
    Def("draw 3D view"),
    note("Wipe last frame's drawing.", pen_clear()),
    *ceiling, *floor_bands,
    note(f"WALLS: one ray per screen column, {RAY_COUNT} columns, each stripe\n{STRIPE_WIDTH} pixels wide.",
         setv("ray column", 0)), pen_size(STRIPE_WIDTH + 1),
    repeat(RAY_COUNT, *ray),
    note("SCREEN FLASHES: red when a monster hits you, gold when you pick\nsomething up. One huge see-through dot covers the screen.",
         if_(gt(V("hurt flash timer"), 0),
             pen_color("#ff0000"), pen_param("transparency", 62), pen_size(620), *dot(0, 0),
             chg("hurt flash timer", -1))),
    if_(gt(V("pickup flash timer"), 0),
        pen_color("#ffd23f"), pen_param("transparency", 72), pen_size(620), *dot(0, 0),
        chg("pickup flash timer", -1)),
    if_(eq(V("map is showing"), 1), pen_size(add(SQUARE, 1)), *minimap),
    note("BOSS HEALTH BAR: a dark track, then a red line as long as the boss's\n"
         "health. The Boss Bar sprite draws the frame and name on top.",
         if_(and_(eq(V("boss is awake"), 1), gt(V("boss health"), 0)),
             pen_size(8), pen_color("#300000"), *line(-98, 94, 98, 94),
             pen_color("#e02424"),
             *line(-98, 94, add(-98, mul(196, div(V("boss health"), V("boss max health")))), 94))),
    note("SPRINT BAR (only while playing): a dark track, then the stamina.\n"
         "Green = plenty, yellow = under 30, flashing red/orange = out of\n"
         "breath (the cooldown). The HUD sprite draws the label and outline.",
         if_(eq(V("screen showing"), NONE),
             pen_size(5), pen_color("#151515"), *line(-222, -109, -126, -109),
             ifelse(eq(V("is exhausted"), 1),
                    [ifelse(lt(mod(mul(timer(), 4), 1), 0.5), [pen_color("#ff3020")], [pen_color("#ffa020")])],
                    [ifelse(lt(V("stamina"), 30), [pen_color("#ffd23f")], [pen_color("#40e060")])]),
             if_(gt(V("stamina"), 0.5),
                 *line(-222, -109, add(-222, mul(96, div(V("stamina"), 100))), -109)))),
    comment="DRAW 3D VIEW: the raycaster. Runs WITHOUT screen refresh so the\n"
            "whole picture appears at once.\n"
            "Idea: for each column of the screen, shoot a ray from the player\n"
            "across the map grid until it hits a wall. A closer wall = a taller,\n"
            "brighter stripe. Same technique as Wolfenstein 3D (1992).")

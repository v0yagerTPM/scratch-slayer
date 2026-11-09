"""The camera, walking, sprinting, doors and switches, and the minimap."""
from sb3extra import *
from game.config import *
from game.engine.sprite import engine

engine.script(
    Def("update camera"),
    note("Look direction = which way you face, as an arrow 1 square long:\n"
         "x = cos(angle), y = sin(angle).",
         setv("look direction x", cos_(V("player angle")))), setv("look direction y", sin_(V("player angle"))),
    note("Camera plane = an arrow at right angles to the look direction. It is\n"
         "the 'window' the rays pass through. Its length = tan(field of view / 2):\n"
         "a longer window lets wider rays through. 66 degrees (length 0.66) is\n"
         "about what Wolfenstein 3D used. Change 'field of view' in the options.",
         setv("camera plane length", tan_(div(V("field of view"), 2)))),
    setv("camera plane x", mul(V("look direction y"), mul(-1, V("camera plane length")))),
    setv("camera plane y", mul(V("look direction x"), V("camera plane length"))),
    note("Projection factor: a number the monsters and items use to work out\n"
         "where they appear on screen. It is 1 / (the 'determinant' of the\n"
         "look direction and camera plane).",
         setv("projection factor", div(1, sub(mul(V("camera plane x"), V("look direction y")),
                                              mul(V("look direction x"), V("camera plane y")))))),
    comment="UPDATE CAMERA: works out which way the camera points from\n'player angle'. Runs every frame after turning.")

engine.script(
    Def("move player with collision"),
    note("Try the X part of the step first. 'wall buffer' looks 0.25 squares\n"
         "ahead of you so you stop BEFORE your face touches the wall.",
         setv("next player x", add(V("player x"), V("move amount x")))),
    ifelse(gt(V("move amount x"), 0), [setv("wall buffer", 0.25)], [setv("wall buffer", -0.25)]),
    note("Only move if that square is floor (0).",
         if_(eq(map_letter_at(floor_(add(V("next player x"), V("wall buffer"))), floor_(V("player y"))), 0),
             setv("player x", V("next player x")))),
    note("Then try the Y part on its own. Doing X and Y separately lets you\n"
         "slide along a wall instead of getting stuck on it.",
         setv("next player y", add(V("player y"), V("move amount y")))),
    ifelse(gt(V("move amount y"), 0), [setv("wall buffer", 0.25)], [setv("wall buffer", -0.25)]),
    if_(eq(map_letter_at(floor_(V("player x")), floor_(add(V("next player y"), V("wall buffer")))), 0),
        setv("player y", V("next player y"))),
    comment="MOVE PLAYER WITH COLLISION: moves you by 'move amount x/y'\nunless a wall is in the way.")

engine.script(Def("find facing square"),
         setv("facing square x", floor_(add(V("player x"), mul(V("look direction x"), 0.9)))),
         setv("facing square y", floor_(add(V("player y"), mul(V("look direction y"), 0.9)))),
         setv("facing letter", map_letter_at(V("facing square x"), V("facing square y"))),
         comment="FIND FACING SQUARE: which square is 0.9 squares in front of you,\n"
                 "and what letter is in it? Used for doors and the exit switch.")

engine.script(Def("change map square"),
         note("Get the row, then rebuild it letter by letter.",
              setv("row text", item(add(V("square to change y"), 1), "current map"))),
         setv("new row text", ""), setv("letter position", 1),
         repeat(strlen(V("row text")),
                note("At the square we're changing, use 'new letter'.\nEverywhere else, copy the old letter.",
                     ifelse(eq(V("letter position"), add(V("square to change x"), 1)),
                            [setv("new row text", join(V("new row text"), V("new letter")))],
                            [setv("new row text", join(V("new row text"), letter(V("letter position"), V("row text"))))])),
                chg("letter position", 1)),
         replace("current map", add(V("square to change y"), 1), V("new row text")),
         comment="CHANGE MAP SQUARE: puts 'new letter' at 'square to change x/y'\n"
                 "in 'current map'. Scratch can't change one letter inside a piece\n"
                 "of text, so we rebuild the whole row with the new letter in it.")

engine.script(Def("open door"),
         setv("square to change x", V("facing square x")), setv("square to change y", V("facing square y")),
         setv("new letter", 0), call("change map square"), play("door"),
         comment="OPEN DOOR: replace the door in front of you with floor (0).")

engine.script(
    Def("use door or switch"), call("find facing square"),
    note("D = ordinary door: always opens.",
         if_(eq(V("facing letter"), "D"), call("open door"))),
    note("R = red door: opens with the red key, otherwise show a message.",
         if_(eq(V("facing letter"), "R"), ifelse(eq(V("has red key"), 1), [call("open door")],
             [setv("message name", "need red key"), setv("message timer", 50), play("locked")]))),
    note("B = blue door: same idea with the blue key.",
         if_(eq(V("facing letter"), "B"), ifelse(eq(V("has blue key"), 1), [call("open door")],
             [setv("message name", "need blue key"), setv("message timer", 50), play("locked")]))),
    note("Z = skull door: only the skull key the boss drops opens it.",
         if_(eq(V("facing letter"), "Z"), ifelse(eq(V("has skull key"), 1), [call("open door")],
             [setv("message name", "need skull key"), setv("message timer", 60), play("locked")]))),
    note("S = secret wall: slide it open (turn it into floor), count the secret\n"
         "and celebrate.",
         if_(eq(V("facing letter"), "S"),
             setv("square to change x", V("facing square x")), setv("square to change y", V("facing square y")),
             setv("new letter", 0), call("change map square"), play("secret"), chg("level secrets found", 1),
             setv("message name", "found secret"), setv("message timer", 60))),
    note("X = exit switch: change it to Y (the switch drawn green) and start\n"
         "the 'exit timer'. The main loop ends the level when it runs out.",
         if_(eq(V("facing letter"), "X"),
             setv("square to change x", V("facing square x")), setv("square to change y", V("facing square y")),
             setv("new letter", "Y"), call("change map square"), play("switch"),
             setv("message name", "exit activated"), setv("message timer", 40), setv("exit timer", 20))),
    comment="USE DOOR OR SWITCH: runs when you press E.")

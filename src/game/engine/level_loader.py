"""Loading a level: reading the map list letter by letter, the map checker,
and changing map squares (doors, secrets, barrel wreckage)."""
from sb3extra import *
from game.config import *
from levels import MAP_LETTERS
from game.stage import MAP_LISTS
from game.engine.sprite import engine

def copy_rows_if_picked(name):
    """if map name = "level 1 map A" then copy every row of the list "level 1 map A" into
    'rows to load'. One of these per map."""
    return if_(eq(V("map name"), name), setv("row to copy", 1),
               repeat(length(name), addto("rows to load", item(V("row to copy"), name)), chg("row to copy", 1)))

def thing(letter_code, *blocks):
    return if_(eq(V("map letter"), letter_code), *blocks, setv("map letter", 0))

def item_start(type_number):
    return [addto("item start x", V("map column")), addto("item start y", V("map row")),
            addto("item start type", type_number)]

def problem(*parts):
    return addto("map problems", joins(*parts))

row_number, letter_number = add(V("map row"), 1), add(V("map column"), 1)
on_outside_edge = or_(or_(eq(V("map row"), 0), eq(V("map row"), sub(V("row count"), 1))),
                      or_(eq(V("map column"), 0), eq(V("map column"), sub(V("first row length"), 1))))

engine.script(
    Def("load level"),
    note("1. CLEAR OUT the last level: empty the map and the start lists,\n"
         "and reset the per-level counters, keys and timers.",
         clear_list("current map")), clear_list("monster start x"), clear_list("monster start y"),
    clear_list("item start x"), clear_list("item start y"), clear_list("item start type"),
    clear_list("map problems"), clear_list("monster start type"),
    clear_list("barrel start x"), clear_list("barrel start y"),
    clear_list("new explosion x"), clear_list("new explosion y"), clear_list("explosion x"), clear_list("explosion y"),
    clear_list("squares to clear x"), clear_list("squares to clear y"),
    clear_list("new shot x"), clear_list("new shot y"), clear_list("new shot speed x"),
    clear_list("new shot speed y"), clear_list("new shot damage"), clear_list("new shot look"),
    clear_list("new shot owner"), setv("killer type", 0),
    setv("boss is awake", 0), setv("boss health", 0), setv("level secret count", 0), setv("level secrets found", 0),
    setv("level kills", 0), setv("level items collected", 0), setv("level monster count", 0),
    setv("has red key", 0), setv("has blue key", 0), setv("hurt flash timer", 0), setv("pickup flash timer", 0),
    setv("has skull key", 0), setv("boss is dead", 0), setv("weapon switch timer", 0),
    setv("exit timer", 0), setv("message timer", 0), setv("shot cooldown", 0),
    setv("stamina", 100), setv("is exhausted", 0), setv("is sprinting", 0), setv("speed boost", 1),
    setv("stamina rest timer", 0),
    setv("player starts found", 0), setv("exits found", 0),
    note("2. COPY THE PICKED MAP into 'rows to load'. 'map name' says which map\n"
         "to play (the 'pick map' block chose it). Scratch can't choose a list by\n"
         "its name, so there is one 'if' per map: the one whose list matches 'map\n"
         "name' copies its rows. To add a map, duplicate one 'if' and pick your\n"
         "new list in it (twice: the 'repeat' and the 'item').",
         clear_list("rows to load")),
    *[copy_rows_if_picked(name) for name in MAP_LISTS],
    if_(eq(length("rows to load"), 0),
        problem("There is no map called \"", V("map name"), "\". Make a list with that name, or check its 'if' in 'load level'.")),
    setv("row count", length("rows to load")),
    setv("row text", item(1, "rows to load")),
    setv("first row length", strlen(V("row text"))),
    note("3. READ THE MAP ROW BY ROW. 'map row' counts from 0 (row 0 = item 1).",
         setv("map row", 0)),
    repeat(V("row count"),
           note("Get this row's text.",
                setv("row text", item(add(V("map row"), 1), "rows to load"))),
           note("MAP CHECK: every row must be as long as the first one.",
                if_(not_(eq(strlen(V("row text")), V("first row length"))),
                    problem("Row ", row_number, " has ", strlen(V("row text")), " letters but row 1 has ",
                            V("first row length"), ". Every row must be the same length."))),
           setv("new row text", ""), setv("map column", 0),
           note("4. LOOK AT EACH LETTER in the row, left to right.",
                repeat(strlen(V("row text")),
                       setv("map letter", letter(add(V("map column"), 1), V("row text"))),
                       note("THINGS: P, the monster letters, H, A, K and J are not walls.\n"
                            "Remember where each one is, then turn its square into floor (0).\n"
                            "Player start -> 'player x/y' (the +0.5 puts you in the middle\n"
                            "of the square).",
                            thing("P", setv("player x", add(V("map column"), 0.5)),
                                  setv("player y", add(V("map row"), 0.5)), chg("player starts found", 1))),
                       note("MONSTERS: if the letter is in 'monster letters', its position in\n"
                            "that list is the monster TYPE (1 imp, 2 spitter, 3 golem, 4 warden,\n"
                            "5 charger, 6 wraith, 7 colossus). A BOSS also gets a skull key\n"
                            "(item 5) on its square: it stays hidden until the boss dies.",
                            if_(gt(itemnum(V("map letter"), "monster letters"), 0),
                                addto("monster start x", V("map column")), addto("monster start y", V("map row")),
                                addto("monster start type", itemnum(V("map letter"), "monster letters")),
                                if_(eq(item(itemnum(V("map letter"), "monster letters"), "monster is boss"), 1),
                                    *item_start(5)),
                                chg("level monster count", 1), setv("map letter", 0))),
                       note("Items -> 'item start x/y/type': 1 health, 2 shells, 3 red key,\n"
                            "4 blue key, (5 skull key), 6 bullets, 7 rockets, 8 shotgun,\n"
                            "9 chaingun, 10 rocket launcher.",
                            thing("H", *item_start(1))),
                       thing("A", *item_start(2)),
                       thing("K", *item_start(3)), thing("J", *item_start(4)),
                       *[thing(item_letter, *item_start(item_type)) for item_letter, item_type in (("I", 6), ("U", 7), ("N", 8), ("Q", 9), ("L", 10))],
                       note("BARRELS (E) keep their letter, so they block like a wall until they\n"
                            "explode. SECRET WALLS (S) are counted for the results screen.",
                            if_(eq(V("map letter"), "E"), addto("barrel start x", V("map column")),
                                addto("barrel start y", V("map row")))),
                       if_(eq(V("map letter"), "S"), chg("level secret count", 1)),
                       note("MAP CHECKS for this letter: count exits, spot letters the game\n"
                            "doesn't know, and spot holes in the outside wall.",
                            if_(eq(V("map letter"), "X"), chg("exits found", 1))),
                       if_(and_(and_(not_(eq(V("map letter"), 0)), not_(eq(V("map letter"), "E"))),
                                eq(itemnum(V("map letter"), "wall letters"), 0)),
                           problem("Row ", row_number, ", letter ", letter_number, ": \"", V("map letter"),
                                   "\" is not a letter the game knows.")),
                       if_(and_(eq(V("map letter"), 0), on_outside_edge),
                           problem("Row ", row_number, ", letter ", letter_number,
                                   ": the outside edge must be a wall, not floor or a thing.")),
                       note("Add the (possibly changed) letter to the new row and move right.",
                            setv("new row text", join(V("new row text"), V("map letter")))),
                       chg("map column", 1))),
           note("5. The row is finished: add it to 'current map', move down a row.",
                addto("current map", V("new row text"))),
           chg("map row", 1)),
    note("6. FINAL MAP CHECKS: exactly one player start and at least one exit.\n"
         "If anything went wrong, show the 'map problems' list on the stage.",
         if_(eq(V("player starts found"), 0), problem("No player start. Put one P on the map."))),
    if_(gt(V("player starts found"), 1),
        problem("Found ", V("player starts found"), " player starts (P). There should be only one.")),
    if_(eq(V("exits found"), 0), problem("No exit switch. Put an X in a wall next to floor.")),
    ifelse(gt(length("map problems"), 0), [show_list("map problems")], [hide_list("map problems")]),
    note("7. MAP SETTINGS: map size (for the minimap), start angle and the\n"
         "ceiling/floor colors, all read from item 'map item number' of each\n"
         "\"map ...\" list (this map's place in \"map list names\").",
         setv("level item count", length("item start x"))),
    setv("map width", V("first row length")), setv("map height", length("current map")),
    setv("minimap square size", floor_(div(112, V("map width")))),
    setv("player angle", item(V("map item number"), "map start angles")),
    setv("ceiling hue", item(V("map item number"), "map ceiling hues")),
    setv("ceiling saturation", item(V("map item number"), "map ceiling saturations")),
    setv("floor hue", item(V("map item number"), "map floor hues")),
    setv("floor saturation", item(V("map item number"), "map floor saturations")),
    note("Big maps: rays stop after 'max ray steps' squares (far walls are\n"
         "black anyway), 'light falloff' = how fast walls get darker with\n"
         "distance, 'sprite darkness' = the same for monsters and items.",
         setv("max ray steps", item(V("map item number"), "map max ray steps"))),
    setv("light falloff", item(V("map item number"), "map light falloffs")),
    setv("sprite darkness", item(V("map item number"), "map sprite darkness")),
    comment="LOAD LEVEL: turns the letters of the picked map ('level N map A')\ninto a playable level.\n"
            "The full step-by-step explanation and how to design your own levels\n"
            "is in the comments on the STAGE (click the Stage, then Code).")

# MAP_LETTERS is "ABCDEFGHI": letter 2 of it is B, so map 2 of a level is map B.
engine.script(
    Def("pick map"),
    note("HOW MANY MAPS does this level have? Try map A, B, C ... and stop at\n"
         "the first name that isn't in \"map list names\" ('item # of' gives 0\n"
         "for a name that isn't in the list).",
         setv("level map count", 0)),
    until(eq(itemnum(joins("level ", V("current level"), " map ", letter(add(V("level map count"), 1), MAP_LETTERS)),
                     "map list names"), 0),
          chg("level map count", 1)),
    note("PICK ONE: the map the options menu's MAP setting asks for ('map\n"
         "choice' 1 = A, 2 = B ...) if this level has it. Otherwise (and when\n"
         "the setting is RANDOM, 0) a random one: 'pick random 1 to 3' gives\n"
         "1, 2 or 3, each just as likely.",
         ifelse(and_(gt(V("map choice"), 0), not_(gt(V("map choice"), V("level map count")))),
                [setv("map variant", V("map choice"))],
                [setv("map variant", rnd(1, V("level map count")))])),
    call("use picked map"),
    comment="PICK MAP: each level can have several maps (map A, map B, map C).\n"
            "This picks which one to play. 'load level' then reads it.")

engine.script(
    Def("pick a different map"),
    note("After you die, R asks for a DIFFERENT map. The trick: pick a random\n"
         "number from 1 to (number of maps - 1). If it is the current map or\n"
         "later, add 1. Then every OTHER map is equally likely and the current\n"
         "one can't come up. (With 3 maps and map B playing: 1 -> A, 2 -> C.)",
         if_(gt(V("level map count"), 1),
             setv("other map", rnd(1, sub(V("level map count"), 1))),
             if_(not_(lt(V("other map"), V("map variant"))), chg("other map", 1)),
             setv("map variant", V("other map")))),
    call("use picked map"),
    comment="PICK A DIFFERENT MAP: any of the level's maps except this one.")

engine.script(
    Def("use picked map"),
    note("Work out everything about the picked map: its letter (2 -> B), the\n"
         "name of its list, and which item of the \"map ...\" lists is its own\n"
         "(its place in \"map list names\").",
         setv("map variant letter", letter(V("map variant"), MAP_LETTERS))),
    setv("map name", joins("level ", V("current level"), " map ", V("map variant letter"))),
    setv("map item number", itemnum(V("map name"), "map list names")),
    comment="USE PICKED MAP: 'map variant' -> 'map variant letter', 'map name'\nand 'map item number'.")

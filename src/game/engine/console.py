"""The developer console: typed commands for testing levels quickly (C during a game, once
developer mode is on: hold D + E + V together on the title screen)."""
from sb3extra import *
from game.config import *
from levels import MAP_LETTERS
from game.engine.sprite import engine

engine.script(
    Def("toggle developer mode", warp=False),
    note("DEVELOPER MODE: switch it on or off. While it's on, C opens the\n"
         "developer console during a game, and the options menu's level select\n"
         "offers every level. Like the other options, the green flag doesn't\n"
         "reset it.",
         setv("developer mode", sub(1, V("developer mode")))),
    play("menu click"),
    ifelse(eq(V("developer mode"), 1), [show_list("developer console")], [hide_list("developer console")]),
    wait_until(not_(or_(or_(key("d"), key("e")), key("v")))),
    comment="TOGGLE DEVELOPER MODE: hold D + E + V together on the title screen.")

engine.script(
    Def("split the answer into words"),
    note("Split what was typed into words at the spaces: \"level 3 b\" becomes\n"
         "\"level\", \"3\", \"b\" in 'console words'. Go along the answer letter by\n"
         "letter, building up a word until a space ends it.",
         clear_list("console words")), setv("console word", ""), setv("console letter position", 1),
    repeat(strlen(answer()),
           ifelse(eq(letter(V("console letter position"), answer()), " "),
                  [if_(not_(eq(V("console word"), "")), addto("console words", V("console word"))),
                   setv("console word", "")],
                  [setv("console word", join(V("console word"), letter(V("console letter position"), answer())))]),
           chg("console letter position", 1)),
    if_(not_(eq(V("console word"), "")), addto("console words", V("console word"))),
    comment="SPLIT THE ANSWER INTO WORDS: for the developer console.")

engine.script(
    Def("use console map letter"),
    note("A 'level' or 'map' command can name a map: \"b\". Find its number (B is\n"
         "letter 2 of \"ABC...\"); if this level has that map, play it. ('=' doesn't\n"
         "care about capitals, so \"b\" and \"B\" both work.)",
         setv("console letter position", 1)),
    repeat(len(MAP_LETTERS),
           if_(and_(eq(letter(V("console letter position"), MAP_LETTERS), V("console map letter")),
                    not_(gt(V("console letter position"), V("level map count")))),
               setv("map variant", V("console letter position")), call("use picked map")),
           chg("console letter position", 1)),
    comment="USE CONSOLE MAP LETTER: play the map the console asked for.")

def command(name, *blocks):
    return if_(eq(V("console command"), name), *blocks)

engine.script(
    Def("developer console", warp=False),
    note("Wait for C to be let go, show the list of commands, and ask. Scratch's\n"
         "'ask and wait' block pauses this script (and so the whole game) until\n"
         "Enter is pressed.",
         wait_until(not_(key("c")))),
    show_list("developer console"),
    ask_and_wait("Developer console: type a command (see the list)"),
    hide_list("developer console"),
    call("split the answer into words"),
    setv("console command", item(1, "console words")),
    command("god", note("GOD: hurt_player() only hurts you while 'god mode' is 0.",
                        setv("god mode", sub(1, V("god mode"))))),
    command("heal", setv("health", 100)),
    command("guns", *[replace("weapons owned", slot, 1) for slot in range(1, len(WEAPON_TYPES) + 1)],
            *[replace("ammo counts", ammo_slot, item(ammo_slot, "ammo limits")) for ammo_slot in range(1, len(AMMO) + 1)]),
    command("keys", setv("has red key", 1), setv("has blue key", 1), setv("has skull key", 1)),
    command("kill", note("KILL: every monster takes a huge hit this frame (see the Monster\n"
                         "sprite's DAMAGE step). They count as kills, and a boss drops its key.",
                         setv("console kill", 1))),
    command("exit", setv("game state", EXIT_REACHED)),
    command("level",
            note("LEVEL N [map letter]: only a level that exists. The main script does\n"
                 "the jump when it sees the 'level jump' game state.",
                 setv("console number", round_(item(2, "console words")))),
            if_(and_(gt(V("console number"), 0), not_(gt(V("console number"), length("level names")))),
                setv("current level", V("console number")), setv("console map letter", item(3, "console words")),
                setv("console jump gives weapons", 1), setv("game state", LEVEL_JUMP))),
    command("map", setv("console map letter", item(2, "console words")),
            setv("console jump gives weapons", 0), setv("game state", LEVEL_JUMP)),
    note("Don't count the time spent typing as level time.",
         setv("time at last frame", timer())),
    comment="DEVELOPER CONSOLE: C during a game, in developer mode. Type a\n"
            "command; the list on the stage shows them all. For testing levels\n"
            "and maps quickly (and for fun).")

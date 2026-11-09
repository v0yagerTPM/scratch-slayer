"""The in-game music."""
from sb3extra import *
from game.config import *
import pictures.world, sounds.music
from game.stage import project

music = Target(project, "Music", layer=1, visible=False)
music.costume("speaker", pictures.world.TINY, 1, 1)
for sound_name, make_sound in (("episode 1 theme", sounds.music.episode_1_theme), ("episode 2 theme", sounds.music.episode_2_theme)):
    add_sound(music, sound_name, make_sound)
music.var("episode number")
music.script(flag(), hide())
music.script(recv(START_MUSIC), stop_sounds(), set_volume(mul(V("music is on"), 100)),
          note("Levels 1-3 are episode 1, levels 4-6 episode 2. Each has its own loop.",
               ifelse(lt(V("current level"), 4), [setv("episode number", 1)], [setv("episode number", 2)])),
          note("Loop the track until you die, go back to the title, or win. (Dying\n"
               "and winning stop all sounds, which ends 'play until done' early.)",
               until(or_(or_(eq(V("game state"), DEAD), eq(V("game state"), TITLE)), eq(V("screen showing"), WIN)),
                     play_until_done_named("episode 1 theme", joins("episode ", V("episode number"), " theme")))),
          comment="IN-GAME MUSIC: starts when each level starts.")
music.script(recv(APPLY_MUSIC), set_volume(mul(V("music is on"), 100)),
          comment="MUSIC ON/OFF (N key or the options menu): volume 100 or 0.")

"""Builds scratch-slayer.sb3 — a 6-level raycasting shooter made of real Scratch blocks.

Every Scratch variable, list, broadcast and custom block uses a descriptive name, and every
section of every script carries a comment that explains it.

    python3 src/build.py dist/scratch-slayer.sb3

The game is written in pieces, one file per part of the game, in the game/ folder. This file
puts them together: importing a piece runs it, and running it adds its sprite and scripts to the
project. THE ORDER BELOW MATTERS. Sprites are created in this order, and every block gets the
next number from one counter, so moving a line here changes the project Scratch sees (and
'npm run compare' will say so). Add a new piece where it belongs in the game, not at the end.
"""
import sys

# Settings and shared names, then the project and its Stage, then the guide on the Stage.
import game.config
from game.stage import project
import game.guide

# The Engine sprite: the game loop, weapons, options logic, level loading, movement, 3D view.
import game.engine.sprite
import game.engine.main_loop
import game.engine.weapons
import game.engine.options_input
import game.engine.level_loader
import game.engine.movement
import game.engine.raycaster

# Things in the 3D world.
import game.screen_placement
import game.monster
import game.pickups
import game.barrels
import game.projectiles

# What's drawn over the 3D view, then the screens between levels, the options menu and music.
import game.hud
import game.title_screen
import game.level_cards
import game.death_screen
import game.victory_screen
import game.options_screen
import game.music

# ---------------- sanity checks: names must be unique between the Stage and each sprite ----------------
for sprite in project.targets[1:]:
    clash = set(sprite.vars) & set(project.stage_vars)
    assert not clash, (sprite.name, clash)
    for name in list(sprite.vars) + list(project.stage_vars) + list(project.stage_lists):
        assert len(name) > 2, f"name too short: {name}"

if __name__ == "__main__":
    output_path = sys.argv[1] if len(sys.argv) > 1 else "scratch-slayer.sb3"
    project_json = project.save(output_path)
    print("saved", output_path, "blocks:", sum(len(target["blocks"]) for target in project_json["targets"]),
          "comments:", sum(len(target["comments"]) for target in project_json["targets"]))

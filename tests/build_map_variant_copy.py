"""Builds a TEST COPY of the game in which levels 1 and 2 have three maps each.

The real game may not have a map B or map C for every level yet, but the code that picks a map,
offers R on the death screen and shows each map's card still needs testing. So this copy gives
levels 1 and 2 two extra maps made from their map A:
    map B "Mirror Image"   map A flipped left to right
    map C "Upside Down"    map A flipped top to bottom
A flipped map is just as finishable as the original, so validate() passes it, and the player
starts somewhere different on each one, so a test can tell which map was loaded.

    python3 tests/build_map_variant_copy.py tests/out/map-variant-copy.sb3

npm test runs this before the plans; a plan that starts with {"project": "map variant copy"}
is played on this copy instead of dist/scratch-slayer.sb3. It is never shipped.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import levels  # noqa: E402

for level in levels.LEVELS[:2]:
    first_map = level["maps"][0]
    # Flipping left to right turns "facing right" (0) into "facing left" (180) and the other way
    # round; flipping top to bottom swaps "facing down" (90) and "facing up" (270).
    level["maps"].append(dict(first_map, name="Mirror Image", tint="#1a2a5a",
                              rows=[row[::-1] for row in first_map["rows"]],
                              angle=(180 - first_map["angle"]) % 360))
    level["maps"].append(dict(first_map, name="Upside Down", tint="#3a1a5a",
                              rows=list(reversed(first_map["rows"])),
                              angle=(360 - first_map["angle"]) % 360))

# Importing build.py builds the whole project from the changed level list (and runs its checks).
import build  # noqa: E402

output_path = sys.argv[1] if len(sys.argv) > 1 else "map-variant-copy.sb3"
os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
build.project.save(output_path)
print("saved", output_path, "(test copy: levels 1 and 2 have maps A, B and C)")

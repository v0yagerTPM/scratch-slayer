"""Tests for the map checker in src/levels.py.

Each test breaks a small, valid map in one way and checks that validate() stops with a
LevelError whose message explains the problem. Run with: python3 tests/test_levels.py
(npm test runs it too).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from levels import LEVELS, Grid, LevelError, validate  # noqa: E402

# A tiny map that passes every check: the start, a red key, a barrel, a secret closet with a
# health pack, a red door, a boss, a skull door, and the exit (in the outside wall).
#   column: 01234567
GOOD_MAP = [
    "11111111",    # row 0
    "1P0K0SH1",    # row 1   secret wall S at column 5, health pack H in the closet behind it
    "10000E11",    # row 2   barrel E at column 5
    "11R11111",    # row 3   red door R at column 2
    "10W00001",    # row 4   the boss W
    "111111Z1",    # row 5   skull door Z at column 6
    "1111110X",    # row 6   exit switch X at column 7
    "11111111",    # row 7
]


def level_with(map_rows):
    return dict(name="Test Level", rows=map_rows)


def change(map_rows, column, row, letter):
    """A copy of the map with one square changed."""
    changed = list(map_rows)
    changed[row] = changed[row][:column] + letter + changed[row][column + 1:]
    return changed


def expect_problem(map_rows, *words):
    """validate() must fail, and its message must contain every one of 'words'."""
    try:
        validate(level_with(map_rows))
    except LevelError as problem:
        message = str(problem)
        missing = [word for word in words if word not in message]
        assert not missing, f"message {message!r} is missing {missing}"
        return message
    raise AssertionError(f"expected a map problem mentioning {words}, but the map passed")


def test_real_levels_pass():
    for level in LEVELS:
        validate(level)


def test_good_map_passes():
    counts = validate(level_with(GOOD_MAP))
    assert counts["size"] == "8x8" and counts["W"] == 1 and counts["S"] == 1


def test_rows_of_different_lengths():
    expect_problem(GOOD_MAP[:2] + ["1000E11"] + GOOD_MAP[3:], "row 2 has 7 letters", "row 0 has 8")


def test_unknown_letter():
    expect_problem(change(GOOD_MAP, 2, 2, "Y"), "unknown letter 'Y'", "column 2, row 2",
                   "item 3 of the list, letter 3")


def test_hole_in_the_outside_wall():
    expect_problem(change(GOOD_MAP, 0, 2, "0"), "outside edge", "column 0, row 2")


def test_no_player_start():
    expect_problem(change(GOOD_MAP, 1, 1, "0"), "exactly one player start", "there are 0")


def test_two_player_starts():
    expect_problem(change(GOOD_MAP, 1, 2, "P"), "exactly one player start", "there are 2", "column 1, row 2")


def test_unreachable_monster():
    walled_in = change(change(GOOD_MAP, 3, 4, "1"), 5, 4, "1")   # walls on both sides of column 4
    walled_in = change(walled_in, 4, 4, "M")                     # ... and a monster boxed in between
    expect_problem(walled_in, "'M'", "column 4, row 4", "can't be reached")


def test_key_after_its_door():
    # Move the red key behind its own red door: nothing past the door can be reached.
    behind_door = change(change(GOOD_MAP, 3, 1, "0"), 4, 4, "K")
    expect_problem(behind_door, "can't be reached")


def test_unreachable_secret_wall():
    sealed = change(GOOD_MAP, 4, 1, "1")   # the only floor next to the secret wall is now wall
    expect_problem(sealed, "secret wall", "column 5, row 1", "no reachable floor")


def test_two_exits():
    expect_problem(change(GOOD_MAP, 6, 2, "X"), "exactly one exit switch", "there are 2")


def test_two_bosses():
    expect_problem(change(GOOD_MAP, 4, 4, "T"), "only one boss per level", "there are 2")


def test_skull_door_without_a_boss():
    expect_problem(change(GOOD_MAP, 2, 4, "0"), "skull door (Z) needs a boss")


def test_skull_door_that_can_be_walked_around():
    # Open a second way down to the exit: it no longer needs the boss.
    expect_problem(change(change(GOOD_MAP, 5, 5, "0"), 5, 6, "0"), "without going through the skull door")


def test_grid_things_must_land_on_floor():
    drawing = Grid(5, "1")
    drawing.put(2, 2, "1")
    try:
        drawing.things("M", [(2, 2)])
    except LevelError as problem:
        assert "can't put 'M'" in str(problem) and "column 2, row 2" in str(problem), str(problem)
    else:
        raise AssertionError("putting a monster inside a wall should fail")


if __name__ == "__main__":
    tests = [(name, test) for name, test in sorted(globals().items()) if name.startswith("test_")]
    failed = 0
    for name, test in tests:
        try:
            test()
        except Exception as problem:   # a failed check, or a crash
            failed += 1
            print(f"FAIL  {name}: {problem}")
    print(f"{len(tests) - failed} of {len(tests)} map checker tests passed.")
    sys.exit(1 if failed else 0)

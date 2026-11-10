"""Tests for the map checker in src/levels.py.

Each test breaks a small, valid map in one way and checks that validate() stops with a
LevelError whose message explains the problem. Run with: python3 tests/test_levels.py
(npm test runs it too).
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import levels  # noqa: E402
from levels import LEVELS, LevelError, every_map, map_title, validate  # noqa: E402

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
    for level_number, map_letter, level, game_map in every_map():
        validate(dict(name=map_title(level_number, map_letter, level, game_map), rows=game_map["rows"]))


def test_every_level_has_maps():
    levels.check_level_list()
    assert all(level["maps"] for level in LEVELS)


def test_level_without_maps():
    saved_maps = LEVELS[0]["maps"]
    LEVELS[0]["maps"] = []
    try:
        levels.check_level_list()
    except LevelError as problem:
        assert "has no maps" in str(problem), problem
    else:
        raise AssertionError("expected a problem for a level with no maps")
    finally:
        LEVELS[0]["maps"] = saved_maps


def test_map_file_names():
    assert levels.map_list_name(2, "B") == "level 2 map B"
    assert levels.map_file_path(2, "B").endswith("level 2 map B.txt")


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


def load_from_text(file_bytes):
    """Write a map file into a temporary maps folder, load it with load_map(), and return the rows."""
    with tempfile.TemporaryDirectory() as folder:
        with open(os.path.join(folder, "level 1 map A.txt"), "wb") as map_file:
            map_file.write(file_bytes)
        real_folder, levels.MAPS_FOLDER = levels.MAPS_FOLDER, folder
        try:
            return levels.load_map(1, "A")
        finally:
            levels.MAPS_FOLDER = real_folder


def test_map_files_load_like_scratch_exports():
    # Scratch on Windows: carriage return + new line between rows, and no line break at the end.
    assert load_from_text(b"111\r\n1P1\r\n111") == ["111", "1P1", "111"]
    # Mac / Linux, with a final line break and some blank lines at the end.
    assert load_from_text(b"111\n1P1\n111\n\n\n") == ["111", "1P1", "111"]
    # Saved by a Windows editor that adds an invisible "byte order mark" at the start.
    assert load_from_text("\ufeff111\n1P1\n111".encode("utf-8")) == ["111", "1P1", "111"]


def test_stray_spaces_are_kept_so_the_checker_can_point_at_them():
    rows = load_from_text(b"11111\n1P0X1 \n11111")
    expect_problem(rows, "row 1 has 6 letters")


def test_empty_map_file():
    try:
        load_from_text(b"\n\n")
    except LevelError as problem:
        assert "is empty" in str(problem), str(problem)
    else:
        raise AssertionError("an empty map file should fail")


def test_missing_map_file():
    try:
        levels.load_map(99, "A")
    except LevelError as problem:
        assert "map file is missing" in str(problem) and "level 99 map A.txt" in str(problem), str(problem)
    else:
        raise AssertionError("a missing map file should fail")


def test_every_map_has_its_file():
    for level_number, map_letter, level, game_map in every_map():
        path = levels.map_file_path(level_number, map_letter)
        assert os.path.exists(path), path


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

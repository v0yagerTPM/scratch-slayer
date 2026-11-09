"""Compare the Scratch project built from your current source with one built from a git version.

    python3 tests/compare_builds.py            compare with main
    python3 tests/compare_builds.py HEAD       compare with your last commit
    npm run compare -- some-branch             the same, through npm

Why: a refactor (renaming, moving code between files) should not change the game at all. The
build is deterministic (the same source always gives the same .sb3 contents), so we can build
both versions and compare them file by file. "IDENTICAL" means students would see exactly the
same project, block for block. Anything else lists what changed, sprite by sprite.

Exit code 0 = identical, 1 = different, 2 = something went wrong.
"""
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import zipfile

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def fail(message):
    """Something went wrong (not a difference between the builds): say what, exit with code 2."""
    print("compare_builds:", message)
    sys.exit(2)


def build(source_folder, output_path):
    """Run src/build.py from a source folder and return the built project's files as a dict."""
    result = subprocess.run([sys.executable, os.path.join(source_folder, "src", "build.py"), output_path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout + result.stderr)
        fail(f"the build failed in {source_folder}")
    with zipfile.ZipFile(output_path) as project_zip:
        return {name: project_zip.read(name) for name in project_zip.namelist()}


def export_git_version(git_ref, folder):
    """Copy the src folder as it was at git_ref into folder (without touching your files)."""
    archive = subprocess.run(["git", "-C", PROJECT_ROOT, "archive", git_ref, "src"], capture_output=True)
    if archive.returncode != 0:
        fail(f"git couldn't find '{git_ref}': {archive.stderr.decode().strip()}")
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as source_tar:
        if hasattr(tarfile, "data_filter"):     # newer Pythons: refuse anything unsafe in the archive
            source_tar.extractall(folder, filter="data")
        else:
            source_tar.extractall(folder)


def renumber_ids(project):
    """Replace the build's IDs with stable ones before comparing.

    The build numbers IDs with one counter for the whole project, so adding a block to the
    Engine shifts the IDs of every sprite built after it. Here variables, lists and broadcasts
    are named after their Scratch names, and blocks and comments are numbered inside each sprite,
    so only real changes show up.
    """
    new_ids = {}
    for target in project["targets"]:
        for kind in ("variables", "lists"):
            for old_id, (name, _value) in (target.get(kind) or {}).items():
                new_ids[old_id] = f"{kind}: {name}"
        for old_id, name in (target.get("broadcasts") or {}).items():
            new_ids[old_id] = f"broadcast: {name}"
    for target in project["targets"]:
        for kind in ("blocks", "comments"):
            for number, old_id in enumerate(target.get(kind) or {}):
                new_ids[old_id] = f"{target['name']} {kind} {number}"

    def rename(value):
        if isinstance(value, dict):
            return {new_ids.get(key, key): rename(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rename(item) for item in value]
        if isinstance(value, str):
            return new_ids.get(value, value)
        return value
    return rename(project)


def describe_project_differences(old_json, new_json):
    """A short, readable list of what changed between two project.json files."""
    old_targets = {target["name"]: target for target in renumber_ids(json.loads(old_json))["targets"]}
    new_targets = {target["name"]: target for target in renumber_ids(json.loads(new_json))["targets"]}
    lines = []
    for name in sorted(set(old_targets) - set(new_targets)):
        lines.append(f"  sprite removed: {name}")
    for name in sorted(set(new_targets) - set(old_targets)):
        lines.append(f"  sprite added: {name}")
    for name in sorted(set(old_targets) & set(new_targets)):
        old_target, new_target = old_targets[name], new_targets[name]
        changes = []
        for part in ("blocks", "comments", "variables", "lists", "costumes", "sounds"):
            if old_target.get(part) != new_target.get(part):
                changes.append(f"{part} ({len(old_target.get(part) or {})} -> {len(new_target.get(part) or {})})")
        other_keys = {key for key in set(old_target) | set(new_target)
                      if key not in ("blocks", "comments", "variables", "lists", "costumes", "sounds")
                      and old_target.get(key) != new_target.get(key)}
        changes += sorted(other_keys)
        if changes:
            lines.append(f"  {name}: " + ", ".join(changes))
    old_rest = {key: value for key, value in json.loads(old_json).items() if key != "targets"}
    new_rest = {key: value for key, value in json.loads(new_json).items() if key != "targets"}
    if old_rest != new_rest:
        lines.append("  project settings (monitors, extensions or meta) changed")
    return lines


def main():
    git_ref = sys.argv[1] if len(sys.argv) > 1 else "main"
    with tempfile.TemporaryDirectory() as work_folder:
        old_source = os.path.join(work_folder, "old")
        export_git_version(git_ref, old_source)
        old_files = build(old_source, os.path.join(work_folder, "old.sb3"))
        new_files = build(PROJECT_ROOT, os.path.join(work_folder, "new.sb3"))

    if old_files == new_files:
        print(f"IDENTICAL: the project built from your source is exactly the same as {git_ref}'s "
              f"({len(new_files)} files).")
        return 0

    print(f"DIFFERENT from {git_ref}:")
    if old_files.get("project.json") != new_files.get("project.json"):
        for line in describe_project_differences(old_files["project.json"], new_files["project.json"]):
            print(line)
    asset_names = (set(old_files) | set(new_files)) - {"project.json"}
    removed = sorted(name for name in asset_names if name not in new_files)
    added = sorted(name for name in asset_names if name not in old_files)
    if removed or added:
        print(f"  art and sound files: {len(removed)} removed, {len(added)} added "
              "(a changed picture or sound gets a new file name)")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as problem:   # report anything unexpected without a long traceback
        fail(f"unexpected error: {problem}")

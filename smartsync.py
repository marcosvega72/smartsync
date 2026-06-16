#!/usr/bin/env python3
"""smartsync.py - Synchronize a target codebase folder to match a source folder.

Usage:
    smartsync.py <target_folder> <source_folder>

Recursively makes <target_folder> a mirror of <source_folder>:
  * Every file/folder present in source is copied into target.
  * Every file/folder present in target that has no counterpart in source
    is deleted.

A well-known set of folder names, file extensions and file names is always
ignored: such items are never copied from source and never deleted from
target (they are treated as invisible to the synchronization).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# Subfolder names ignored at any level.
IGNORED_DIR_NAMES: frozenset[str] = frozenset({
    ".git",
    "external_tools",
    ".settings",
    ".metadata",
    "target",
})

# File extensions ignored (compared case-insensitively).
IGNORED_FILE_EXTENSIONS: frozenset[str] = frozenset({
    ".class",
    ".classpath",
    ".db",
    ".dll",
    ".gz",
    ".jar",
    ".pdf",
    ".war",
})

# Specific file names ignored.
IGNORED_FILE_NAMES: frozenset[str] = frozenset({
    ".gitattributes",
    ".gitignore",
})


def is_ignored_dir(name: str) -> bool:
    return name in IGNORED_DIR_NAMES


def is_ignored_file(name: str) -> bool:
    if name in IGNORED_FILE_NAMES:
        return True
    return Path(name).suffix.lower() in IGNORED_FILE_EXTENSIONS


def _names(directory: Path, *, dirs: bool) -> set[str]:
    """Return non-ignored child names of *directory* (dirs or files)."""
    result: set[str] = set()
    for child in directory.iterdir():
        if child.is_dir():
            if not dirs or is_ignored_dir(child.name):
                continue
        else:
            if dirs or is_ignored_file(child.name):
                continue
        result.add(child.name)
    return result


def copy_tree(source: Path, target: Path) -> None:
    """Recursively copy *source* into a fresh *target*, honoring ignore rules."""
    target.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        if child.is_dir():
            if is_ignored_dir(child.name):
                continue
            copy_tree(child, target / child.name)
        else:
            if is_ignored_file(child.name):
                continue
            shutil.copy2(child, target / child.name)


def delete_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def sync(source: Path, target: Path) -> None:
    """Make *target* mirror *source* recursively, honoring ignore rules."""
    target.mkdir(parents=True, exist_ok=True)

    source_dirs = _names(source, dirs=True)
    source_files = _names(source, dirs=False)
    target_dirs = _names(target, dirs=True)
    target_files = _names(target, dirs=False)

    # Delete target entries with no counterpart in source.
    for name in target_files - source_files:
        delete_path(target / name)
    for name in target_dirs - source_dirs:
        delete_path(target / name)

    # Copy / overwrite files from source.
    for name in source_files:
        dest = target / name
        # If a directory currently occupies the destination, remove it first.
        if dest.is_dir():
            delete_path(dest)
        shutil.copy2(source / name, dest)

    # Recurse into directories from source.
    for name in source_dirs:
        src_dir = source / name
        dest_dir = target / name
        # If a file currently occupies the destination, remove it first.
        if dest_dir.exists() and not dest_dir.is_dir():
            delete_path(dest_dir)
        sync(src_dir, dest_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize a target codebase folder to mirror a source folder.",
    )
    parser.add_argument("target", help="Target folder (will be modified to match source).")
    parser.add_argument("source", help="Source folder (authoritative copy).")
    args = parser.parse_args(argv)

    target = Path(args.target)
    source = Path(args.source)

    if not source.is_dir():
        parser.error(f"source folder does not exist or is not a directory: {source}")
    if target.exists() and not target.is_dir():
        parser.error(f"target exists but is not a directory: {target}")

    if source.resolve() == target.resolve():
        parser.error("source and target must be different folders.")

    sync(source, target)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3

"""
TODO:
* insert good documentation here
* add built-in code tests
* add flag to optionally over-write existing copies
* --ignore= flag to manage list of metadata file extensions to ignore by glob (default ['log', 'bak'])


# REMEMBER REMEMBER ALWAYS LOOM FULL FILES
"""

from pathlib import Path
from sys import stdin, argv, stderr
from uuid import UUID
from hashlib import sha256
from datetime import datetime, timezone
from os import symlink, environ, uname
from re import compile as RE_compile
from mimetypes import guess_extension
from shutil import copy2, SameFileError
from typing import Optional, List, Generator, Tuple
import argparse

from dotenv import load_dotenv
from magic import from_file as magic_from_file

try:
    from reflink import reflink

    def file_link(from_path: Path | str, to_path: Path | str, verbose: bool = False):
        from_path = Path(from_path)
        to_path = Path(to_path)

        try:
            reflink(str(from_path), str(to_path))
            if verbose:
                print(f"{to_path.name:<45} <= {from_path}")
            return
        except:
            copy2(str(from_path), str(to_path))
            if verbose:
                print(f"{to_path.name:<45} <- {from_path}")

except ModuleNotFoundError:

    def file_link(from_path: Path | str, to_path: Path | str, verbose: bool = False):
        from_path = Path(from_path)
        to_path = Path(to_path)
        copy2(str(from_path), str(to_path))
        if verbose:
            print(f"{to_path.name:<45} <- {from_path}")


load_dotenv()

UDIR_DEFAULT: Path = Path(environ.get("UDIR", Path.cwd() / "uu")).resolve()
HASH_CHUNKSIZE: int = 8192
HOST: str = uname().nodename

re_UUID = RE_compile(
    r"[0-9a-fA-F]{8}[.-]?[0-9a-fA-F]{4}[.-]?[0-9a-fA-F]{4}[.-]?[0-9a-fA-F]{4}[.-]?[0-9a-fA-F]{12}"
    # r"[0-9a-fA-F]{8}[.-]?[0-9a-fA-F]{4}[.-]?[1-5][0-9a-fA-F]{3}[.-]?[89abAB][0-9a-fA-F]{3}[.-]?[0-9a-fA-F]{12}"
)


def now() -> datetime:
    return datetime.now(timezone.utc)


def path_sha256(path: Path, version: int = 4) -> Tuple[UUID, str]:
    sha256_hash = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(HASH_CHUNKSIZE), b""):
            sha256_hash.update(chunk)
    digest = sha256_hash.digest()
    raw = bytearray(digest[:16])
    raw[6] = (raw[6] & 0x0F) | (version << 4)
    raw[8] = (raw[8] & 0x3F) | 0x80
    _uuid = UUID(bytes=bytes(raw))
    return _uuid, digest.hex()


def uu_dir(_uuid: UUID) -> Path:
    uuid_dir = UDIR_DEFAULT / _uuid.hex[:2] / _uuid.hex[2:4]
    uuid_dir.mkdir(parents=True, exist_ok=True)
    return uuid_dir


def _clean_extension(path: Path) -> Tuple[str, str]:

    mime = magic_from_file(str(path), mime=True)
    extension = guess_extension(mime, strict=True)

    # fix for markdown
    if path.suffix == ".md" and mime == "text/html":
        mime = "text/markdown"
        extension = ".md"

    # fix for markdown
    if path.suffix in [".yml", ".yaml"] and mime == "text/plain":
        mime = "text/yml"
        extension = ".yml"

    if not extension:
        extension = path.suffix or ".dat"

    return mime, extension


def uu_link(path: Path, with_related=True, verbose=False) -> str:
    uu, digest = path_sha256(path)

    source_stem = path.stem
    source_full = path.resolve()
    parent = source_full.parent
    target_base = uu_dir(uu) / str(uu)

    mime, target_ext = _clean_extension(path)

    target_name = Path(f"{target_base}{target_ext}")

    with open(f"{target_base}.ylog", "a") as uulog:
        _now = f"{now():%Y-%m-%dT%H:%M:%S}"

        print(
            f"---\nuuid: {uu}\npath: {source_full}\nhost: {HOST}\nhash:\n  sha256: {digest}\ntype: {target_ext} {mime}\ntimestamp: {_now}",
            file=uulog,
        )

        try:
            file_link(source_full, f"{target_name}", verbose=verbose)
        except:
            return None

        if with_related:
            _flag_info = False

            for extra_file in parent.glob(str(path.stem) + ".*"):

                if extra_file.resolve() == source_full:
                    continue

                if extra_file.suffix == ".ylog":
                    continue

                if not _flag_info:
                    print("info:", file=uulog)
                    _flag_info = True

                extra_uu_name = Path(
                    uu_link(extra_file, with_related=False, verbose=verbose)
                ).name

                mime, extra_link_ext = _clean_extension(extra_file)
                print(f"  {extra_uu_name}: {extra_file}", file=uulog)

                extra_link = Path(f"{target_base}{extra_link_ext}")

                if extra_link.is_symlink():
                    extra_link.unlink()

                try:

                    extra_link.symlink_to(
                        f"../../{extra_uu_name[:2]}/{extra_uu_name[2:4]}/{extra_uu_name}"
                    )
                    if verbose:
                        print(f"{extra_link.name:<45} ~> {extra_uu_name}")

                except FileExistsError:
                    if verbose:
                        print(f"{extra_link.name:<45} !> {extra_uu_name}")

        _flag_links = False
        for _other_match in re_UUID.findall(path.stem):
            if _other_match == uu:
                continue

            if not _flag_links:
                print("links:", file=uulog)
                _flag_links = True

            linked_uu = UUID(_other_match)
            linked_link = uu_dir(linked_uu) / (str(linked_uu) + target_ext)

            if linked_link.is_symlink():
                linked_link.unlink()

            try:

                linked_link.symlink_to(
                    f"../../{uu.hex[:2]}/{uu.hex[2:4]}/{target_name.name}"
                )

                print(f"  - {linked_uu}", file=uulog)
                if verbose:
                    print(f"{target_name.name:<45} +> {linked_uu}{target_ext}")

            except FileExistsError:
                print(f"  - UNLINKED {linked_uu}", file=uulog)

        print("...", file=uulog)

    return target_name


def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Link files into UUID-based deduplicated archive"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Progress output")
    parser.add_argument("files", nargs="+", help="Files to link")
    return parser.parse_args(argv)


def main(*argv) -> None:
    args = parse_args(argv)

    files = args.files

    for file_name in files:
        path = Path(file_name)
        if path.is_dir():
            continue

        uu_link(path, verbose=args.verbose)


if __name__ == "__main__":
    main(*argv[1:])

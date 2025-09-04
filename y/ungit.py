#!/usr/bin/env python3

"""
Flatten all Git objects in a repository into a deterministic, UUID‑named file
hierarchy using GitPython.

Output tree layout (inside --outdir):
    blobs/
    commits/
    trees/
    tags/
Each contains pairs  <uuid>.obj / <uuid>.json  where the JSON sidecar stores
sha1, size and original path (if any).

Usage::
    python ungit.py /path/to/repo /tmp/export --verbose

Dependencies:
    pip install gitpython python-magic
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, Optional, Set, Tuple, List

import magic  # type: ignore
from git import Repo, BadName

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MIME = magic.Magic(mime=True)
TYPES = {"blob", "tree", "commit", "tag"}


def sha_to_uuid(sha: str) -> uuid.UUID:
    """Derive a stable v5 UUID from a 40‑char SHA‑1 hex string."""
    return uuid.uuid5(uuid.NAMESPACE_OID, sha.lower())


def guess_extension(data: bytes, default: str = "") -> str:
    if not data:
        return default
    mime = MIME.from_buffer(data)
    ext = mimetypes.guess_extension(mime) or default
    # Ensure no leading dot duplication later
    return ext.lstrip(".")


def save_pair(
    outdir: Path, otype: str, uid: uuid.UUID, payload: bytes, meta: Dict
) -> None:
    o_dir = outdir / f"{otype}s"
    o_dir.mkdir(parents=True, exist_ok=True)

    # determine extension for blobs only
    ext = ""
    if otype == "blob":
        ext = guess_extension(payload)

    subdir = o_dir / f"{uid.hex[0:2]}/{uid.hex[2:4]}"
    subdir.mkdir(parents=True, exist_ok=True)

    obj_path = subdir / f"{uid}.obj{('.' + ext) if ext else ''}"
    meta_path = subdir / f"{uid}.json"

    obj_path.write_bytes(payload)
    meta_path.write_text(json.dumps(meta, indent=2))


# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------


def export_repo(repo_path: Path, outdir: Path, *, verbose: bool = False) -> None:
    repo = Repo(repo_path)
    if repo.bare is False and (repo_path / ".git").exists():
        # for a non‑bare repo, use its .git
        repo = Repo(repo_path / ".git")

    processed: Set[str] = set()
    count = 0

    # Use rev‑list to get all reachable objects; add --objects to include blobs
    for line in repo.git.rev_list("--objects", "--all").splitlines():
        parts = line.split()
        if not parts:
            continue
        sha = parts[0]
        if sha in processed:
            continue
        processed.add(sha)
        try:
            git_obj = repo.rev_parse(sha)
            otype = git_obj.type
            if otype not in TYPES:
                continue
            data = git_obj.data_stream.read()
        except Exception:
            continue  # skip unresolvable

        uid = sha_to_uuid(sha)
        meta = {
            "sha1": sha,
            "size": len(data),
            "type": otype,
        }
        if len(parts) >= 2:
            meta["path_hint"] = parts[1]

        save_pair(outdir, otype, uid, data, meta)
        count += 1
        if verbose and count % 500 == 0:
            print(f"{count:,} objects exported…", file=sys.stderr)

    if verbose:
        print(f"Done. {count:,} objects exported into {outdir}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None):
    p = argparse.ArgumentParser(description="Press all Git objects into flat files")
    p.add_argument("repo", type=Path, help="Path to a bare or working Git repository")
    p.add_argument(
        "outdir", type=Path, help="Directory to receive the exported objects"
    )
    p.add_argument("--verbose", "-v", action="store_true", help="Progress output")
    args = p.parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)
    export_repo(args.repo, args.outdir, verbose=args.verbose)


if __name__ == "__main__":
    from sys import argv, stdin, stdout, stderr
    from os import environ

    from dotenv import load_dotenv

    load_dotenv()

    main(argv[1:])

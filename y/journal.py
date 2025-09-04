#!/usr/bin/env python3

from uuid import uuid1
from os import execvp, getenv
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def main(*args, **vargs):

    _EDITOR = getenv("EDITOR", "vim")
    _JDIR = getenv("JDIR", "j")
    _NOW = datetime.now().replace(microsecond=0).isoformat()

    _uuid = uuid1()
    _path = Path(_JDIR) / f"{_uuid}.md"

    with _path.open("w") as jdoc:
        jdoc.write(
            f"""category: journal
id: {_uuid}
date: {_NOW}
---
"""
        )

    try:
        execvp(_EDITOR, [_EDITOR, str(_path)])
    except OSError as e:
        print(f"Error opening editor {_EDITOR} fpr {_path}")
        exit(1)


if __name__ == "__main__":
    from sys import argv

    main(*argv)

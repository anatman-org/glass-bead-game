#!/usr/bin/env python
"""
this is meant to be called as

  `python -my <cmd> [arguments ...]`

and is a set of random tools
"""

"""import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)"""


from argparse import ArgumentParser

from datetime import datetime
import subprocess
import os
import sys
from shlex import split as sh_split
from datetime import datetime
from argparse import ArgumentParser
from cmd import Cmd

from git import Repo

from ._chinese import ChineseHouse
from .log import LOG

sys.stderr = open("error.log", "a")


REPO = Repo(".")
HEAD = REPO.heads[0]

OBJECTS_DIR = os.getcwd() + "/m"


def check_modified():
    proc = subprocess.Popen(["git", "status"], stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline()
        if not line:
            return False

        if (
            line.startswith(b"\tmodified:   ")
            or line.startswith(b"\tdeleted:")
            or line.startswith(b"\trenamed:")
            or line.startswith(b"\tnew file:")
        ):
            return True

    return False


def check(*args):

    print("check")
    print(REPO, REPO.is_dirty())


def commit(*args):
    house = ChineseHouse(ChineseHouse.play())
    composition = house.composition

    if not check_modified():
        return True

    house = ChineseHouse(ChineseHouse.play())
    composition = house.composition

    with open("play.log", "a") as play_log:
        stamp = f"{composition} {datetime.now():%Y%m%d.%H%M%S}"
        print(stamp)
        play_log.write(stamp + "\n")

    subprocess.run(("git", "commit", "-a", "-q", "-m", composition))

    return False


def comment(*args):

    house = ChineseHouse(ChineseHouse.play())
    composition = house.composition

    if not check_modified():
        return True

    house = ChineseHouse(ChineseHouse.play())
    composition = house.composition

    # subprocess.run(("git", "add", "-f", "play.log", "index.*"))

    # figure out how to get f"{composition} in to start the comment
    # or use '! tail -1 play.log'
    # ●    ●●●ⴱ    ⵔⴲⵔ●ⴱ●●ⵔ      ⵔ●●●                  ⵀ
    subprocess.run(("git", "commit", "-a", "-q"))

    return False


def main(*args, input_stream=None):

    match args[0]:

        case "comment":
            comment()

        case "commit":
            commit()

        case "check":
            check()

    return


if __name__ == "__main__":
    from sys import stdin, stdout, stderr, argv

    main(*argv[1:], input_stream=stdin)

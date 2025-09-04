#!/usr/bin/env python3

from sys import stdin, stdout, stderr, argv
from random import choice
from re import compile as re_compile, I as RE_CASE_INSENSITIVE
from io import StringIO
from argparse import ArgumentParser

from glob import glob as file_glob

from ._chinese import ChineseHouse, Hexagram
from ._bits import YSequence, YBit, Yin, Yang, OldYang, OldYin


TRANSLATIONS = [f[2:-4] for f in file_glob("t/*.yml")]
TRANSLATIONS.sort()


def hexagrams():

    for i in range(0, 64):
        x = Hexagram(i)

        print(
            f"""- yi: y{x.value:02o}
  int_val: {x.value}
  binary: 0x{x.value:06b}
  octal: 0o{x.value:02o}
  wen_num: {x.wen}
  unicode: {x}"""
        )

        print("  lines: ", [bool(x.value & (1 << N)) for N in range(0, 6)])

        # print("  trans:")

        # for t in TRANSLATIONS:
        #    try:
        #        print(f"  - {t}: {x.translate(t)}")
        #    except KeyError:
        #        pass


def main(*args, input_stream=stdin):

    hexagrams()
    return


if __name__ == "__main__":
    main(*argv[1:])

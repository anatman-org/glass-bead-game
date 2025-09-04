from sys import stdin, stdout, stderr, argv
from random import choice
from re import compile as re_compile, I as RE_CASE_INSENSITIVE
from io import StringIO
from argparse import ArgumentParser

from ._chinese import ChineseHouse, Hexagram
from ._bits import YSequence, YBit, Yin, Yang, OldYang, OldYin

VIM = ""
for y in (Yin, Yang, OldYang, OldYin):
    VIM += f"{str(y.lines)}{y.dot}{y.dot_alt}{y.unicode}"
VIM = f"[{VIM}][\\s:]*([{VIM}]{{4}}[\\s:]*)+[{VIM}]"
re_VIM = re_compile(VIM)

re_WIM = re_compile(r"\b[y~][0-8][0-8]\b")


def _randomize(in_buf: str) -> str:

    out_buf = ""

    for char in str(in_buf):
        out_buf = out_buf + choice([char.upper(), char.lower()])

    return out_buf


def _vim_fmt(in_buf: str) -> str:
    return YBit.tr_vim(in_buf)


def fmt(*args, input_stream=stdin):

    arg_parser = ArgumentParser()
    arg_parser.add_argument("-z", "--trim", action="store_true")
    arg_parser.add_argument("-y", "--yi", action="store_true")
    arg_parser.add_argument("-x", "--hexagram", action="store_true")
    arg_parser.add_argument("-w", "--wen", action="store_true")
    arg_parser.add_argument(
        "-t",
        "--translation",
        action="store",
        const="prime",
        default=None,
        type=str,
        nargs="?",
    )
    arg_parser.add_argument("-s", "--strip", action="store_true")
    arg_parser.add_argument("-r", "--randomize", action="store_true")
    flags = arg_parser.parse_args(args)

    GLASS = _randomize("glass")
    BEAD = _randomize("bead")
    GAME = _randomize("game")
    ANNOTATED = _randomize("annotated")
    MANUAL = _randomize("manual")
    ANATMAN = "".join(
        (_randomize("the"), ANNOTATED, MANUAL, _randomize("of the"), GLASS, BEAD, GAME)
    )

    TRANSFORMATIONS = {
        GLASS: re_compile(GLASS, RE_CASE_INSENSITIVE),
        BEAD: re_compile(BEAD, RE_CASE_INSENSITIVE),
        GAME: re_compile(GAME, RE_CASE_INSENSITIVE),
        ANNOTATED: re_compile(ANNOTATED, RE_CASE_INSENSITIVE),
        MANUAL: re_compile(MANUAL, RE_CASE_INSENSITIVE),
        ANATMAN: re_compile(ANATMAN, RE_CASE_INSENSITIVE),
    }

    try:
        for n, orig_line in enumerate(input_stream.readlines()):

            line = orig_line
            _vim = False

            for re_test in TRANSFORMATIONS:
                line = TRANSFORMATIONS[re_test].sub(re_test, line)

            if re_VIM.search(line):
                line = _vim_fmt(line)

                try:
                    reading = line[:51]
                    extra = orig_line[50:]

                    rooms = [YSequence(r) for r in reading.split()]
                    house = ChineseHouse(rooms)

                    if flags.randomize:
                        house = ChineseHouse(ChineseHouse.play())

                    x_real = Hexagram(house.major.real)
                    x_imag = Hexagram(house.major.imag)
                    line = house.composition

                    if flags.wen:
                        line += f" w{x_real.wen}~{x_imag.wen}"
                    if flags.hexagram:
                        line += f" {x_real}~{x_imag}"
                    if flags.yi:
                        line += f" y{house.major.real:02o}~{house.major.imag:02o}"

                    if flags.translation:
                        line += f" :{x_real.translate(flags.translation)} ~ {x_imag.translate(flags.translation)}"

                    if not flags.trim:
                        line += extra

                    _vim = True

                except:
                    pass

            # for wim in re_WIM.findall(line):
            #     yield wim

            # de-morse
            # calc

            if flags.strip and not _vim:
                next
            else:
                line = line.rstrip()
                yield line

    except UnicodeDecodeError:
        # just skip
        pass

    return


def filter_main(*args, input_stream=stdin):

    for line in input_stream.readlines():
        fmt_line = _vim_fmt(line)
        if fmt_line != line.rstrip():
            print(fmt_line)


def main(*args, input_stream=stdin):

    for line in fmt(*args, input_stream=input_stream):
        print(line)

    return


if __name__ == "__main__":
    main(*argv[1:])

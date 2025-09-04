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
VIM = f"[{VIM}]\\s*([{VIM}]{{4}}\\s*)+[{VIM}]"
re_VIM = re_compile(VIM)

re_WIM = re_compile(r"\b[yw~][0-7][0-9]\b")
re_HEX = re_compile(r"~?([\u4DC0-\u4DFF])")


def _vim_fmt(in_buf: str) -> str:
    return YBit.tr_vim(in_buf)


def _random_line(x_real, x_imag):

    l_real = None
    l_imag = None
    line = None

    while not (l_real == x_real and l_imag == x_imag):
        house = ChineseHouse(ChineseHouse.play())
        l_real = Hexagram(house.major.real)
        l_imag = Hexagram(house.major.imag)
        line = house.composition

    return line


def resonate(*args, input_stream=stdin):

    for note in args:

        x_real, x_imag = None, None

        if y := re_WIM.findall(note):
            wen = False
            if y[0][0] == "w":
                # wen mode
                wen = True

            imag = real = int(y[0][1:]) if wen else int(y[0][1:], 8)

            if len(y) == 2:
                imag = int(y[1][1:]) if wen else int(y[1][1:], 8)

            x_real = Hexagram(wen=real) if wen else Hexagram(real)
            x_imag = Hexagram(wen=imag) if wen else Hexagram(imag)

        elif y := re_HEX.findall(note):

            match len(y):

                case 1:
                    x_real = x_imag = Hexagram(y[0])
                case 2:
                    x_real, x_imag = Hexagram(y[0]), Hexagram(y[1])

        else:
            yield note
            continue

        yield _random_line(x_real, x_imag)

    return


def main(*args, input_stream=stdin):

    if len(args):
        for echo in resonate(*args):
            if echo:
                print(echo)

    else:
        for line in input_stream.readlines():
            for echo in resonate(*line.split()):
                if echo:
                    print(echo)

    return


if __name__ == "__main__":
    main(*argv[1:])

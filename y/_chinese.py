""" Chinese House rules

this is based on the original rules conceived
by Magister Ludi Knecht who based them heavily
on the I Ching.
"""

from typing import Any, Tuple, List
from random import shuffle, uniform
from pathlib import Path
from functools import total_ordering


# from yaml import safe_load as yaml_load, CLoader as Loader
from yaml import safe_load as yaml_load, Loader

from ._bits import YSequence, YHouse, Yin, Yang, OldYin, OldYang, YBit


TR_PATH = Path(__file__).parent.parent / "t"


@total_ordering
class Trigram(YSequence):
    """Trigram sequence"""

    # two key indexes, first by value then unicode
    _U = "☰☱☲☳☴☵☶☷"
    _V = "0123456789abcdefghijklmnopqrstuvwxyz%ABCDEFGHIJKLMNOPQRSTUVWXYZ="
    _Y = "☷☳☵☱☶☲☴☰"

    _SEQUENCE_MAP = {
        "y": _Y,  # standard Yi sequence
        "fuxi": "☰☴☵☶☷☳☲☱",  # the Fuxi sequence
        "wen": "☲☷☱☰☵☶☳☴",  # the tradional Wen sequence
        "desig": "☷☳☵☴☰☶☲☱",  # the Designori-Campbell sequence
    }

    def __init__(self, value):

        self._value = None

        if isinstance(value, str) and value in self._Y:
            self._value = self._Y.index(value)

        elif isinstance(value, YSequence):
            self._value = value.real

        else:
            self._value = value

        self._sequence = self.from_int(self._value, 3)

    def __str__(self):
        return self._Y[self._value]

    def __eq__(self, other):
        return self._value == other._value

    def __lt__(self, other):
        return self._value < other._value

    def __hash__(self):
        return self._value


@total_ordering
class Hexagram(YSequence):
    """yijing hexagram"""

    # two key indexes, first by value then unicode
    _Y = "䷁䷗䷆䷒䷎䷣䷭䷊䷏䷲䷧䷵䷽䷶䷟䷡䷇䷂䷜䷻䷦䷾䷯䷄䷬䷐䷮䷹䷞䷰䷛䷪䷖䷚䷃䷨䷳䷕䷑䷙䷢䷔䷿䷥䷷䷝䷱䷍䷓䷩䷺䷼䷴䷤䷸䷈䷋䷘䷅䷉䷠䷌䷫䷀"
    _U = "䷀䷁䷂䷃䷄䷅䷆䷇䷈䷉䷊䷋䷌䷍䷎䷏䷐䷑䷒䷓䷔䷕䷖䷗䷘䷙䷚䷛䷜䷝䷞䷟䷠䷡䷢䷣䷤䷥䷦䷧䷨䷩䷪䷫䷬䷭䷮䷯䷰䷱䷲䷳䷴䷵䷶䷷䷸䷹䷺䷻䷼䷽䷾䷿"

    _seq = {
        "vim": _Y,
        "wen": _U,
        "fuxi": "䷀䷪䷍䷡䷈䷄䷙䷊䷉䷹䷥䷵䷼䷻䷨䷒䷌䷰䷝䷶䷤䷾䷕䷣䷘䷐䷔䷲䷩䷂䷚䷗䷫䷛䷱䷟䷸䷯䷑䷭䷅䷮䷿䷧䷺䷜䷃䷆䷠䷞䷷䷽䷴䷦䷳䷎䷋䷬䷢䷏䷓䷇䷖䷁",
        "mawangdui": "䷀䷋䷠䷉䷅䷌䷘䷫䷳䷙䷖䷨䷃䷕䷚䷑䷜䷄䷇䷦䷻䷾䷂䷯䷲䷡䷏䷽䷵䷧䷶䷟䷁䷊䷎䷒䷆䷣䷗䷭䷹䷪䷬䷞䷮䷰䷐䷛䷝䷍䷢䷷䷥䷿䷔䷱䷸䷈䷓䷴䷼䷺䷤䷩",
        "jingfang": "䷀䷫䷠䷋䷓䷖䷢䷍䷲䷏䷧䷟䷭䷯䷛䷐䷜䷻䷂䷾䷰䷶䷣䷆䷳䷕䷙䷨䷥䷉䷼䷴䷁䷗䷒䷊䷡䷪䷄䷇䷸䷈䷤䷩䷘䷔䷚䷑䷝䷷䷱䷿䷃䷺䷅䷌䷹䷮䷬䷞䷦䷎䷽䷵",
        "shaoyong": "䷁䷖䷇䷓䷏䷢䷬䷋䷎䷳䷦䷴䷽䷷䷞䷠䷆䷃䷜䷺䷧䷿䷮䷅䷭䷑䷯䷸䷟䷱䷛䷫䷗䷚䷂䷩䷲䷔䷐䷘䷣䷕䷾䷤䷶䷝䷰䷌䷒䷨䷻䷼䷵䷥䷹䷉䷊䷙䷄䷈䷡䷍䷪䷀",
        "siu": "䷀䷫䷌䷉䷈䷍䷪䷠䷘䷼䷙䷡䷅䷤䷥䷄䷸䷝䷹䷱䷰䷛䷋䷩䷨䷊䷺䷕䷵䷴䷔䷻䷑䷶䷷䷐䷟䷞䷮䷯䷾䷿䷓䷚䷒䷃䷣䷳䷲䷢䷂䷭䷽䷬䷜䷦䷧䷗䷆䷎䷏䷇䷖䷁",
    }

    def __init__(self, value=None, **args):

        self._value = None

        if args:
            for idx in args:
                if idx in self._seq:
                    value = self._seq[idx][int(args[idx] - 1)]
                    self._value = self._Y.index(value)

        elif isinstance(value, str) and value in self._Y:
            self._value = self._Y.index(value)

        elif isinstance(value, YSequence):
            self._value = value.real

        else:
            self._value = value

        self._sequence = self.from_int(self._value, 6)

    @property
    def value(self):
        return self._value

    @property
    def wen(self):
        return self._seq["wen"].index(self._Y[self._value]) + 1

    @property
    def top(self):
        return Trigram(self._sequence[:3])

    @property
    def bottom(self):
        return Trigram(self._sequence[3:])

    def translate(self, translation):

        with open(TR_PATH / (translation + ".yml"), "r", encoding="utf-8") as f_trans:

            translation = yaml_load(f_trans)
            return (
                translation[f"{self._value:02o}"]["title"]
                .encode()
                .decode("unicode-escape")
            )

    def __str__(self):
        return self._Y[self._value]

    def __eq__(self, other):
        try:
            return self._value == other._value
        except:
            return False

    def __lt__(self, other):
        return self._value < other._value

    def __hash__(self):
        return self._value


class ChineseHouse(YHouse):
    def __init__(self, rooms: List[YSequence]):

        if isinstance(rooms, str):
            rooms = rooms[:-1].split() + [
                rooms[-1],
            ]

        super().__init__(rooms)

    @property
    def composition(self):
        result = str(self.rooms[0])
        for i, room in enumerate(self.rooms[1:4]):
            offset = 0

            if room.product == Yang:
                offset = 1
            elif room.product == Yin:
                offset = 2
            elif room.product == OldYang:
                offset = 3
            elif room.product == OldYin:
                offset = 4

            result += " " * offset * (i + 1) + str(room)

        result += " " * (49 - len(result)) + str(self.rooms[4])
        return result

    @property
    def major(self):

        major_seq = [
            self.rooms[0][0],
            *[
                YBit(Yang),
            ]
            * 4,
            self.rooms[4][0],
        ]
        for room in self.rooms[1:4]:

            for i in range(0, 4):

                major_seq[i + 1] = major_seq[i + 1] * room[i]

                if len(room) > 4:
                    major_seq[i + 1] = major_seq[i + 1] * room[i + 4]

        return YSequence(major_seq)

    @property
    def minor(self):
        lines = []

        for room in self.rooms[1:4]:
            lines.append(room[0::4] + room[1::4])
            lines.append(room[2::4] + room[3::4])

        return YSequence([l.product for l in lines])

    def line_length(self):
        return 12 - (len(self.rooms[1]) + len(self.rooms[2]) + len(self.rooms[3])) // 4

    @staticmethod
    def play() -> List[YSequence]:
        # first assemble a pile
        pile = [Yin] * 22 + [Yang] * 16 + [OldYang] * 9 + [OldYin] * 3

        # shuffle
        shuffle(pile)

        # pull the intent
        intent = pile.pop()

        # plan scores and start
        start = None
        rooms = [None, None, None]

        for r, _ in enumerate(rooms):
            shuffle(pile)
            score = []

            length = len(pile)
            split = int(uniform(4, length - 4))

            left = pile[:split]
            right = pile[split:]

            shuffle(left)
            shuffle(right)

            # pop the wave starter
            if not start:
                start = right.pop()
            else:
                score += [right.pop()]

            left_remainder = len(left) % 4 or 4
            right_remainder = len(right) % 4 or 4

            left, score_left = left[:-left_remainder], left[-left_remainder:]
            right, score_right = right[:-right_remainder], right[-right_remainder:]

            pile = left + right

            score += score_left + score_right
            rooms[r] = score

        return [YSequence(start), *[YSequence(r) for r in rooms], YSequence(intent)]


class Translate(YSequence):
    def __call__(self, value):
        if value.startswith("y"):
            return self.from_y(value)

        # test if hexagram (x)

        elif value.startswith("w"):
            return self.from_w(value)

        # test if "vimcode" from core (v)

        # test if unicode (u)

        # test if dot-notation (t)

    def from_y(self, value):
        return value

    def from_w(self, value):
        return value


class Play:

    @staticmethod
    def coin():
        def _pick():
            return choice(
                [
                    OldYin,
                    *[
                        Yang,
                    ]
                    * 3,
                    *[
                        Yin,
                    ]
                    * 3,
                    OldYang,
                ]
            )

        return YSequence([_pick() for x in range(6)])

    @staticmethod
    def yarrow():
        def _pick():
            return choice(
                [
                    OldYin,
                    *[
                        Yang,
                    ]
                    * 5,
                    *[
                        Yin,
                    ]
                    * 7,
                    *[
                        OldYang,
                    ]
                    * 3,
                ]
            )

        return YSequence([_pick() for x in range(6)])

    @staticmethod
    def bean():
        pool = [
            *[OldYin] * 3,
            *[
                Yang,
            ]
            * 16,
            *[
                Yin,
            ]
            * 22,
            *[
                OldYang,
            ]
            * 9,
        ]
        shuffle(pool)

        def _pick():
            return pool.pop()

        return YSequence([_pick() for x in range(6)])

    @staticmethod
    def card():
        return Hexagram(choice(range(0, 64)))

    @staticmethod
    def card_hatcher():
        # https://www.hermetica.info/Tarot.htm
        return False

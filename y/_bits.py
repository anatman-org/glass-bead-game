"""types
"""

from typing import Any, List
from types import SimpleNamespace
from random import choice
from functools import reduce
from collections.abc import Iterable


class YException(Exception):
    """foundation exception for Y types"""


class YStateException(YException):
    """Exception for states"""

    pass


class YSequenceException(YException):
    pass


class Y_BitState(SimpleNamespace):
    """class representing basic bit states
    states are immutable, so this class emulates
    that.

    a key notion of any state is the value which
    represents the probability space in the
    complex plane

    this is a "private" class that shouldn't be
    called unless defining new states
    """

    @property
    def real(self) -> int:
        return self.value.real

    @property
    def imag(self) -> int:
        return self.value.imag

    def __setattr__(*args):
        raise TypeError("can't change immutable class")

    __delattr__ = __setattr__

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other: Any):
        if not other:
            return False

        if isinstance(other, Y_BitState) and other.name == self.name:
            return True

        if other in (
            self.name,
            self.lines,
            str(self.lines),
            self.value,
            self.pair,
            *list(self.dot),
            *list(self.dot_alt),
            *list(self.extra),
            *list(self.unicode),
        ):
            return True

        return False


GLYPHS = """○●◎◉⊖⊝⊕⨶⨷⦻⊗⊖⊗⊘⊙⊚⊛⊜⊝🜔🜕🜖🜗𝇈𝇉⨷⨀⨁⦿⦾⦻⦰⚪⚫◉◍◎●◐◑◒◓◔◕◯⊕⊖⊗⊘⊙⊚⊛⊜⊝◉◍◎●◯⚌⚍⚏⚎⚊⚋◯○"""
PRODUCT = """~·"""
GLYPHS2 = "●ⴲⴱⵀⵔ"

## DEFINITION OF Y STATES
#
# these are the four primary Y states

Yin = Y_BitState(
    name="yin",
    lines=8,
    unicode="⚋",
    dot_alt="●◍",
    dot="●",
    value=-1 + 0j,
    extra="⚏●⬤02-●•●●",
    pair=(0, 0),
)
Yang = Y_BitState(
    name="yang",
    lines=7,
    unicode="⚊",
    dot_alt="○◯",
    dot="ⵔ",
    value=1 + 0j,
    extra="⚌ⵔ❍⭕1+ⵔ❍⭘",
    pair=(1, 1),
)
OldYang = Y_BitState(
    name="old-yang",
    lines=9,
    value=0 + 1j,
    dot_alt="⦵⦶⦸",
    dot="ⴱⵀ",
    extra="3%iⵀⴱ∅⦸⦶◎ⵀ⊖⊝⦵⦶⦸",
    unicode="⚎",
    pair=(1, 0),
)
OldYin = Y_BitState(
    name="old-yin",
    lines=6,
    value=0 - 1j,
    dot="ⴲ",
    dot_alt="⊗⊕",
    extra="*4ⴲ⊗⊕∗ⴲ⨁ⴲ◉⊗⊕⊕⨂⨁⨶⨷⦻⊗",
    unicode="⚍",
    pair=(0, 1),
)

Y_STATES = [Yin, Yang, OldYin, OldYang]


Y_EQUIV = {
    Yang: [{Yang, Yang}, {Yin, Yin}, {OldYin, OldYang}],
    Yin: [{Yang, Yin}, {OldYin, OldYin}, {OldYang, OldYang}],
    OldYang: [{Yang, OldYang}, {Yin, OldYin}],
    OldYin: [{Yang, OldYin}, {Yin, OldYang}],
}


class YBit:
    """complex YBit with superpositions"""

    @staticmethod
    def random():
        # TODO allow passing a generator
        return YBit(choice(Y_STATES))

    @staticmethod
    def tr_vim(text_in):
        # translate regex to vim dots

        text_out = ""
        for c in text_in:

            if c in Y_STATES:
                i = Y_STATES.index(c)
                text_out = text_out + YBit(Y_STATES[i]).dot

            else:
                text_out = text_out + c

        return text_out

    def __init__(self, value: Any = None):
        self._bit = None

        if isinstance(value, YBit):
            self._bit = value._bit
        elif isinstance(value, Y_BitState):
            self._bit = value
        else:
            for check in Y_STATES:
                if value == check:
                    self._bit = check
                    break

        if not self._bit:
            raise YStateException(f"Invalid state value {value}")

    @property
    def value(self) -> int:
        return self._bit.value

    @property
    def real(self) -> bool:
        return (self._bit.real or self._bit.imag) > 0

    @property
    def imag(self) -> bool:
        return (self._bit.real or -self._bit.imag) > 0

    @property
    def dot(self) -> str:
        return choice(self._bit.dot)

    def __eq__(self, other) -> bool:
        return self.value == other.value

    def __str__(self) -> str:
        return f'{self.dot or " "}'

    def __repr__(self) -> str:
        return str(self._bit)

    def __mul__(self, other: "YBit") -> "YBit":

        if not isinstance(other, YBit):
            other = YBit(other)

        try:
            return YBit(self._bit.value * other._bit.value)
        except AttributeError:
            raise YException(f"weird bit {other}")

    def __add__(self, other: Any) -> "YSequence":
        return YSequence(self) + YSequence(other)


class YSequence:
    """Y sequence

    a sequence is one or more YBits arranged in
    distinct order but that has a commutative
    product value.
    """

    MAX_REPR = 20  # the maximum number of elements in __repr__

    @staticmethod
    def from_int(n: int | float, bitlength: int = None) -> "YSequence":
        """convert a complex integer to a sequence
        while called "from_int" it actually takes
        a complex value (which in python is a float)"""

        result = []

        bits = bin(n)[2:]

        if not bitlength:
            bitlength = len(bits)

        result = [
            Yin,
        ] * (
            bitlength - len(bits)
        ) + [bool(int(digit)) and Yang or Yin for digit in bits]

        # bits = bitlength or max(int(n.real).bit_length(), int(n.imag).bit_length())

        # for bit in range(bits):
        #    result.append(YBit((int(n.real) >> bit & 1, int(n.imag) >> bit & 1)))

        return YSequence(result)

    def __init__(self, sequence: Any):
        self._sequence = []

        if isinstance(sequence, Iterable):
            for y in sequence:
                try:
                    self._sequence.append(YBit(y))
                except YStateException:
                    # ignore junk in sequences
                    pass

        else:
            try:
                self._sequence.append(YBit(sequence))
            except YStateException:
                pass

        if not self._sequence:
            raise YSequenceException(f"No YBits from {sequence}")

    @property
    def sequence(self) -> List[YBit]:
        return self._sequence

    @property
    def product(self) -> YBit:
        return reduce(lambda x, y: x * y, self.sequence)

    @property
    def real(self) -> int:
        result = 0
        for n, b in enumerate((y.real for y in self)):
            result += 2**n * b
        return result

    @property
    def imag(self) -> int:
        result = 0
        for n, b in enumerate((y.imag for y in self)):
            result += 2**n * b
        return result

    @property
    def len(self) -> int:
        return len(self.sequence)

    def __len__(self) -> int:
        return len(self.sequence)

    def __iter__(self) -> YBit:
        yield from self.sequence

    def __add__(self, other: Any) -> "YSequence":
        return YSequence(self.sequence + YSequence(other).sequence)

    def __str__(self) -> str:
        return "".join(str(y) for y in self._sequence)

    def __repr__(self) -> str:
        seq_str = str(self)
        if self.len > YSequence.MAX_REPR:
            seq_str = f"{seq_str[:YSequence.MAX_REPR]}…(+{self.len-YSequence.MAX_REPR})"
        return f"<YSequence {self.product}={seq_str}>"

    def __getitem__(self, key):
        if isinstance(key, slice):
            return YSequence(self._sequence[key.start : key.stop : key.step])
        else:
            return self._sequence[key]


class YHouse:
    """glass (bead) house

    the House is the major component of any glass
    bead composition, composed of one or more
    "rooms" (sequences) which produce distinct
    products within the larger product of the house
    itself
    """

    def __init__(self, rooms: List[YSequence]):
        self._rooms = rooms

    @property
    def rooms(self) -> List[YSequence]:
        """returns a list of the rooms within
        the house, preserving order"""
        return self._rooms

    @property
    def product(self) -> YBit:
        return reduce(lambda x, y: x.product * y.product, self.rooms)

    @property
    def composition(self) -> str:
        """the composition is a dot-notation
        of the overall House
        """

        return (
            "\n".join([f"{room} {room.product}" for room in self.rooms])
            + f"\n{self.product}"
        )

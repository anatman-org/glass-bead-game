import sys
from typing import Optional, List
from argparse import ArgumentParser

import pyphen
from . import GlowBase


class PoemGlow(GlowBase):
    def __init__(self, outlet, base_duration: float, poem_file: Optional[str] = None):
        super().__init__(outlet, base_duration)
        self.poem_file = poem_file

    @classmethod
    async def create(cls, outlet_spec, base_duration, *unknown):
        outlet = await cls.parse_outlet_spec(outlet_spec)

        parser = ArgumentParser()
        parser.add_argument("--file", type=str, default=None)
        try:
            extras = parser.parse_args(unknown)
        except SystemExit:
            print("🛑 Invalid extra arguments for PoemGlow.")
            raise

        return cls(outlet, base_duration, poem_file=extras.file)

    async def glow(self):
        print("📜 Poem mode initiated: flickering by syllables")
        dic = pyphen.Pyphen(lang="en")

        if self.poem_file:
            with open(self.poem_file, "r") as f:
                lines = f.readlines()
        else:
            lines = sys.stdin.readlines()

        syllable_counts: List[int] = []
        for line in lines:
            words = line.strip().split()
            for word in words:
                parts = dic.inserted(word).split("-")
                syllable_counts.append(len(parts))

        while True:
            for count in syllable_counts:
                duration = self.base * count / 3  # normalize around 3
                print(f"🕊️  Syllable: {count}, glowing for {duration:.2f}s")
                await self.outlet.turn_on()
                await self.sleep(duration)
                await self.outlet.turn_off()
                await self.sleep(0.4)

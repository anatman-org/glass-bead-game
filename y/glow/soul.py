import asyncio
import sys
import re
from typing import Optional
from argparse import ArgumentParser

from . import GlowBase


class SoulGlow(GlowBase):
    def __init__(self, outlet, base_duration: float, soul_string: Optional[str] = None):
        super().__init__(outlet, base_duration)
        self.soul_string = soul_string

    @classmethod
    async def create(cls, outlet_spec, base_duration, *unknown):
        outlet = await cls.parse_outlet_spec(outlet_spec)

        parser = ArgumentParser()
        parser.add_argument(
            "--value",
            type=str,
            default=None,
            help="Hex or integer value to encode as pulses",
        )
        try:
            extras = parser.parse_args(unknown)
        except SystemExit:
            print("🛑 Invalid extra arguments for SoulGlow.")
            raise

        return cls(outlet, base_duration, soul_string=extras.value)

    async def glow(self):
        print("💓 Soul mode initiated: encoding binary pulses")

        # Accept UUIDs, hex, integers
        if self.soul_string is None:
            print("⚠️ No value provided. Reading from stdin...")
            self.soul_string = sys.stdin.read().strip()

        # Strip non-hex characters, then convert to binary
        hex_string = re.sub(r"[^0-9a-fA-F]", "", self.soul_string)
        try:
            as_int = int(hex_string, 16)
        except ValueError:
            print("🛑 Could not parse value into hexadecimal.")
            return

        bin_string = bin(as_int)[2:].zfill(len(hex_string) * 4)
        print(f"🧬 Binary sequence: {bin_string}")

        # Pulse each bit
        while True:
            for i, bit in enumerate(bin_string):
                if bit == "1":
                    await self.outlet.turn_on()
                else:
                    await self.outlet.turn_off()
                print(f"⚡ Bit {i}: {bit}")
                await asyncio.sleep(self.base)

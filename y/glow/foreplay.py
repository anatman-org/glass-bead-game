# foreplay.py
# Glow module for prelude pulses

import asyncio
from . import GlowBase

PULSE_PATTERNS = {
    "tease": [0.3, 0.7, 0.4, 1.0],
    "heartbeat": [0.5, 0.5],
    "slowbuild": [0.4, 0.6, 0.8, 1.2],
    "shiver": [0.1, 0.2, 0.15, 0.25, 0.1],
}


class ForeplayGlow(GlowBase):
    def __init__(self, outlet, base_duration: float, mode: str = "tease"):
        super().__init__(outlet, base_duration)
        self.mode = mode if mode in PULSE_PATTERNS else "tease"

    async def glow(self) -> None:
        print(f"💡 Initiating foreplay glow: mode={self.mode}")
        pattern = PULSE_PATTERNS[self.mode]

        for i, duration in enumerate(pattern):
            print(f"✨ Step {i}: pulsing for {duration * self.base:.2f}s")
            await self.outlet.turn_on()
            await asyncio.sleep(duration * self.base)
            await self.outlet.turn_off()
            await asyncio.sleep(0.2)

    @classmethod
    async def create(cls, outlet_spec, base_duration, *args):
        mode = args[0] if args else "tease"
        outlet = await cls.parse_outlet_spec(outlet_spec)
        return cls(outlet, base_duration, mode)

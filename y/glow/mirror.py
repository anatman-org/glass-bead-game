import asyncio
import sys
from typing import Optional, TextIO

from . import GlowBase


class MirrorGlow(GlowBase):
    """
    🪞 Mirror rhythm: responsive to external reflection

    Reads from a file-like source (default: stdin).
    Each line represents an impulse: "reflect", "reverse", "asymmetry", or "rest".
    This allows scripting or poetic ritual interaction.
    """

    def __init__(self, outlet, base_duration: float, source: Optional[TextIO] = None):
        super().__init__(outlet, base_duration)
        self.source = source or sys.stdin

    @classmethod
    async def create(cls, outlet_spec, base_duration: float, *unknown):
        outlet = await cls.parse_outlet_spec(outlet_spec)
        return cls(outlet, base_duration)

    async def glow(self) -> None:
        print("🪞 Mirror rhythm (listening mode) initiated")
        base = self.base

        loop = asyncio.get_event_loop()

        while True:
            line = await loop.run_in_executor(None, self.source.readline)
            if not line:
                await self.sleep(base * 2.0)
                continue

            cmd = line.strip().lower()
            if cmd == "reflect":
                print("🔲 Reflect command received")
                await self.outlet.turn_on()
                await self.sleep(base * 0.9)
                await self.outlet.turn_off()
                await self.sleep(base * 1.1)

            elif cmd == "reverse":
                print("🔁 Reverse command received")
                for _ in range(2):
                    await self.outlet.turn_on()
                    await self.sleep(base * 0.2)
                    await self.outlet.turn_off()
                    await self.sleep(base * 0.2)

            elif cmd == "asymmetry":
                print("🎭 Asymmetry command received")
                await self.outlet.turn_on()
                await self.sleep(base * 0.35)
                await self.outlet.turn_off()
                await self.sleep(base * 0.1)

            elif cmd == "rest":
                print("🌒 Rest command received")
                await self.sleep(base * 2.0)

            else:
                print(f"⚠️ Unknown command: {cmd.strip()} — skipping")

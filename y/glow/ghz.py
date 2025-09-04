from . import GlowBase


class GHZGlow(GlowBase):
    async def glow(self):
        print("✨ GHZ rhythm initiated: alternating long entangled pairs")
        while True:
            await self.outlet.turn_on()
            await self.sleep(self.base * 1.8)
            await self.outlet.turn_off()
            await self.sleep(self.base * 1.8)

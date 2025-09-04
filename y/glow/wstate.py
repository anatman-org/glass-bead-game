from . import GlowBase


class WStateGlow(GlowBase):
    async def glow(self):
        print("🌐 W-State rhythm initiated: soft, quick pulses with rests")
        while True:
            for _ in range(3):
                await self.outlet.turn_on()
                await self.sleep(self.base * 0.3)
                await self.outlet.turn_off()
                await self.sleep(self.base * 0.6)
            await self.sleep(self.base * 2.5)

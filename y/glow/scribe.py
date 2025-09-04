import asyncio
from . import GlowBase


class ScribeGlow(GlowBase):
    async def glow(self) -> None:
        print("📜 Scribe rhythm: return → center → gather")

        # Phase 1: Return
        for i in range(3):
            print(f"🔄 Returning step {i+1}")
            await self.outlet.turn_on()
            await asyncio.sleep(0.3 * self.base)
            await self.outlet.turn_off()
            await asyncio.sleep(0.3 * self.base)

        # Phase 2: Center
        print("🎯 Centering long breath")
        await self.outlet.turn_on()
        await asyncio.sleep(2.0 * self.base)
        await self.outlet.turn_off()
        await asyncio.sleep(0.5 * self.base)

        # Phase 3: Gather
        for i in range(5):
            print(f"🌀 Gathering pulse {i+1}")
            await self.outlet.turn_on()
            await asyncio.sleep(0.15 * self.base)
            await self.outlet.turn_off()
            await asyncio.sleep(0.15 * self.base)

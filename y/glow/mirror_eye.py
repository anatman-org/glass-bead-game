import asyncio
from . import GlowBase


class MirrorEyeGlow(GlowBase):
    async def glow(self) -> None:
        print("👁️ mirror_eye rhythm begins: reflective cycles by the Pond")
        base = self.base

        while True:
            print(f"🪷 On: holding light for {base:.2f}s")
            await self.outlet.turn_on()
            await asyncio.sleep(base * 0.6)

            print("🌫️ Peak pause")
            await asyncio.sleep(base * 0.1)

            print(f"🌒 Off: releasing light for {base:.2f}s")
            await self.outlet.turn_off()
            await asyncio.sleep(base * 0.6)

            # Occasional shimmer: faint chance of a quick flicker
            if asyncio.get_event_loop().time() % 10 < 1:
                print("✨ Ripple flicker")
                await self.outlet.turn_on()
                await asyncio.sleep(0.1)
                await self.outlet.turn_off()

            await asyncio.sleep(0.2)  # gentle stillness

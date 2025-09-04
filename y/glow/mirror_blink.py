import asyncio
from . import GlowBase


class MirrorBlinkGlow(GlowBase):
    async def glow(self) -> None:
        print("👁️ mirror_blink rhythm begins: inversion and intensity build")
        base = self.base
        step = 0
        max_duration = 2.1
        duration = 0.3 * self.base

        while True:
            mod7 = step % 7 == 6
            print(f"\n🔁 Step {step}: {'Inverted' if mod7 else 'Normal'}")

            # Inversion pattern every 7th step
            if mod7:
                print(f"🌑 Inverted: darkness first for {duration:.2f}s")
                await self.outlet.turn_off()
                await asyncio.sleep(duration / 2)
                await self.outlet.turn_on()
                await asyncio.sleep(duration / 2)
                await self.outlet.turn_off()
            else:
                print(f"🌕 Normal: light first for {duration:.2f}s")
                await self.outlet.turn_on()
                await asyncio.sleep(duration / 2)
                await self.outlet.turn_off()
                await asyncio.sleep(duration / 2)

            step += 1
            duration = min(0.3 + 0.2 * step, max_duration)

            # Every 21 steps, reflect deeply
            if step % 21 == 0:
                print(
                    f"✨ Full reflection at step {step}: holding light {base * 3:.2f}s"
                )
                await self.outlet.turn_on()
                await asyncio.sleep(base * 3)
                await self.outlet.turn_off()
                duration = 0.3

            await asyncio.sleep(0.2)

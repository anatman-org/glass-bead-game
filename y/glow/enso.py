from . import GlowBase


class EnsoGlow(GlowBase):
    async def glow(self):
        print("⟁ Enso rhythm initiated: entrance → drift → crescendo → flutter → fade")
        pace = self.base

        while True:

            # 1 ▸ Entrance (gentle, regular)
            for _ in range(8):
                await self.outlet.turn_on()
                await self.sleep(pace * 0.5)
                await self.outlet.turn_off()
                await self.sleep(pace * 0.5)

            # 2 ▸ Slow drift (rests stretch)
            for step in range(6):  # rests: 0.6→2.1 × base
                await self.outlet.turn_on()
                await self.sleep(pace * 0.6)
                await self.outlet.turn_off()
                await self.sleep(pace * (0.6 + step * 0.3))

            # 3 ▸ Mysterious build (tightening) + heart-flutter
            for step in range(10, 0, -1):  # pulses shorten 0.5→0.05 × base
                beat = pace * step / 20
                await self.outlet.turn_on()
                await self.sleep(beat)
                await self.outlet.turn_off()
                await self.sleep(beat / 2)

            # ─♥─ Triple flutter: the tilting desire
            for _ in range(3):
                await self.outlet.turn_on()
                await self.sleep(pace * 0.15)
                await self.outlet.turn_off()
                await self.sleep(pace * 0.15)

            # 4 ▸ Fade away (rests widen, bringing silence)
            for step in range(1, 6):  # rests: 1→5 × base
                await self.outlet.turn_on()
                await self.sleep(pace * 0.2)
                await self.outlet.turn_off()
                await self.sleep(pace * step)

            await self.sleep(self.base * 5)

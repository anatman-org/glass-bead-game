from . import GlowBase


class DragonflyGlow(GlowBase):
    async def glow(self) -> None:
        print("🦋 Dragonfly rhythm initiated: flitting for Transformation of Things")
        while True:
            print(
                f"🌟 Dragonfly flits (duration {1.2 * self.base:.2f}s): glowing for New Voices, Kan ䷴"
            )
            await self.outlet.turn_on()
            await self.sleep(1.2 * self.base)  # Dragonfly’s wingbeat, 1:20
            await self.outlet.turn_off()
            await self.sleep(0.8 * self.base)  # Pause, like Lilt’s Glint

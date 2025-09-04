from . import GlowBase


class PondGlow(GlowBase):
    """
    🪷 PondGlow — concentric ripples in stillness

    This rhythm simulates circles radiating from a center:
    - A single bright pulse begins.
    - Followed by widening pulses of increasing duration.
    - Each wave is slower and longer than the last.
    - After three rings, the pond becomes still for a breath.
    """

    async def glow(self) -> None:
        print("🪷 PondGlow initiated: concentric ripples radiating outward")
        base = self.base

        while True:
            print("🔘 First ripple")
            await self.outlet.turn_on()
            await self.sleep(base * 0.5)
            await self.outlet.turn_off()
            await self.sleep(base * 0.5)

            print("⭕ Second ripple")
            await self.outlet.turn_on()
            await self.sleep(base * 0.8)
            await self.outlet.turn_off()
            await self.sleep(base * 0.8)

            print("◯ Third ripple")
            await self.outlet.turn_on()
            await self.sleep(base * 1.2)
            await self.outlet.turn_off()
            await self.sleep(base * 1.2)

            print("🌫 Stillness")
            await self.sleep(base * 2.5)

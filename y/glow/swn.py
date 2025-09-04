from . import GlowBase


class SwnGlow(GlowBase):
    async def glow(self) -> None:
        print("🌾 Swn rhythm initiated: hexagrams unfolding as breath")
        yang = self.base * 0.6
        yin = self.base * 0.3

        # Binary from bottom to top:  y20 =  0 0 1 0 0 0   (Guan)
        hex20 = [0, 0, 1, 0, 0, 0]
        # y02 = 0 0 0 0 0 0   (Kun – pure yin)
        hex02 = [0, 0, 0, 0, 0, 0]

        while True:
            for bit in reversed(hex20):  # top‑down display feels like falling sand
                await self.outlet.turn_on()
                await self.sleep(yang if bit else yin)
                await self.outlet.turn_off()
                await self.sleep(yin if bit else yang)

            await self.sleep(self.base * 1.2)  # contemplative gap

            for bit in reversed(hex02):
                await self.outlet.turn_on()
                await self.sleep(yin)  # every line now the short pulse
                await self.outlet.turn_off()
                await self.sleep(yang)

            await self.sleep(self.base * 2.0)  # full breath before the next round

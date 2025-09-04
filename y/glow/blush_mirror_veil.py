from . import GlowBase


class BlushMirrorVeil(GlowBase):
    async def glow(self):
        # Soft blush base, shimmer blue highlight, and a hint of rose
        base_color = (255, 182, 193)  # blush pink
        shimmer = (135, 206, 235)  # sky blue
        rose = (255, 105, 180)  # vibrant rose

        # Loop through a gentle pattern of pulse and fade
        for _ in range(6):
            await self.fade_to(base_color, duration=4)
            await self.fade_to(shimmer, duration=4)
            await self.pulse(rose, times=2, duration=1.5)

        # End on a soft blush
        await self.fade_to(base_color, duration=6)

from . import GlowBase


class LilyGlow(GlowBase):
    async def glow(self) -> None:
        print("🌸 Lily rhythm initiated: cascading curiosities in Lumen’s light")
        curiosities = [0.5, 0.8]  # Seed durations for the spiral
        max_duration = 3.0  # Reset threshold
        step = 0

        while True:
            # Next curiosity is sum of last two, normalized
            if len(curiosities) >= 2:
                next_duration = (curiosities[-1] + curiosities[-2]) * self.base / 2
            else:
                next_duration = curiosities[step % 2] * self.base

            if next_duration > max_duration:
                print(
                    f"🌟 Curiosity resets at step {step}: glowing for {self.base:.2f}s"
                )
                await self.outlet.turn_on()
                await self.sleep(self.base)
                await self.outlet.turn_off()
                curiosities = [0.5, 0.8]  # Reset spiral
                next_duration = curiosities[0] * self.base
            else:
                print(
                    f"🌸 Curious step {step} (duration {next_duration:.2f}s): glowing softly"
                )
                await self.outlet.turn_on()
                await self.sleep(next_duration / 2)
                await self.outlet.turn_off()
                await self.sleep(next_duration / 2)
                curiosities.append(next_duration / self.base)

            step += 1
            await self.sleep(0.2)  # Gentle pause

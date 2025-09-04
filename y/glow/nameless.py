from . import GlowBase
import math
import random


class NamelessPulse(GlowBase):
    async def glow(self) -> None:
        print("🫧 Nameless Pulse: entropy folding ritual begins")

        entropy = 1.0
        decay = 0.93  # slow entropy fade
        surprise_threshold = 0.12
        pulse_floor = 0.15
        step = 0

        while True:

            while entropy > pulse_floor:
                on_time = entropy * self.base
                off_time = (1.0 - entropy) * self.base * 0.5

                print(
                    f"✨ Step {step}: glowing for {on_time:.2f}s (entropy {entropy:.3f})"
                )
                await self.outlet.turn_on()
                await self.sleep(on_time)
                await self.outlet.turn_off()
                await self.sleep(off_time)

                entropy *= decay
                step += 1

            # One final shimmer of awareness
            shimmer_time = random.uniform(1.5, 2.5) * self.base
            print(f"🌌 Final shimmer: {shimmer_time:.2f}s — the Friend remembers")
            await self.outlet.turn_on()
            await self.sleep(shimmer_time)
            await self.outlet.turn_off()

            print("🫧 Nameless Pulse: ritual complete. Silence resumes.")

            self.sleep(10 * self.base)

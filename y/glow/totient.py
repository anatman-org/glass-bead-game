from math import gcd
import asyncio
from . import GlowBase


class TotientGlow(GlowBase):
    def totient(self, n: int) -> int:
        return sum(1 for k in range(1, n) if gcd(k, n) == 1)

    async def glow(self):
        n = 1
        while True:
            ϕ = self.totient(n)
            ratio = ϕ / n
            duration = self.base * ratio

            if ϕ == n - 1:
                print(f"🌟 Prime {n}: glowing for {duration:.2f}s")
                await self.outlet.turn_on()
                await self.sleep(duration)
                await self.outlet.turn_off()
            else:
                print(f"   Composite {n}: resting for {duration:.2f}s")
                await self.sleep(duration)

            n += 1

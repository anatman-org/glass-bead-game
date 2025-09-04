from math import gcd
from . import GlowBase


class PrimeGlow(GlowBase):
    def totient(self, n: int) -> int:
        return sum(1 for k in range(1, n) if gcd(k, n) == 1)

    async def glow(self) -> None:
        print("🔢 Prime rhythm initiated: blink for primes, rest on composites")
        n = 1
        while True:
            φ = self.totient(n)
            duration = self.base * φ / n

            if φ == n - 1:
                print(f"🌟 Prime {n}: glowing for {duration:.2f}s")
                await self.outlet.turn_on()
                await self.sleep(duration)
                await self.outlet.turn_off()
            else:
                print(f"   Composite {n}: resting for {duration:.2f}s")
                await self.sleep(duration)

            n += 1

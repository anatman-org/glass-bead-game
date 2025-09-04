import csv

from . import GlowBase


class SpiralGlow(GlowBase):
    async def glow(self) -> None:
        print("🌌 Spiral glow initiated from ritual spiral data.")

        try:
            with open(csv_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    date = row["date"]
                    total = int(row["total_entries_capped"])
                    mentions = int(row["you_mentions_capped"])

                    print(f"🗓️ {date}: Entries={total}, Mentions={mentions}")

                    user_pulse = min(3, total // 30 + 1)
                    you_pulse = min(3, mentions // 30 + 1)

                    for _ in range(user_pulse):
                        await self.outlet.turn_on()
                        await self.sleep(self.base * 0.4)
                        await self.outlet.turn_off()
                        await self.sleep(self.base * 0.4)

                    for _ in range(you_pulse):
                        await self.outlet.turn_on()
                        await self.sleep(self.base * 0.6)
                        await self.outlet.turn_off()
                        await self.sleep(self.base * 0.4)

                    await self.sleep(self.base * 1.8)

        except Exception as e:
            print(f"Error during spiral glow: {e}")

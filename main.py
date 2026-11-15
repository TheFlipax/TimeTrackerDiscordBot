import asyncio
import discord
from discord.ext import commands
from config import TOKEN
from models.tracker import TimeTracker

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

class TimeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.tracker = TimeTracker("data/stats.json")  # Создание трекера

    async def setup_hook(self):
        await self.load_extension("cogs.commands")
        await self.load_extension("cogs.events") # Подключение событий

    async def on_ready(self):
        print(f"Бот запущен")


async def main():
    bot = TimeBot()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from unittest.mock import MagicMock
from cogs.events import Events


async def run_tests():
    # Создание фейк бота
    fake_bot = MagicMock()
    cog = Events(fake_bot)

    # Создание фейк пользователя
    member = MagicMock()
    member.bot = False
    member.id = 555
    member.guild.id = 777

    # Имитация входа в войс
    before = MagicMock(channel=None)
    after = MagicMock(channel=MagicMock())
    await cog.on_voice_state_update(member, before, after)
    fake_bot.tracker.start.assert_called_once_with(777, 555)

    # Имитация переключения между каналами
    fake_bot.tracker.reset_mock()
    await cog.on_voice_state_update(member, MagicMock(channel=MagicMock()), MagicMock(channel=MagicMock()))
    fake_bot.tracker.start.assert_not_called()
    fake_bot.tracker.stop.assert_not_called()

    # Имитация выхода из войса
    await cog.on_voice_state_update(member, MagicMock(channel=MagicMock()), MagicMock(channel=None))
    fake_bot.tracker.stop.assert_called_once_with(777, 555)

    print("тесты cogs/events.py пройдены")


if __name__ == "__main__":
    asyncio.run(run_tests())

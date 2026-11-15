import pytest
from unittest.mock import MagicMock
from cogs.events import Events


@pytest.fixture
def fake_bot():
    return MagicMock()

@pytest.fixture
def cog(fake_bot):
    return Events(fake_bot)

@pytest.fixture
def member():
    m = MagicMock()
    m.bot = False
    m.id = 555
    m.guild.id = 777
    return m

@pytest.mark.asyncio
async def test_voice_join(cog, fake_bot, member):
    before = MagicMock(channel=None)
    after = MagicMock(channel=MagicMock())

    await cog.on_voice_state_update(member, before, after)

    fake_bot.tracker.start.assert_called_once_with(777, 555)


@pytest.mark.asyncio
async def test_voice_channel_switch(cog, fake_bot, member):
    before = MagicMock(channel=MagicMock())
    after = MagicMock(channel=MagicMock())

    await cog.on_voice_state_update(member, before, after)

    fake_bot.tracker.start.assert_not_called()
    fake_bot.tracker.stop.assert_not_called()


@pytest.mark.asyncio
async def test_voice_leave(cog, fake_bot, member):
    before = MagicMock(channel=MagicMock())
    after = MagicMock(channel=None)

    await cog.on_voice_state_update(member, before, after)

    fake_bot.tracker.stop.assert_called_once_with(777, 555)

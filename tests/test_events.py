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
    m.guild.afk_channel = MagicMock()
    return m


@pytest.mark.asyncio
async def test_voice_join(cog, fake_bot, member):
    ch = MagicMock(id=10)
    before = MagicMock(channel=None)
    after = MagicMock(channel=ch)

    await cog.on_voice_state_update(member, before, after)

    fake_bot.tracker.start.assert_called_once_with(777, 555, 10)


@pytest.mark.asyncio
async def test_voice_channel_switch(cog, fake_bot, member):
    ch1 = MagicMock(id=10)
    ch2 = MagicMock(id=20)
    before = MagicMock(channel=ch1)
    after = MagicMock(channel=ch2)

    await cog.on_voice_state_update(member, before, after)

    fake_bot.tracker.start.assert_called_once_with(777, 555, 20)
    fake_bot.tracker.stop.assert_not_called()


@pytest.mark.asyncio
async def test_voice_leave(cog, fake_bot, member):
    ch = MagicMock(id=10)
    before = MagicMock(channel=ch)
    after = MagicMock(channel=None)

    await cog.on_voice_state_update(member, before, after)

    fake_bot.tracker.stop.assert_called_once_with(777, 555)


@pytest.mark.asyncio
async def test_voice_join_afk_ignored(cog, fake_bot, member):
    before = MagicMock(channel=None)
    after = MagicMock(channel=member.guild.afk_channel)

    await cog.on_voice_state_update(member, before, after)

    fake_bot.tracker.start.assert_not_called()
    fake_bot.tracker.stop.assert_not_called()


@pytest.mark.asyncio
async def test_voice_move_to_afk_stops_timer(cog, fake_bot, member):
    ch = MagicMock(id=10)
    before = MagicMock(channel=ch)
    after = MagicMock(channel=member.guild.afk_channel)

    await cog.on_voice_state_update(member, before, after)

    fake_bot.tracker.stop.assert_called_once_with(777, 555)
    fake_bot.tracker.start.assert_not_called()

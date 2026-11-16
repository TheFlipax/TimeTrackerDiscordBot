import pytest
from unittest.mock import AsyncMock, MagicMock
from cogs.commands import Commands


@pytest.fixture
def fake_bot():
    return MagicMock()


@pytest.fixture
def cog(fake_bot):
    return Commands(fake_bot)


@pytest.fixture
def ctx():
    c = MagicMock()
    c.send = AsyncMock()
    c.guild.id = 777
    c.author.id = 555
    c.author.display_name = "AuthorUser"
    return c


@pytest.mark.asyncio
async def test_ping(cog, ctx):
    await cog.ping.callback(cog, ctx)
    ctx.send.assert_called_once_with("в сети")


@pytest.mark.asyncio
async def test_stats_self(cog, fake_bot, ctx):
    fake_bot.tracker.get_user_seconds.return_value = 3661

    await cog.stats.callback(cog, ctx, None)

    fake_bot.tracker.get_user_seconds.assert_called_once_with(777, 555)
    ctx.send.assert_called_once_with(
        "⏱️ **AuthorUser** провел в голосовых каналах: **1 ч. 1 мин. 1 сек.**"
    )


@pytest.mark.asyncio
async def test_stats_other_member(cog, fake_bot, ctx):
    other = MagicMock(id=888, display_name="OtherUser")
    fake_bot.tracker.get_user_seconds.return_value = 120

    await cog.stats.callback(cog, ctx, other)

    fake_bot.tracker.get_user_seconds.assert_called_once_with(777, 888)
    ctx.send.assert_called_once_with(
        "⏱️ **OtherUser** провел в голосовых каналах: **0 ч. 2 мин. 0 сек.**"
    )


@pytest.mark.asyncio
async def test_duos_with_author(cog, fake_bot, ctx):
    other = MagicMock(id=888, display_name="OtherUser")
    fake_bot.tracker.get_duo_seconds.return_value = 50

    await cog.duos.callback(cog, ctx, other, None)

    fake_bot.tracker.get_duo_seconds.assert_called_once_with(777, 555, 888)
    ctx.send.assert_called_once_with(
        "🤝 **AuthorUser** и **OtherUser** провели вместе в голосовых каналах: **0 ч. 0 мин. 50 сек.**"
    )


@pytest.mark.asyncio
async def test_duos_same_user(cog, fake_bot, ctx):
    await cog.duos.callback(cog, ctx, ctx.author, None)

    fake_bot.tracker.get_duo_seconds.assert_not_called()
    ctx.send.assert_called_once_with("❌ Укажите другого участника.")


@pytest.mark.asyncio
async def test_top_empty(cog, fake_bot, ctx):
    fake_bot.tracker.get_top.return_value = []

    await cog.top.callback(cog, ctx)

    ctx.send.assert_called_once_with(
        "📊 Статистика пока пуста — никто еще не заходил в голосовые каналы."
    )


@pytest.mark.asyncio
async def test_top_with_users(cog, fake_bot, ctx):
    fake_bot.tracker.get_top.return_value = [(555, 168), (888, 50)]
    member1 = MagicMock(display_name="AuthorUser")
    ctx.guild.get_member.side_effect = lambda uid: member1 if uid == 555 else None

    await cog.top.callback(cog, ctx)

    expected = (
        "🏆 **Топ участников по времени в голосовых каналах:**\n\n"
        "**1.** AuthorUser — 0 ч. 2 мин. 48 сек.\n"
        "**2.** Пользователь (888) — 0 ч. 0 мин. 50 сек."
    )
    ctx.send.assert_called_once_with(expected)

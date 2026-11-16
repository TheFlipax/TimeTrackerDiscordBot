import discord
from discord.ext import commands


def format_time(total_seconds: int) -> str:
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours} ч. {minutes} мин. {seconds} сек."


class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        await ctx.send("в сети")

    @commands.command(name="stats")
    async def stats(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        total_seconds = self.bot.tracker.get_user_seconds(ctx.guild.id, target.id)

        await ctx.send(
            f"⏱️ **{target.display_name}** провел в голосовых каналах: **{format_time(total_seconds)}**"
        )

    @commands.command(name="duos")
    async def duos(
        self,
        ctx: commands.Context,
        member1: discord.Member,
        member2: discord.Member = None,
    ):
        first = ctx.author if member2 is None else member1
        second = member1 if member2 is None else member2

        if first.id == second.id:
            await ctx.send("❌ Укажите другого участника.")
            return

        total_seconds = self.bot.tracker.get_duo_seconds(ctx.guild.id, first.id, second.id)
        await ctx.send(
            f"🤝 **{first.display_name}** и **{second.display_name}** провели вместе в голосовых каналах: **{format_time(total_seconds)}**"
        )

    @commands.command(name="top")
    async def top(self, ctx: commands.Context):
        top_list = self.bot.tracker.get_top(ctx.guild.id, limit=10)

        if not top_list:
            await ctx.send("📊 Статистика пока пуста — никто еще не заходил в голосовые каналы.")
            return

        lines = ["🏆 **Топ участников по времени в голосовых каналах:**\n"]
        for index, (user_id, seconds) in enumerate(top_list, start=1):
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"Пользователь ({user_id})"
            lines.append(f"**{index}.** {name} — {format_time(seconds)}")

        await ctx.send("\n".join(lines))


async def setup(bot: commands.Bot):
    await bot.add_cog(Commands(bot))

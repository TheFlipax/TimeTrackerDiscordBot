import discord
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if member.bot:
            return

        if before.channel is None and after.channel is not None:
            self.bot.tracker.start(member.guild.id, member.id)

        elif before.channel is not None and after.channel is None:
            self.bot.tracker.stop(member.guild.id, member.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))

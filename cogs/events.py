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

        afk_channel = member.guild.afk_channel
        before_active = before.channel is not None and before.channel != afk_channel
        after_active = after.channel is not None and after.channel != afk_channel

        if not before_active and after_active:
            self.bot.tracker.start(member.guild.id, member.id, after.channel.id)

        elif before_active and not after_active:
            self.bot.tracker.stop(member.guild.id, member.id)

        elif before_active and after_active and before.channel != after.channel:
            self.bot.tracker.start(member.guild.id, member.id, after.channel.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))

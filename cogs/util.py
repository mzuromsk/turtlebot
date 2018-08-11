import discord
import asyncio
import turtlecheck

from discord.ext import commands

class UtilityControls:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def pingutility(self, ctx):
        await ctx.send('Pong!')

    @commands.command(description="This shuts down the bot process. Contact a bot administrator [Rev, Renay] if you need the bot shutdown.", brief="Shut down turtlebot. Requires bot administrator privileges.")
    @commands.check(turtlecheck.if_admin)
    async def shutdown(self, ctx):
        await ctx.message.delete()
        await self.bot.logout()
        await self.bot.close()


def setup(bot):
    bot.add_cog(UtilityControls(bot))

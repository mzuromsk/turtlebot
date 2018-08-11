import discord
import asyncio
import turtlecheck
from discord.ext import commands

class ApiControls:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def pingapi(self, ctx):
        await ctx.send('Pong!')

def setup(bot):
    bot.add_cog(ApiControls(bot))
import discord
import asyncio

from discord.ext import commands

class UtilityControls:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pingutility(self, ctx):
        await ctx.send('Pong!')

def setup(bot):
    bot.add_cog(UtilityControls(bot))

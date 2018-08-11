import discord
import asyncio

from discord.ext import commands

class ApiControls:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pingapi(self, ctx):
        await ctx.send('Pong!')

def setup(bot):
    bot.add_cog(ApiControls(bot))
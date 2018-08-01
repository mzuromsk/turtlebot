import discord
import asyncio

from discord.ext import commands

class Control:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    @commands.command()
    async def startfoodtimer(self, ctx, timerlength=30):
        self.keepLooping = True
        while self.keepLooping:
            try:
                print(timerlength)
                await ctx.send("Reminder: Eat your {0} min food & utility!".format(timerlength))
                await asyncio.sleep(timerlength*60)
            except:
                await ctx.send("Enter the time in minutes")
                self.keepLooping = False

    @commands.command()
    async def endfoodtimers(self, ctx):
        self.keepLooping = False

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')


def setup(bot):
    bot.add_cog(Control(bot))
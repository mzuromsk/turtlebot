import discord
import asyncio
import turtlecheck
from discord.ext import commands

class TextControls:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Dhuum monologue distilled to text. For mere mortals.')
    @commands.check(turtlecheck.if_seaguard)
    async def dhuumtypes(self, ctx):
        embed = discord.Embed(title='DHUUM', colour=0xb30000)
        embed.set_thumbnail(url='https://wiki.guildwars2.com/images/thumb/e/e9/Dhuum_full1.jpg/175px-Dhuum_full1.jpg')
        embed.add_field(name='...', value='MORTALS.', inline=False)
        embed.add_field(name='...', value='You believe yourselves saviors, naturally.', inline=False)
        embed.add_field(name='...', value='You seek to write the conclusion of your legend.', inline=False)
        embed.add_field(name='...', value='There is no conclusion more natural...', inline=False)
        embed.add_field(name='...', value='THAN DEATH.', inline=False)
        await ctx.send(embed=embed)

    @commands.command(brief='Glenna responds, because she is not your canine companion.')
    @commands.check(turtlecheck.if_seaguard)
    async def glenna(self, ctx):
        await ctx.send('I\'M NOT YOUR PUPPY!')

    @commands.command(brief='Wholesome mantra, courtesy Lyanna.')
    @commands.check(turtlecheck.if_seaguard)
    async def lyanna(self, ctx):
        await ctx.send('Everyone carries in their own special way!')

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def pingtext(self, ctx):
        await ctx.send('Pong!')

def setup(bot):
    bot.add_cog(TextControls(bot))
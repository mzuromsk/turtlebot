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

    @commands.command(hidden=True,brief='Dhuum monologue distilled to text. For mere mortals.')
    @commands.check(turtlecheck.if_seaguard)
    async def leaderboardmockup(self, ctx):
        embed = discord.Embed(title='__**The Leaderboard  |  Grand Siege Turtle Games: Season 1**__', colour=0x76AFA5, url='https://www.youtube.com/watch?v=9jK-NcRmVcw&mute=1')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.set_footer(text='Time at last successful turtle progression: Sunday 10th, 12:01AM', icon_url='https://cdn.discordapp.com/attachments/471547983859679232/478072773659328524/108145_time_512x512.png')
        embed.add_field(name='1) **Renay** __**[Finished!]**__', value='~~__**|#1|#2|#3|#4|#5|#6|#7|#8|#9|#10|#11|#12|#13|#14|#15|**__~~', inline=False)
        embed.add_field(name='2) **Rev** *(@ 11:59PM)*  ', value='__**|#1|#2|#3|#4|#5|#6|#7|#8|#9|**__', inline=False)
        embed.add_field(name='3) **Kusi** *(@ 12:01AM)*   ', value='__**|#1|#2|#3|#4|#5|#6|#7|#8|#9|**__', inline=False)
        embed.add_field(name='4) **Lyanna**', value='__**|#1|#2|#3|#4|#5|#6|#7|**__', inline=False)
        embed.add_field(name='5) **Tyr** *(@ 10:59PM)* ', value='__**|#1|#2|#3|#4|#5|#6|**__', inline=False)
        embed.add_field(name='6) **Turtle** *(@ 11:00PM)* ', value='__**|#1|#2|#3|#4|#5|#6|**__', inline=False)
        embed.add_field(name='7) **Turtle**', value='__**|#1|#2|#3|#4|**__', inline=False)
        embed.add_field(name='8) **Turtle**', value='__**|#1|#2|#3|**__', inline=False)
        embed.add_field(name='9) **Turtle**', value='__**|#1|#2|**__', inline=False)
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
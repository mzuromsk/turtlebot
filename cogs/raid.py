import discord
import asyncio
import turtlecheck
import turtle_credentials as tc

from discord.ext import commands

class RaidControls:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Returns the current weekly raid schedule.')
    @commands.check(turtlecheck.if_seaguard)
    async def schedule(self, ctx):
        await ctx.send('Raids are at reset on Monday, and reset + 1 hour on Thursday.')
        await ctx.send('Reset is currently at 8pm Eastern US Time.')

    @commands.command(brief='Return the time until the next scheduled raid.')
    @commands.check(turtlecheck.if_seaguard)
    async def raidtime(self, ctx):
        try:
            conn
        except NameError:
            conn = tc.get_conn()
        cur = conn.cursor()
        cur.execute("""WITH next_raid AS (SELECT min(time_of_raid) as next_raid_time FROM turtle.raid_schedule WHERE is_raid AND time_of_raid > NOW() - INTERVAL '4 hour') SELECT  next_raid_time - (now() - INTERVAL '4 hour') FROM next_raid""")
        result = cur.fetchall()
        await ctx.send('The next raid is in:')
        await ctx.send(result[0][0])

    @commands.command(brief='Planning to pregame? Time till you should start.')
    @commands.check(turtlecheck.if_seaguard)
    async def pregame(self, ctx):
        try:
            conn
        except NameError:
            conn = tc.get_conn()
        cur = conn.cursor()
        cur.execute("""WITH next_raid AS (SELECT min(time_of_raid) as next_raid_time FROM turtle.raid_schedule WHERE is_raid AND time_of_raid > NOW() - INTERVAL '4 hour') SELECT  next_raid_time - (now() - INTERVAL '4 hour') - INTERVAL '1 hour' FROM next_raid""")
        result = cur.fetchall()
        await ctx.send('Start drinking in:')
        await ctx.send(result[0][0])

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def pingraid(self, ctx):
        await ctx.send('Pong!')

def setup(bot):
    bot.add_cog(RaidControls(bot))
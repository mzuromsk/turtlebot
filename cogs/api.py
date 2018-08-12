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

    @commands.command(description="After entering this command, the bot will direct message the user to request a GW2 API key. This key will be saved in a database and linked with the discord account. Future bot commands will query the GW2 API for your account.", brief = "Set a GW2 API key to be used for API discord commands.")
    @commands.check(turtlecheck.if_seaguard)
    async def set_api_key(self, ctx):
        await ctx.message.delete()
        out = 'Enter the `GW2 API key` that you wish to link with your discord account into the message below then send.\n```md\n# Notes: Your API key will be saved to an online database and linked to your discord account. You only need to update your API code if you would like to change permissions. \nOnly bot administers will have access to the database [Rev, Renay]. \n# You may choose to limit your permissions for your provided API key, but this may block some bot functionality.\nTo get a GW2 API Key, go here: https://account.arena.net/applications.```'
        try:
            message = await ctx.author.send(out)
        except discord.Forbidden:
            return await ctx.send('I do not have permission to DM you. Please enable this in the future.')

        def m_check(m):
            return m.author == ctx.author and m.channel == message.channel

        try:
            ans = await self.bot.wait_for('message', check=m_check, timeout=300.0)
        except asyncio.TimeoutError:
            await ctx.author.send('Sorry. You took to long to enter your key. If you would like to retry, re-enter the command in a text channel and the bot will re-message you.')
        else:
            await ctx.author.send('You entered the following GW2 API key: `{0}` ```\nThis key has been linked to your discord username. If you would like to update it in the future, just re-run this command from any text channel.```'.format(ans.content))
            #TODO: Add some kind of input check and add the GW2 API key to the database

        await message.delete()

    @commands.command(description="After entering this command, the bot will direct message the user to confirm that you would like to delete your GW2 API key.", brief = "Delete your GW2 API key.")
    @commands.check(turtlecheck.if_seaguard)
    async def clear_api_key(self, ctx):
        await ctx.message.delete()
        out = 'Please confirm that you would like to delete your key (if you change your mind at a later date, you will have to re-set it). ```\nClick ✅ to confirm, ❌ to cancel```'
        try:
            message = await ctx.author.send(out)
            await message.add_reaction('✅')
            await message.add_reaction('❌')
        except discord.Forbidden:
            return await ctx.send('I do not have permission to DM you. Please enable this in the future.')

        def r_check(r, user):
            return user == ctx.author and r.count > 1

        try:
            ans, user = await self.bot.wait_for('reaction_add', check=r_check, timeout=300.0)
        except asyncio.TimeoutError:
            await ctx.author.send('Sorry. You took to long to select your choice. If you would like to retry, re-enter the command in a text channel and the bot will re-message you.')
        else:
            if str(ans.emoji) == '✅':
                await ctx.author.send('Your GW2 API key has been deleted.')
                #TODO: Clear GW2 API key from the database

            if str(ans.emoji) == '❌':
                await ctx.author.send('Your GW2 API key has been preserved...for now.')
        await message.delete()

def setup(bot):
    bot.add_cog(ApiControls(bot))
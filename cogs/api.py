import discord
import asyncio
import turtlecheck
from discord.ext import commands
import psycopg2
import turtle_credentials as tc

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
            api_key = ans.content
            discord_id = ctx.author.id
            if check_valid_api_key(api_key):   
                try:
                    try:
                        conn
                    except NameError:
                        conn = tc.get_conn()
                    cur = conn.cursor()
                    #get the id of any existing key for this person
                    sqlStr = "SELECT id FROM turtle.api_keys WHERE discord_id = " + str(discord_id)
                    cur.execute(sqlStr)
                    result = cur.fetchall()
                    try:
                        to_be_deleted = result[0][0]
                        if to_be_deleted is None:
                            to_be_deleted = -1
                    except:
                        to_be_deleted = -1
                    sqlStr = "INSERT INTO turtle.api_keys (discord_id, api_key) VALUES (" + str(discord_id) + ", '" + api_key + "');"
                    cur.execute(sqlStr)
                    conn.commit()
                    #now that we've successfully inserted, delete the previous key
                    if to_be_deleted != -1:
                        sqlStr = "DELETE FROM turtle.api_keys WHERE id = " + str(to_be_deleted)
                        print(sqlStr)
                        cur.execute(sqlStr)
                        conn.commit()
                    await ctx.author.send('You entered the following GW2 API key: `{0}` ```\nThis key has been linked to your discord username. If you would like to update it in the future, just re-run this command from any text channel.```'.format(ans.content))
                except:
                   await ctx.author.send('Something went wrong.  Tell Rev, he wrote this part')
            else:
                await ctx.author.send('That API key looks like it is the wrong length, or something.  Ask Rev to take a look')

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
                sqlStr = "DELETE FROM turtle.api_keys WHERE discord_id = " + str(ctx.author.id)
                try:
                    conn
                except NameError:
                    conn = tc.get_conn()
                cur = conn.cursor()
                cur.execute(sqlStr)
                conn.commit()
                await ctx.author.send('Your GW2 API key has been deleted.')                
            if str(ans.emoji) == '❌':
                await ctx.author.send('Your GW2 API key has been preserved...for now.')
        await message.delete()
        

def get_api_key(discord_id):
    try:
        sqlStr = "SELECT api_key FROM turtle.api_keys WHERE discord_id = "  + str(discord_id)
        try:
            conn
        except NameError:
            conn = tc.get_conn()
        cur = conn.cursor()
        cur.execute(sqlStr)
        result = cur.fetchall()
        try:
            return result[0][0]
        except:
            return None
    except:
        return None

def setup(bot):
    bot.add_cog(ApiControls(bot))


def check_valid_api_key(key):
    try:
        return len(key) == 72
    except:
        return False
    return False

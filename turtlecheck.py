import discord
import asyncio
import psycopg2
import turtle_credentials as tc
from discord.ext import commands

async def if_admin(ctx):
    if ctx.message.author.id == tc.get_renay_id() or ctx.message.author.id == tc.get_rev_id():
        return True
    else:
        await ctx.send('Sorry, you need to be a bot administrator to use this command. Please contact Rev or Renay.')
        return False

async def if_seaguard(ctx):
    if ctx.message.author.id == tc.get_renay_id() or ctx.message.author.id == tc.get_rev_id() or ctx.message.author.id == tc.get_kusi_id():
        return True
    for role in ctx.message.author.roles:
        #Check if seaguard
        if role.id == tc.get_seaguard_id():
            return True

    await ctx.send('Sorry, you need to be a Seaguard to use my commands. Please let a mod or admin know if your rank needs to upgraded.')
    return False

async def if_mod(ctx):
    if ctx.message.author.id == tc.get_renay_id() or ctx.message.author.id == tc.get_rev_id() or ctx.message.author.id == tc.get_kusi_id():
        return True
    for role in ctx.message.author.roles:
        if role.id == tc.get_mod_id():
            return True

    await ctx.send('Sorry, you need to be a server moderator to use this command.')
    return False

async def if_raider(ctx):
    if ctx.message.author.id == tc.get_renay_id() or ctx.message.author.id == tc.get_rev_id() or ctx.message.author.id == tc.get_kusi_id():
        return True
    for role in ctx.message.author.roles:
        #Check if seaguard
        if role.id == tc.get_raider_id():
            return True

    await ctx.send('Sorry, you need to be a Raider to use this command. Please let a mod or admin know if your rank needs to upgraded.')
    return False

async def if_api_key(ctx):
    if get_api_key(ctx.message.author.id) is not None:
        return True
    else:
        await ctx.message.author.send('```Sorry, this command requires API functionality and you do not currently have a GW2 API key linked to your discord account.```' + '```In order to set an API key, use the command $set_api_key in any guild text channel.```')
        return False

def has_unlocked_hidden_key(current_question_step):
    async def predicate(ctx):
        if get_active_step(ctx.message.author.id) >= current_question_step:
            return True
        else:
            game_id = get_active_game()
            if game_id == -1:
                await ctx.message.author.send('```That hidden key belongs to a Grand Game that is not currently active. If you believe you\'ve received this message in error, let Rev or Renay know.```')
            else:
                await ctx.message.author.send('```Hmmm, seem\'s like you might be ahead of the game. *Cough*```' + '```You haven\'t unlocked the ability to use that hidden key yet. To unlock it, make sure you have earned all prior keys.```')
            return False
    return commands.check(predicate)

async def if_active_game(ctx):
    game_id = get_active_game()
    if game_id == -1:
        await ctx.message.author.send('```That hidden key belongs to a Grand Game that is not currently active. If you believe you\'ve received this message in error, let Rev or Renay know.```')
        return False
    else:
        return True


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

def get_active_step(discord_id):
    game_id = get_active_game()
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()

    sqlStr = "SELECT max(step_id) FROM turtle.game_step_completions WHERE discord_id = " + str(discord_id) + " AND game_id = " + str(game_id) + ";"
    cur.execute(sqlStr)
    result = cur.fetchall()
    try:
        if result[0][0] is None:
            return 1  #If no compelted steps, active step is 1
        max_completed_step =  result[0][0]
        return max_completed_step + 1 # active step is 1 more than max_completed_step
    except:
        return 1

def get_active_game():
    try:
        conn
    except NameError:
        conn = tc.get_conn()
    cur = conn.cursor()
    sqlStr = "SELECT game_id FROM turtle.grand_games WHERE is_active = TRUE;"
    cur.execute(sqlStr)
    result = cur.fetchall()
    try:
        return result[0][0]
    except:
        return -1
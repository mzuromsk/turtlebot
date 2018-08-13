import discord
import asyncio

import turtle_credentials as tc

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
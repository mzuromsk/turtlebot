import discord
import asyncio
import time
from discord.ext import commands

#import turtle_credentials as tc
import turtle_credentials_phantom as tc

import aiohttp

import logging

timestring = time.strftime("%m-%d-%Y_%I_%M%p")

logging.basicConfig(filename='logs/turtlebot_{0}.log'.format(timestring),level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

from cogs.exceptions import APIError, APIInactiveError, APIInvalidKey, APIKeyError

extensions = ['cogs.voice', 'cogs.text', 'cogs.raid', 'cogs.api', 'cogs.util', 'cogs.grandturtlegame', 'cogs.easter_egg', 'cogs.tutorialgame']

class TurtleBot(commands.Bot):
    def __init__(self):
        prefix = tc.get_prefix()
        super().__init__(command_prefix=prefix, case_insensitive=True)
        self.session = aiohttp.ClientSession(loop=self.loop)

        for ext in extensions:
            try:
                self.load_extension(ext)
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(ext, exc))

    async def on_ready(self):
        print('Connected to the server!')
        logging.info('Connected to the server!')
        print('Username: {0.name}\nID: {0.id}'.format(self.user))
        logging.info('Username: {0.name}\nID: {0.id}'.format(self.user))

    async def on_command_error(self, ctx, error):
        logging.info("Error for {}: {}".format(ctx.message.author.name,error))
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            await ctx.message.author.send('That command is still on cooldown. You can retry it in `{0:.0f}min and {1:.0f}s`.'.format(m, s))
        if isinstance(error, APIKeyError):
            await ctx.message.author.send(error)
        if isinstance(error, APIInactiveError):
            await ctx.message.author.send("{0}, the API is currently down. Try again later.".format(ctx.message.author))
        if isinstance(error, APIInvalidKey):
            await ctx.message.author.send("{0}, your API key is invalid! Remove your key and add a new one".format(ctx.message.author))
        if isinstance(error, APIError):
            await ctx.message.author.send("{0}, API has responded with the following error: `{1}`".format(user, error))
        raise error

    async def on_message(self, message):
        if message.content.startswith('$'):
            logging.info('{} entered command {}'.format(message.author.name, message.content))
        if not message.author.bot:
            await self.process_commands(message)
        if message.content.startswith('$game'):
            try:
                await message.delete()
            except:
                return
        if message.content.startswith('$key'):
            try:
                await message.delete()
                await message.author.send('You entered the following potential hidden key command: `{0}`.```If this was a correct hidden key, the bot will either message you with the next game card or its cooldown. If not, feel free to try again.```'.format(message.content))
            except:
                return

token = tc.get_pk()

bot = TurtleBot()
bot.run(token)





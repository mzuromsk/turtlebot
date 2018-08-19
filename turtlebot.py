import discord
import asyncio
from discord.ext import commands

#import turtle_credentials as tc
import turtle_credentials_phantom as tc

import aiohttp



from cogs.exceptions import APIError, APIInactiveError, APIInvalidKey, APIKeyError

extensions = ['cogs.voice', 'cogs.text', 'cogs.raid', 'cogs.api', 'cogs.util', 'cogs.grandturtlegame']

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
        print('Username: {0.name}\nID: {0.id}'.format(self.user))

    async def error_handler(self, ctx, exc):
        user = ctx.author
        if isinstance(exc, APIKeyError):
            await ctx.send(exc)
            return
        if isinstance(exc, APIInactiveError):
            await ctx.send("{.mention}, the API is currently down. "
                           "Try again later.".format(user))
            return
        if isinstance(exc, APIInvalidKey):
            await ctx.send("{.mention}, your API key is invalid! Remove your "
                           "key and add a new one".format(user))
            return
        if isinstance(exc, APIError):
            await ctx.send(
                "{.mention}, API has responded with the following error: "
                "`{}`".format(user, exc))
            return

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)
        if message.content.startswith('$game'):
            try:
                await message.delete()
            except:
                return

token = tc.get_pk()

bot = TurtleBot()
bot.run(token)





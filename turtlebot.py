import discord
import asyncio
from discord.ext import commands

import turtle_credentials as tc
#import turtle_credentials_phantom as tc

extensions = ['cogs.voice', 'cogs.text', 'cogs.raid', 'cogs.api', 'cogs.util']

class TurtleBot(commands.Bot):
    def __init__(self):
        prefix = tc.get_prefix()
        super().__init__(command_prefix=prefix, case_insensitive=True)

        for ext in extensions:
            try:
                self.load_extension(ext)
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print('Failed to load extension {}\n{}'.format(ext, exc))

    async def on_ready(self):
        print('Connected to the server!')
        print('Username: {0.name}\nID: {0.id}'.format(self.user))

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

token = tc.get_pk()

bot = TurtleBot()
bot.run(token)





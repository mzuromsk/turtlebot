import discord
import asyncio
from discord.ext import commands

import turtle_credentials as tc
extensions = ['cogs.control']



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
##        for guild in self.guilds:
##            for channel in guild.channels:
##                print('Channel ID: {0} | Channel Name: {1}'.format(channel.id,channel.name))
##            print('-------------------')
##            print('Users:')
##            for member in guild.members:
##                print('Member ID: {0} | Member Name: {1} | Member Nickname: {2}'.format(member.id, member.name, member.nick))

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

        if message.content.startswith('!deleteme'):
            await message.delete()

        elif message.content.startswith('!help'):
            await message.channel.send('List of currently active commands:')
            await message.channel.send('type \'!schedule\' - will print the current raid schedule')
            await message.channel.send('type \'!raidtime\' - CURRENTLY UNAVAILABLE')
            await message.channel.send('type \'!pregame\' - ALSO UNAVAILBLE')

        elif message.content.startswith('!raidtime'):
            try:
                conn
            except NameError:
                conn = tc.get_conn()
            cur = conn.cursor()
            cur.execute("""WITH next_raid AS (SELECT min(time_of_raid) as next_raid_time FROM turtle.raid_schedule WHERE is_raid AND time_of_raid > NOW() - INTERVAL '4 hour') SELECT  next_raid_time - (now() - INTERVAL '4 hour') FROM next_raid""")
            result = cur.fetchall()
            await message.channel.send('The next raid is in:')
            await message.channel.send(result[0][0])

        elif message.content.startswith('!pregame'):
            try:
                conn
            except NameError:
                conn = tc.get_conn()
            cur = conn.cursor()
            cur.execute("""WITH next_raid AS (SELECT min(time_of_raid) as next_raid_time FROM turtle.raid_schedule WHERE is_raid AND time_of_raid > NOW() - INTERVAL '4 hour') SELECT  next_raid_time - (now() - INTERVAL '4 hour') - INTERVAL '1 hour' FROM next_raid""")
            result = cur.fetchall()
            await message.channel.send('Start drinking in:')
            await message.channel.send(result[0][0])

        elif message.content.startswith('!dhuumtypes'):
            embed = discord.Embed(title='DHUUM', colour=0xb30000)
            embed.set_thumbnail(url='https://wiki.guildwars2.com/images/thumb/e/e9/Dhuum_full1.jpg/175px-Dhuum_full1.jpg')
            embed.add_field(name='...', value='MORTALS.', inline=False)
            embed.add_field(name='...', value='You believe yourselves saviors, naturally.', inline=False)
            embed.add_field(name='...', value='You seek to write the conclusion of your legend.', inline=False)
            embed.add_field(name='...', value='There is no conclusion more natural...', inline=False)
            embed.add_field(name='...', value='THAN DEATH.', inline=False)
            await message.channel.send(embed=embed)

        elif message.content.startswith('!isdhuumdead'):
            await message.channel.send('Still alive :cry:')

        elif message.content.startswith('!schedule'):
            await message.channel.send('Raids are at reset on Monday, and reset + 1 hour on Thursday')
            await message.channel.send('Reset is currently at 8pm Eastern US Time.')

        elif message.content.startswith('!glenna'):
            await message.channel.send('/tts I\'M NOT YOUR PUPPY!')
            await self

        elif message.content.startswith('!lyanna'):
            await message.channel.send('Everyone carries in their own special way!')




token = tc.get_pk()

bot = TurtleBot()
bot.run(token)





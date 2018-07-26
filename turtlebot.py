import discord
import asyncio


client = discord.Client()
      


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-=-=-=-=')


@client.event
async def on_message(message):
    timestamp = message.timestamp
    weekday = timestamp.weekday()
    hour = timestamp.hour
    if message.content.startswith('!help'): 
        await client.send_message(message.channel, 'List of currently active commands:')
        await client.send_message(message.channel, 'type \'!schedule\' - will print the current raid schedule')
        await client.send_message(message.channel, 'type \'!raidtime\' - CURRENTLY UNAVAILABLE')
        await client.send_message(message.channel, 'type \'!pregame\' - ALSO UNAVAILBLE')
        #await client.send_message(message.channel, 'type \'!botinfo\' - bot will tell you its username')
    elif message.content.startswith('!raidtime'):        
        await client.send_message(message.channel, 'currently borked, sorry')
    elif message.content.startswith('!pregame'):        
        await client.send_message(message.channel, 'currently borked, sorry')     
    elif message.content.startswith('!dhuum'): 
        await client.send_message(message.channel, 'MORTALS.')
        await client.send_message(message.channel, 'You believe yourselves saviors, naturally.')
        await client.send_message(message.channel, 'You seek to write the conclusion of your legend.')
        await client.send_message(message.channel, 'There is no conclusion more natrual...')
        await client.send_message(message.channel, 'THAN DEATH')
    elif message.content.startswith('!isdhuumdead'):
        await client.send_message(message.channel, 'Still alive :cry:')   
    elif message.content.startswith('!schedule'): 
        await client.send_message(message.channel, 'Raids are at reset on Monday, and reset + 1 hour on Thursday')
        await client.send_message(message.channel, 'Reset is currently at 8pm Eastern US Time.')
    elif message.content.startswith('!kusi'): 
        await client.send_message(message.channel, 'Kusi\'s status:  Flyboye.')
    elif message.content.startswith('!glenna'):
        await client.send_message(message.channel, 'I\'M NOT YOUR PUPPY!')
    elif message.content.startswith('!lyanna'):
        await client.send_message(message.channel, 'Everyone carries in their own special way!')
    


    

client.run('NDU4MjcxNTkzNjk3OTAyNjAy.DigfxA.V9Aqd7Hd6jZJk35A8s96J6ADPeE')


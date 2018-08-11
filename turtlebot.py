import discord
import asyncio
import turtle_credentials as tc

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
        await client.send_message(message.channel, 'type \'!raidtime\' -  will tell you how long until the next raid')
        await client.send_message(message.channel, 'type \'!pregame\' - will tell you how long until you should start drinking for the next raid')        
    elif message.content.startswith('!raidtime'):        
        try:
            conn
        except NameError:
            conn = tc.get_conn()
        cur = conn.cursor()
        cur.execute("""WITH next_raid AS (SELECT min(time_of_raid) as next_raid_time FROM turtle.raid_schedule WHERE is_raid AND time_of_raid > NOW() - INTERVAL '4 hour') SELECT  next_raid_time - (now() - INTERVAL '4 hour') FROM next_raid""")
        result = cur.fetchall()
        await client.send_message(message.channel, 'The next raid is in:')
        await client.send_message(message.channel, result[0][0])
    elif message.content.startswith('!pregame'):        
        try:
            conn
        except NameError:
            conn = tc.get_conn()
        cur = conn.cursor()
        cur.execute("""WITH next_raid AS (SELECT min(time_of_raid) as next_raid_time FROM turtle.raid_schedule WHERE is_raid AND time_of_raid > NOW() - INTERVAL '4 hour') SELECT  next_raid_time - (now() - INTERVAL '4 hour') - INTERVAL '1 hour' FROM next_raid""")
        result = cur.fetchall()
        await client.send_message(message.channel, 'Start drinking in:')
        await client.send_message(message.channel, result[0][0])     
    elif message.content.startswith('!dhuum'): 
        await client.send_message(message.channel, 'MORTALS.')
        await client.send_message(message.channel, 'You believe yourselves saviors, naturally.')
        await client.send_message(message.channel, 'You seek to write the conclusion of your legend.')
        await client.send_message(message.channel, 'There is no conclusion more natrual...')
        await client.send_message(message.channel, 'THAN DEATH')
    elif message.content.startswith('!isdhuumdead'):
        await client.send_message(message.channel, 'DHUUM IS FUCKING DEAD :D :D :D :D :D')   
    elif message.content.startswith('!schedule'): 
        await client.send_message(message.channel, 'Raids are at reset on Monday, and reset + 1 hour on Thursday')
        await client.send_message(message.channel, 'Reset is currently at 8pm Eastern US Time.')
    elif message.content.startswith('!kusi'): 
        await client.send_message(message.channel, 'Kusi\'s status:  Flyboye.')
    elif message.content.startswith('!glenna'):
        await client.send_message(message.channel, 'I\'M NOT YOUR PUPPY!')
    elif message.content.startswith('!lyanna'):
        await client.send_message(message.channel, 'Everyone carries in their own special way!')
    

print('connecting')
private_key = tc.get_pk()#grabs the private token for turtlebot
client.run(private_key)



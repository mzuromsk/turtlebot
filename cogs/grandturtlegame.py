import discord
import asyncio
import turtlecheck
from discord.ext import commands

class GrandTurtleGameControls:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def pingturtlegamecontrols(self, ctx):
        await ctx.send('That was correct.')

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def game_test_update_gameturn(self, ctx, turn=0):
        #Make sure the message gets deleted before someone else can see it (in case the general flag doesn't catch it)
        try:
            await ctx.message.delete()
        except:
            pass

        out = 'Just click the checkmark already. '
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
            await ctx.author.send('Sorry. You took too long to select your choice. If you would like to retry, re-enter the command in a text channel and the bot will re-message you.')
        else:
            if str(ans.emoji) == '✅':
                await ctx.author.send('Pretending you answered something correct. This should mark the flag for the {0} turn correct and update the step number. If I didn\'t break something you should be able to run the next command.'.format(turn))
                #TODO: Write a function that will update the db with current progress of the user
                # You can use "turn" as the parameter to be updated in the table, so we can use this for testing
                # i.e. game_test_update_gameturn 3 should act as if just completed the 3rd step
                #
                #
                #

                await self.game_update_leaderboard(ctx, turn)
            if str(ans.emoji) == '❌':
                await ctx.author.send('Why cancel? Okay, canceled.')

        await message.delete()

    @commands.command(hidden=True)
    @commands.cooldown(1,180,commands.BucketType.user)
    @commands.check(turtlecheck.if_seaguard)
    #TODO: Figure out if there is a way to catch the cooldown error. It currently nicely prints out a You are on cooldown. Try again in [time]. It would be nice to send that to ctx.
    async def game_example_send_audio_pickone(self, ctx):
        #Make sure the message gets deleted before someone else can see it (in case the general flag doesn't catch it)
        try:
            await ctx.message.delete()
        except:
            pass

        out = 'You stand at the center of Divinity\'s Reach. To unlock the next clue, select the correct direction from the choices below based on the audio hint. \n\n**Answer advice: you only get to pick one answer. The first reaction you click will be your selection.** \n\n*Be careful, if you choose wrong, you will have to re-enter this command in a text window again (but it has a cooldown of 3 minutes).*\n\n\n\n'
        reactionout = 'Choose the correct direction from the indicated choices by clicking that reaction.'
        audio = discord.File('audio/NobodyLikesYouKormir.mp3', filename="YourNextHint.mp3")

        try:
            next_clue = await ctx.author.send(content=out,file=audio)
            message = await ctx.author.send(reactionout)
            await message.add_reaction('\U00002B05')
            await message.add_reaction('\U00002196')
            await message.add_reaction('\U00002B06')
            await message.add_reaction('\U00002197')
            await message.add_reaction('\U000027A1')
            await message.add_reaction('\U00002198')
            await message.add_reaction('\U00002B07')
            await message.add_reaction('\U00002199')

        except discord.Forbidden:
            return await ctx.send('I do not have permission to DM you. Please enable this in the future.')

        def r_check(r, user):
            return user == ctx.author and r.count > 1

        try:
            ans, user = await self.bot.wait_for('reaction_add', check=r_check, timeout=300.0)
        except asyncio.TimeoutError:
            await ctx.author.send('Sorry. You took to long to select your choice. If you would like to retry, re-enter the command in a text channel and the bot will re-message you. Be aware that this command does have a cooldown of 3 minutes.')
        else:
            if str(ans.emoji) == '\U00002198':
                await ctx.author.send('Correct.')
            else:
                await ctx.author.send('Sorry, you didn\'t make the correct selection, you can try again after the 3 minute cooldown is up on this command.')
        await message.delete()


    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def game_example_send_picture_clue(self, ctx):
        #Make sure the message gets deleted before someone else can see it (in case the general flag doesn't catch it)
        try:
            await ctx.message.delete()
        except:
            pass

        out = 'Pack something warm. To unlock the next clue, enter the answer to the following question. (Use the image to guide you). \n\n**What is the name of the next closest point of interest following the road that crosses between feline and fowl?** \n\n[Format advice: enter the name of the POI as written in game, not as a discord command. Watch your spelling and punctuation!]\n\n'
        image = discord.File('images/Wayfarer.png')
        correct_answer = 'Victor\'s Point'

        try:
            next_clue = await ctx.author.send(content=out,file=image)

        except discord.Forbidden:
            return await ctx.send('I do not have permission to DM you. Please enable this in the future.')

        def m_check(m):
            return m.author == ctx.author and m.channel == next_clue.channel

        guess_count = 0
        time_until_message_disappears = 300

        while guess_count < 5:
            try:
                ans = await self.bot.wait_for('message', check=m_check, timeout=time_until_message_disappears)
            except asyncio.TimeoutError:
                await ctx.author.send('Sorry. You took too long to enter your answer. If you would like to retry, re-enter the command in a text channel and the bot will re-message you.')
                return
            else:
                if(str(ans.content).lower())==correct_answer.lower():
                    await ctx.author.send('You were correct!')
                    return
                else:
                    guess_count = guess_count+1
                    await ctx.author.send('You were not correct! You may try again. You have 2 minutes to make your next guess.')
                    time_until_message_disappears = 120
                    if guess_count == 5:
                        await ctx.author.send('You have run out of guesses.')



    @commands.command(hidden=True, description="After entering this command, the bot will direct message the user to request a GW2 API key. This key will be saved in a database and linked with the discord account. Future bot commands will query the GW2 API for your account.", brief = "Set a GW2 API key to be used for API discord commands.")
    @commands.check(turtlecheck.if_seaguard)
    async def game_example_combination_lock(self, ctx):
        #Make sure the message gets deleted before someone else can see it (in case the general flag doesn't catch it)
        try:
            await ctx.message.delete()
        except:
            pass

        out = 'Please enter the correct combination. You only get one try.'
        try:
            message = await ctx.author.send(out)
            emoji_guard = discord.utils.get(ctx.author.guild.emojis, name='Guardian_icon')
            await message.add_reaction(emoji_guard)
            emoji_thief = discord.utils.get(ctx.author.guild.emojis, name='Thief_icon')
            await message.add_reaction(emoji_thief)
            await message.add_reaction('\U0001F525')
            await message.add_reaction('\U0001F4A7')

            correct_answer_order=['\U0001F525',emoji_guard.name,emoji_thief.name,'\U0001F4A7']
            tumbler_count = 0
            current_correct_answer = correct_answer_order[0]
            time_until_message_disappears = 300

        except discord.Forbidden:
            return await ctx.send('I do not have permission to DM you. Please enable this in the future.')

        def r_check(r, user):
            return user == ctx.author and r.count > 1

        while tumbler_count < len(correct_answer_order):
            try:
                ans, user = await self.bot.wait_for('reaction_add', check=r_check, timeout=time_until_message_disappears)
            except asyncio.TimeoutError:
                await ctx.author.send('Sorry. You took too long to select your choice. If you would like to retry, re-enter the command in a text channel and the bot will re-message you.')
                break
            else:
                time_until_message_disappears = 20
                try:
                    answer = str(ans.emoji.name)
                except:
                    answer = str(ans.emoji)

                if answer == current_correct_answer:
                    tumbler_count = tumbler_count + 1

                    if tumbler_count == len(correct_answer_order):
                        await ctx.author.send('You got the combination correct!')
                        break
                    else:
                        current_correct_answer = correct_answer_order[tumbler_count]
                else:
                    tumbler_count = tumbler_count + 1

                    if tumbler_count == len(correct_answer_order):
                        await ctx.author.send('The entered combination was not correct. To try again, re-run the command from any guild text channel.')
                        break
                    else:
                        current_correct_answer = 'This_is_an_unmatchable_string'

        await message.delete()

    @commands.command(hidden=True,brief='Dhuum monologue distilled to text. For mere mortals.')
    @commands.check(turtlecheck.if_seaguard)
    async def leaderboardmockup(self, ctx):

        embed = discord.Embed(title='__**The Leaderboard  |  Grand Siege Turtle Games: Season 1**__', colour=0x76AFA5, url='https://www.youtube.com/watch?v=9jK-NcRmVcw&mute=1')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.set_footer(text='Time at last successful turtle progression: Sunday 10th, 12:01AM', icon_url='https://cdn.discordapp.com/attachments/471547983859679232/478072773659328524/108145_time_512x512.png')
        embed.add_field(name='1) **Renay** __**[Finished!]**__', value='~~__**|#1|#2|#3|#4|#5|#6|#7|#8|#9|#10|#11|#12|#13|#14|#15|**__~~', inline=False)
        embed.add_field(name='2) **Rev** *(@ 11:59PM)*  ', value='__**|#1|#2|#3|#4|#5|#6|#7|#8|#9|**__', inline=False)
        embed.add_field(name='3) **Kusi** *(@ 12:01AM)*   ', value='__**|#1|#2|#3|#4|#5|#6|#7|#8|#9|**__', inline=False)
        embed.add_field(name='4) **Lyanna**', value='__**|#1|#2|#3|#4|#5|#6|#7|**__', inline=False)
        embed.add_field(name='5) **Tyr** *(@ 10:59PM)* ', value='__**|#1|#2|#3|#4|#5|#6|**__', inline=False)
        embed.add_field(name='6) **Turtle** *(@ 11:00PM)* ', value='__**|#1|#2|#3|#4|#5|#6|**__', inline=False)
        embed.add_field(name='7) **Turtle**', value='__**|#1|#2|#3|#4|**__', inline=False)
        embed.add_field(name='8) **Turtle**', value='__**|#1|#2|#3|**__', inline=False)
        embed.add_field(name='9) **Turtle**', value='__**|#1|#2|**__', inline=False)
        await ctx.send(embed=embed)

    @commands.command(hidden=True,brief='Dhuum monologue distilled to text. For mere mortals.')
    @commands.check(turtlecheck.if_seaguard)
    async def game_initialize_leaderboard(self, ctx, name='Grand Siege Turtle Games'):
        #Make sure the message gets deleted before someone else can see it (in case the general flag doesn't catch it)
        try:
            await ctx.message.delete()
        except:
            pass

        leaderboard = await self.initialize_leaderboard(ctx, name)

    #This is a version of the command that can be called by other commands as needed if an active leaderboard can't be found
    async def initialize_leaderboard(self, ctx, name='Grand Siege Turtle Games'):

        title_string = '__** Leaderboard  |  ' + name + '**__'

        embed = discord.Embed(title=title_string, colour=0x76AFA5, url='https://www.youtube.com/watch?v=9jK-NcRmVcw&mute=1')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.set_footer(text='No turtles have made it onto the leaderboard. Yet.', icon_url='https://cdn.discordapp.com/attachments/471547983859679232/478072773659328524/108145_time_512x512.png')

        leaderboard = await ctx.send(embed=embed)
        leaderboard_message_id = leaderboard.id
        leaderboard_name = name

        #TODO: Add the leaderboard_message_id and leaderboard_name to a db lookup table
        #
        #
        #
        #

        return(leaderboard)

    async def game_update_leaderboard(self, ctx, turn=0):

        try:
            leaderboard = await ctx.get_message(478679591414792192)
        except:
            #initialize a new leaderboard
            await ctx.send('Could not find a currently running leaderboard. Initialized a new leaderboard here.')
            leaderboard = await self.initialize_leaderboard(ctx)

        ######################################################
        #Replace this section with the actual database lookup
        #Currently the code assumes the following order from the resulting query
        #discord_id name nickname current_farthest_sucessful_step_number flag_if_tie timestamp_most_recent_progress
        the_grand_game = []
        with open("the_grand_game.txt") as textFile:
            for row in textFile:
                the_grand_game.append([str(s) for s in row.split()])
        ########################################################

        place_on_leaderboard = 1
        last_question_number = 15
        max_number_on_leaderboard = 25

        #TODO: Edit this so it looks up the leaderboard name in the lookup table
        embed = discord.Embed(title='__**The Leaderboard  |  Grand Siege Turtle Games: Season 1**__', colour=0x76AFA5, url='https://www.youtube.com/watch?v=9jK-NcRmVcw&mute=1')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.set_footer(text='Time at last successful turtle progression:', icon_url='https://cdn.discordapp.com/attachments/471547983859679232/478072773659328524/108145_time_512x512.png')

        for turtle in range(len(the_grand_game)):
            #As long as the turtle has completed at least the first hint, add them to the leaderboard
            if int(the_grand_game[turtle][3]) >= 1:
                #If there is a nickname for the turtle, use that as turtle_name
                if the_grand_game[turtle][2] != 'x':
                    turtle_name = str(the_grand_game[turtle][2])
                else:
                    turtle_name = str(the_grand_game[turtle][1])

                #If the turtle completed the last question add finished status to string
                if int(the_grand_game[turtle][3]) == last_question_number:
                    finished_status = '__**[Finished!]**__'
                    starting_char = '~~'
                    ending_char = '~~'
                else:
                    finished_status = ''
                    starting_char = ''
                    ending_char = ''

                #If there is a tie add tie breaker time to string
                if the_grand_game[turtle][4] == '1':
                    tiebreak_time = '*(\@' + str(the_grand_game[turtle][5]) + ')*'
                else:
                    tiebreak_time = ''

                field_name_string = str(place_on_leaderboard) + ') **' + turtle_name + '** ' + finished_status + ' ' + tiebreak_time

                field_value_string = starting_char+'__**'

                #Add progress bar for each completed step up until the last completed step
                for i in range(1,int(the_grand_game[turtle][3])+1):
                    field_value_string=field_value_string+'|#'+str(i)
                field_value_string= field_value_string+"|**__"+ending_char

                #Only add as many to the leaderboard as we choose:
                if place_on_leaderboard <= max_number_on_leaderboard:
                    embed.add_field(name=field_name_string, value=field_value_string, inline=False)
                else:
                    break

                place_on_leaderboard = place_on_leaderboard + 1

        try:
            await leaderboard.edit(embed=embed)
        except:
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GrandTurtleGameControls(bot))
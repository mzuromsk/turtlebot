import discord
import asyncio
import turtlecheck
import datetime
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
    async def game_send_test_card(self, ctx):
        start_card = await self.create_start_card(ctx)

    async def create_start_card(self, ctx, gamename='', keyname='Hidden Key', steps=1, cooldown=0, timer=5):
        #Format all the strings
        description_string = "```$" + keyname + "```" + "\n**Congratulations!** You have `found` the hidden key `$" + keyname + "`, but now you have to prove your worth to earn it. This key involves:\n\n \n"
        gamename_string = "Grand Game: " + gamename
        if steps==1:
            steps_string = ':footprints: | ' + str(steps) + ' step'
            steps_description_string = 'To earn this hidden key, you will have to correctly answer ' + str(steps) + ' question.\nIf you give an incorrect answer, you may be asked to restart by retyping the hidden key ' + '`$' +keyname+ '` in any ST text channel.'
            stopwatch_description_string = 'The questions in this series have a default time limit of ' + str(timer) + ' minutes.\n[Unless otherwise indicated]\n\n'
        else:
            steps_string = ':footprints: | ' + str(steps) + ' steps'
            steps_description_string = 'To earn this hidden key, you will have to correctly answer ' + str(steps) + ' seperate questions in a row.\n\nIf you give an incorrect answer at any step, you may be asked to restart the entire series of questions by retyping the hidden key ' + '`$' +keyname+ '` in any ST text channel.\n'
            stopwatch_description_string = 'The questions in this series have a default time limit of ' + str(timer) + ' minutes.\n[Unless otherwise indicated]\n\n'

        if cooldown==0:
            cooldown_string = ':repeat: | No cooldown'
            cooldown_description_string = 'This hidden key has no cooldown. If you answer any step incorrectly, you can `immediately` reattempt the key by retyping the hidden key in any ST text channel.'
        else:
            cooldown_string = ':repeat: | ' + str(cooldown) + ' minute cooldown'
            cooldown_description_string = 'This hidden key has a ' + str(cooldown) + ' minute cooldown (measured from when you entered the hidden key). If you answer any step incorrectly, you will have to wait the required cooldown period. After the cooldown, you may try again by retyping the hidden key in any ST text channel.\n'

        stopwatch_string = ':stopwatch: | ' + str(timer) + ' minutes'

        ready_string = 'Ready to get started, {0}?\n'.format(ctx.author.name)
        ready_description_string = 'When you are ready to begin, click ✅. You have ' + str(timer) + ' minutes before this attempt will time out and you must re-enter the key.'

        time = datetime.datetime.utcnow()

        #Create the start card embed message
        embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/192385258736451585/479126995599491078/key.png')
        embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.add_field(name=steps_string, value=steps_description_string, inline=False)
        embed.add_field(name=cooldown_string, value=cooldown_description_string, inline=False)
        embed.add_field(name=stopwatch_string, value=stopwatch_description_string, inline=False)
        embed.add_field(name=ready_string, value=ready_description_string)

        #Send it to the user
        start_card = await ctx.author.send(embed=embed)
        await start_card.add_reaction('✅')
        await start_card.add_reaction('❌')
        return(start_card)

    async def create_choose_one_card(self, ctx, choose_one_card):
        #TODO: Edit so that it just accepts a choose_one_card class instance

        description_string = "`$" + choose_one_card.keyname + "`" + " | Step " + str(choose_one_card.step_number) + " of " + str(choose_one_card.steps) + " | :stopwatch: " + str(choose_one_card.timer) + ' minutes\n' + "\n```Select your answer from the choices below. You make a selection by clicking the associated reaction.```"
        gamename_string = "Grand Game: " + choose_one_card.gamename

        time = datetime.datetime.utcnow()

        with ctx.author.dm_channel.typing():
            #Create the start card embed message
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/189526271288410112/479417475025469483/SelectOne.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name='The Clue', value=choose_one_card.clue_text, inline=False)

            count = 0
            key_text = ''

            for item in range(len(choose_one_card.emoji_key)):
                key_text = key_text + choose_one_card.emoji[item] + ' ' + choose_one_card.emoji_key[item] + '  |  '
                count += 1
                if count > 2:
                    count = 0
                    key_text += '\n\n'

            embed.add_field(name='Icon Key', value=key_text, inline=False)

            #Send it to the user
            card = await ctx.author.send(embed=embed)

            #Add all the reactions
            for item in range(len(choose_one_card.emoji)):
                await card.add_reaction(choose_one_card.emoji_code[item])
            return(card)

    async def create_earned_key_card(self, ctx, earned_key_card):
        #Format all the strings
        description_string = "```$" + earned_key_card.keyname + "```" + "\n**Congratulations!** You have now fully `earned` the hidden key `$" + earned_key_card.keyname + "`!\n\n \n"
        gamename_string = "Grand Game: " + earned_key_card.gamename

        #TODO: Query the db for leaderboard position
        leaderboard_description_string = 'Your leaderboard progres now reflects that you have earned this key. You are currently in `1st` place!'

        unlocked_next_clue_description_string = 'The clue will appear below. If you take a break and forget where you left off, you can always type: $game_my_last_clue into any ST text channel to have the clue for the next `hidden key` resent to you.'

        time = datetime.datetime.utcnow()

        #Create the earned key card embed message
        embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/192385258736451585/479478074702954496/crossedkeys.png')
        embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.add_field(name=':sparkles: | Your position on the leaderboard has been updated!', value=leaderboard_description_string, inline=False)
        embed.add_field(name=':unlock: | You have unlocked a clue for the next hidden key!', value=unlocked_next_clue_description_string, inline=False)
        embed.add_field(name='```The Clue for your next $hiddenkey```', value=earned_key_card.clue_text, inline=False)

        #Send it to the user
        earned_key_card = await ctx.author.send(embed=embed)

        return(earned_key_card)


    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def game_test_update_gameturn(self, ctx, turn=0):
        #Make sure the message gets deleted before someone else can see it (in case the general flag doesn't catch it)
        try:
            await ctx.message.delete()
        except:
            pass

        start_time = datetime.datetime.utcnow()

        #Set overall hidden key paramaters
        gamename ='Divinity\'s Reach Pre-Season'
        keyname='Uzolan'
        steps=1
        cooldown=5
        timer=5

        #Send the start card for this hidden key
        try:
            message = await self.create_start_card(ctx, gamename, keyname, steps, cooldown, timer)
        except discord.Forbidden:
            return await ctx.send('I do not have permission to DM you. Please enable this in the future.')

        #If the user is ready, ask the first question
        def r_check(r, user):
            return user == ctx.author and r.count > 1
        try:
            ans, user = await self.bot.wait_for('reaction_add', check=r_check, timeout=300.0)
        except asyncio.TimeoutError:
            timeout_message = '```You did not answer within the time limit.```' + self.format_retry_message(start_time, keyname, cooldown)
            await ctx.author.send(timeout_message)
            return
        else:
            if str(ans.emoji) == '✅':
                step_1_settings = Choose_One_Card_Settings(gamename, keyname, steps, cooldown, timer)
                step_1_settings.step_number=1
                step_1_settings.clue_text='Take a load off and wander through the gardens of the Central Plaza. Some might say the Gods themselves tend to the garden, but which of the gods “fought the hardest and rightfully earned their spot among the six” (More of a Joke about GW: Nightfall)'
                step_1_settings.emoji = [':regional_indicator_d:',':regional_indicator_m:',':regional_indicator_k:',':regional_indicator_l:',':regional_indicator_g:',':regional_indicator_b:']
                step_1_settings.emoji_key = ['Dwayna','Melandru','Kormir','Lyssa','Grenth','Balthazar']
                step_1_settings.emoji_code = ['\U0001F1E9','\U0001F1F2','\U0001F1F0','\U0001F1F1','\U0001F1EC','\U0001F1E7']
                step_1_settings.emoji_correct_index = 2
                step_1_settings.timer=5

                question_card = await  self.create_choose_one_card(ctx, step_1_settings)
            if str(ans.emoji) == '❌':
                comeback_message = 'Okay, come back when you are ready.' + self.format_retry_message(start_time, keyname, cooldown)
                await ctx.author.send(comeback_message)
                return

        try:
            pick_one_answer, user = await self.bot.wait_for('reaction_add', check=r_check, timeout=300.0)
        except asyncio.TimeoutError:
            timeout_message = '```You did not answer within the time limit.```' + self.format_retry_message(start_time, keyname, cooldown)
            await ctx.author.send(timeout_message)
            return
        else:
            if str(pick_one_answer.emoji) == step_1_settings.emoji_code[step_1_settings.emoji_correct_index]:
                earned_key_settings = Earned_Key_Card_Settings(gamename, keyname, steps, cooldown, timer)
                earned_key_settings.clue_text = "The next hint for a question would go here."

                earned_key_message = await self.create_earned_key_card(ctx, earned_key_settings)

                #Update the database and leaderboard
                #TODO: ADD FUNCTION TO UPDATE DATABASE
                await self.update_leaderboard(ctx)

            else:
                incorrect_message = '```I\'m sorry, you are not correct.```' + self.format_retry_message(start_time, keyname, cooldown)
                await ctx.author.send(incorrect_message)
                return

    def format_retry_message(self, start_time, keyname='hidden key', cooldown=0):
        retry_message_immediately = '```To retry, re-enter the hidden key `$' + str(keyname) + '` in any text channel and the bot will re-message you. You can retry immediately.```'
        retry_message_time_remaining = '```To retry, re-enter the hidden key `$' + str(keyname) + '` in any text channel and the bot will re-message you. You can retry in {0} minutes and {1} seconds.```'

        current_time = datetime.datetime.utcnow()
        cooldown_finished_time = start_time + datetime.timedelta(minutes=cooldown)
        if current_time > cooldown_finished_time:
            time_in_seconds_remaining_on_cooldown = datetime.datetime.utcnow()
            retry_message = retry_message_immediately
        else:
            time_remaining = cooldown_finished_time - current_time
            minutes, seconds = divmod(time_remaining.total_seconds(),60)
            retry_message = retry_message_time_remaining.format(int(minutes), int(seconds))

        return(retry_message)


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

        #First send the question type embed-card


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

    @commands.command(hidden=True,brief='Updates the game leaderboard.')
    @commands.check(turtlecheck.if_seaguard)
    async def game_update_leaderboard(self, ctx, name='Grand Siege Turtle Games'):
        #Make sure the message gets deleted before someone else can see it (in case the general flag doesn't catch it)
        await self.update_leaderboard(ctx, turn=0)

    async def update_leaderboard(self, ctx, turn=0):

        #First try and see if we can find the current leaderboard
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

        #Leaderboard display options for fancy version
        last_question_number = 15
        max_number_full_display = 5
        max_number_on_leaderboard = 25
        number_icons_per_line =15

        with leaderboard.channel.typing():

            complete_emoji = discord.utils.get(ctx.author.guild.emojis, name='hpf')
            incomplete_emoji = discord.utils.get(ctx.author.guild.emojis, name='hpe')

            if incomplete_emoji is not None and complete_emoji is not None:
                leaderboard_description_string = description='**Icon Key**   '+ str(complete_emoji) + ': Step Completed   **||**   '+ str(incomplete_emoji) + ': Step Unfinished \n '
                leaderboard_icons_succesfully_loaded = True
            else:
                leaderboard_description_string = description='Each number indicates a completed step in the game.'
                leaderboard_icons_succesfully_loaded = False

            time = datetime.datetime.utcnow()
            #TODO: Edit this so it looks up the leaderboard name in the lookup table
            leaderboard_title_string = '__**The Leaderboard  |  Grand Siege Turtle Games: Season 1**__'

            #Create Embed
            embed = discord.Embed(title=leaderboard_title_string, colour=0x76AFA5, url='https://www.youtube.com/watch?v=9jK-NcRmVcw&mute=1', description = leaderboard_description_string, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')

            #Initialize strings and counters that we need in the leaderboard generation loop

            field_value_string = ''
            chunk_name_string = ''
            place_on_leaderboard = 1

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
                        finished_status = '__**[Done!]**__'
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

                    #If we were able to load the icons we need, do a fancier table
                    if leaderboard_icons_succesfully_loaded:
                        #Only full diplay as many to the leaderboard as we choose:
                        if place_on_leaderboard <= max_number_full_display:
                            countperline = 1
                            for i in range(1,int(the_grand_game[turtle][3])+1):
                                field_value_string=field_value_string+str(complete_emoji)
                                countperline +=1
                                if countperline>number_icons_per_line:
                                    field_value_string+='\n'
                                    countperline =1
                            for i in range(1,last_question_number-int(the_grand_game[turtle][3])+1):
                                field_value_string=field_value_string+str(incomplete_emoji)
                                countperline +=1
                                if countperline>number_icons_per_line:
                                    field_value_string+='\n'
                                    countperline =1
                            embed.add_field(name=field_name_string, value=field_value_string, inline=False)
                            field_value_string = ''

                        #Then group the rest of leaderboard entries into sets of the same size to display
                        elif place_on_leaderboard <= max_number_on_leaderboard:
                            if place_on_leaderboard%max_number_full_display == 1:
                                chunk_name_string = ':turtle:  __**' + str(place_on_leaderboard)

                            field_value_string = field_value_string + str(place_on_leaderboard) + ')  **|**  ' + str(the_grand_game[turtle][3]) + '/' + str(last_question_number) + ' ' + str(complete_emoji) + '  **|  ' + turtle_name + '** ' + finished_status + ' ' + tiebreak_time + '\n'

                            if place_on_leaderboard%max_number_full_display == 0:
                                chunk_name_string += ' - ' + str(place_on_leaderboard)+'**__'
                                embed.add_field(name=chunk_name_string, value=field_value_string, inline=True)
                                chunk_name_string = ''
                                field_value_string = ''

                        #Stop when we are over the max number to be allowed on leaderboard
                        else:
                            break

                        place_on_leaderboard = place_on_leaderboard + 1

                    #If we weren't able to load the icons, make do with a simple table
                    else:
                        field_value_string = starting_char+'__**'
                        #Add progress bar for each completed step up until the last completed step
                        for i in range(1,int(the_grand_game[turtle][3])+1):
                            field_value_string=field_value_string+'|#'+str(i)
                        field_value_string= field_value_string+"|**__"+ending_char
                        embed.add_field(name=field_name_string, value=field_value_string, inline=True)

            #Fancy table cleanup
            if leaderboard_icons_succesfully_loaded:
                if field_value_string != '':
                    chunk_name_string += ' - ' + str(place_on_leaderboard-1)+'**__'
                    embed.add_field(name=chunk_name_string, value=field_value_string, inline=True)

            try:
                await leaderboard.edit(embed=embed)
            except:
                await ctx.send(embed=embed)

class Choose_One_Card_Settings:
    def __init__(self, gamename='Current Game Name', keyname='Current Key Name', steps=1, cooldown=5, timer=5):
        self.gamename = gamename
        self.keyname = keyname
        self.steps = steps
        self.cooldown = cooldown
        self.timer = timer
        self.step_number = 1
        self.clue_text = ''
        self.emoji = []
        self.emoji_key = []
        self.emoji_correct_index = 0
        self.timer = 5
        self.img = ''
        self.url = ''

class Earned_Key_Card_Settings:
    def __init__(self, gamename='Current Game Name', keyname='Current Key Name', steps=1, cooldown=5, timer=5):
        self.gamename = gamename
        self.keyname = keyname
        self.steps = steps
        self.cooldown = cooldown
        self.timer = timer
        self.step_number = 1
        self.clue_text = ''
        self.img = ''
        self.url = ''

def setup(bot):
    bot.add_cog(GrandTurtleGameControls(bot))
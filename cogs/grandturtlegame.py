import discord
import asyncio
import datetime
import turtlecheck
import cogs.api as api
import grandturtlegame_question_classes as game_q_type
from discord.ext import commands
import psycopg2
import turtle_credentials as tc
from discord import NotFound
import regex

class GrandTurtleGameControls:
    def __init__(self, bot):
        self.bot = bot
        self.api = api.ApiControls(self.bot)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def pingturtlegamecontrols(self, ctx):
        await ctx.send('Pong!')

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_admin)
    async def game_turn_bot_status_on(self, ctx):
        await self.bot.change_presence(activity=discord.Game(name="Grand \U0001F422 Game"))

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_admin)
    async def game_turn_bot_status_off(self, ctx):
        await self.bot.change_presence(activity=None)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    async def game_test_hiddenkey(self, ctx, description=True):

        #Set overall hidden key paramaters
        gamename ='Divinity\'s Reach Pre-Season'
        keyname='game_test_hiddenkey'
        step_number = 1
        steps=4
        cooldown=5
        timer=5

        start_card_settings = game_q_type.Start_Card_Settings(ctx, gamename, keyname, step_number, steps, cooldown, timer)

        step_1_settings = game_q_type.Choose_One_Card_Settings(ctx, gamename, keyname, step_number, steps, cooldown, timer, description)
        step_1_settings.substep_number=1
        step_1_settings.clue_text='Take a load off and wander through the gardens of the Central Plaza. Some might say the Gods themselves tend to the garden, but which of the gods “fought the hardest and rightfully earned their spot among the six” (More of a Joke about GW: Nightfall)'
        step_1_settings.emoji_answer_key_text = ['Dwayna','Melandru','Kormir','Lyssa','Grenth','Balthazar']
        step_1_settings.emoji = ['\U0001F1E9','\U0001F1F2','\U0001F1F0','\U0001F1F1','\U0001F1EC','\U0001F1E7']
        step_1_settings.correct_item_in_list = 3
        step_1_settings.timer=5

        step_2_settings = game_q_type.Combination_Card_Settings(ctx, gamename, keyname, step_number, steps, cooldown, timer, description)
        step_2_settings.substep_number=2
        step_2_settings.clue_text='In order of descending cleave.'
        step_2_settings.icon_key_per_line = 2

        emoji_guard = discord.utils.get(ctx.author.guild.emojis, name='Guardian_icon')
        emoji_thief = discord.utils.get(ctx.author.guild.emojis, name='Thief_icon')

        step_2_settings.emoji_answer_key_text = ['Guardian','Thief','Fire Elementalist','Water Elementalist']
        step_2_settings.emoji = [emoji_guard,emoji_thief,'\U0001F525','\U0001F4A7']
        step_2_settings.correct_combination= [3,1,2,4]
        step_2_settings.timer=1

        step_3_settings = game_q_type.Text_Card_Settings(ctx, gamename, keyname, step_number, steps, cooldown, timer, description)
        step_3_settings.substep_number=3
        step_3_settings.clue_text='Exploring near Uzolan’s Mechanical Orchestra you\'ll find yourself wondering \"how do you walk on these stones all day long?\"'
        step_3_settings.correct_answer_text='You get used to it.'

        step_4_settings = game_q_type.Get_In_Game_Card_Settings(ctx, gamename, keyname, step_number, steps, cooldown, timer, description)
        step_4_settings.substep_number=4
        step_4_settings.clue_text='You were gonna try for the jailbreak, but the key you found is complete garbage.'
        #step_4_settings.item_id=23794
        step_4_settings.item_id=46733
        step_4_settings.required_amount=5000

        earned_key_card_settings = game_q_type.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, steps, cooldown, timer)
        earned_key_card_settings.clue_text = 'Not feeling very creative. Go find the next hidden key.'

        question_cards_settings = [step_1_settings, step_2_settings,step_3_settings, step_4_settings]

        await self.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)


    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def print_active_leaderboard_message_id(self, ctx):
        #await ctx.author.send("active leaderboard id message id:")
        await ctx.author.send(get_active_leaderboard_message_id())


    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def game_delete_active_leaderboard_from_database(self, ctx):
        await delete_active_leaderboard_from_database(ctx)


    async def create_start_card(self, card_settings):
        #Format all the strings
        description_string = "```$" + card_settings.keyname + "```" + "\n**Congratulations!** You have `found` the hidden key `$" + card_settings.keyname + "`, but now you have to prove your worth to earn it. This key involves:\n\n \n"
        gamename_string = "Grand Game: " + card_settings.gamename
        if card_settings.steps==1:
            steps_string = ':footprints: | ' + str(card_settings.steps) + ' step'
            steps_description_string = 'To earn this hidden key, you will have to correctly answer ' + str(card_settings.steps) + ' question. If you give an incorrect answer at any step, you may be asked to restart the key.'
            stopwatch_description_string = 'The questions in this series have a default time limit of ' + str(card_settings.timer) + ' minutes.\n[Unless otherwise indicated]\n\n'
        else:
            steps_string = ':footprints: | ' + str(card_settings.steps) + ' steps'
            steps_description_string = 'To earn this hidden key, you will have to correctly answer ' + str(card_settings.steps) + ' seperate questions in a row. If you give an incorrect answer at any step, you may be asked to restart the key.\n'
            stopwatch_description_string = 'The questions in this series have a default time limit of ' + str(card_settings.timer) + ' minutes.\n[Unless otherwise indicated]\n\n'

        if card_settings.cooldown==0:
            cooldown_string = ':repeat: | No cooldown'
            cooldown_description_string = 'This hidden key has no cooldown. If you answer any step incorrectly, you can `immediately` reattempt the key by retyping the hidden key ' + '`$' +card_settings.keyname+ '` in any ST text channel'
        else:
            cooldown_string = ':repeat: | ' + str(card_settings.cooldown) + ' minute cooldown'
            cooldown_description_string = 'This hidden key has a ' + str(card_settings.cooldown) + ' minute cooldown (measured from when you entered the hidden key). If you fail, you will have to wait the required cooldown period before retyping the hidden key ' + '`$' +card_settings.keyname+ '` in any ST text channel.\n'

        stopwatch_string = ':stopwatch: | ' + str(card_settings.timer) + ' minutes'

        ready_string = 'Ready to get started, {0}?\n'.format(card_settings.ctx.author.name)
        ready_description_string = 'When you are ready to begin, click ✅. You have ' + str(card_settings.timer) + ' minutes before this attempt will time out and you must re-enter the key.'

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
        start_card = await card_settings.ctx.author.send(embed=embed)
        await start_card.add_reaction('✅')
        await start_card.add_reaction('❌')
        return(start_card)


    async def create_question_card(self, card_settings):
        if card_settings.card_type=='choose_one':
            question_card = await self.create_choose_one_card(card_settings)
        elif card_settings.card_type=='combination':
            question_card = await self.create_combination_card(card_settings)
        elif card_settings.card_type=='text':
            question_card = await self.create_text_card(card_settings)
        elif card_settings.card_type=='get_in_game':
            question_card = await self.create_get_in_game_card(card_settings)
        return(question_card)


    async def create_choose_one_card(self, card_settings):
        #TODO: Edit so that it just accepts a choose_one_card class instance

        description_string = "`$" + card_settings.keyname + "`" + " | Step " + str(card_settings.substep_number) + " of " + str(card_settings.steps) + " | :stopwatch: " + str(card_settings.timer) + ' minutes\n'
        if card_settings.question_description:
            description_string+="```Select your answer from the choices below. You make a selection by clicking the associated reaction.```"
        gamename_string = "Grand Game: " + card_settings.gamename

        time = datetime.datetime.utcnow()

        with card_settings.ctx.author.dm_channel.typing():
            #Create the start card embed message
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/189526271288410112/479417475025469483/SelectOne.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name='The Clue', value=card_settings.clue_text, inline=False)

            count = 0
            key_text = ''

            for item in range(len(card_settings.emoji)):
                key_text = key_text + str(card_settings.emoji[item]) + ' ' + card_settings.emoji_answer_key_text[item] + '  **|**  '
                count += 1
                if count >= card_settings.icon_key_per_line:
                    count = 0
                    key_text += '\n\n'

            embed.add_field(name='Icon Key', value=key_text, inline=False)


            #Send it to the user
            card = await card_settings.ctx.author.send(embed=embed)

            #Add all the reactions
            for item in range(len(card_settings.emoji)):
                await card.add_reaction(card_settings.emoji[item])
            return(card)


    async def create_text_card(self, card_settings):
        #TODO: Edit so that it just accepts a choose_one_card class instance

        description_string = "`$" + card_settings.keyname + "`" + " | Step " + str(card_settings.substep_number) + " of " + str(card_settings.steps) + " | :stopwatch: " + str(card_settings.timer) + ' minutes\n'
        if card_settings.question_description:
            description_string+="```Type in your answer: it may be a single word or a longer phrase.\n\nNote: Spelling counts, but not punctuation.```"

        gamename_string = "Grand Game: " + card_settings.gamename

        time = datetime.datetime.utcnow()

        with card_settings.ctx.author.dm_channel.typing():
            #Create the start card embed message
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/189526271288410112/479417402107363328/textinput.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name='The Clue', value=card_settings.clue_text, inline=False)

            #Send it to the user
            card = await card_settings.ctx.author.send(embed=embed)
        return(card)


    async def create_get_in_game_card(self, card_settings):
        #TODO: Add API key lookup
        description_string = "`$" + card_settings.keyname + "`" + " | Step " + str(card_settings.substep_number) + " of " + str(card_settings.steps) + " | :stopwatch: " + str(card_settings.timer) + ' minutes\n'
        if card_settings.question_description:
            description_string+="```Figure out the clue and find the corresponding item in game. When you have the item in your inventory, click the checkmark to begin the scan. \n\nNote: Requires a full API key. Scan completes in 5 minutes.```"

        gamename_string = "Grand Game: " + card_settings.gamename

        time = datetime.datetime.utcnow()

        with card_settings.ctx.author.dm_channel.typing():
            #Create the start card embed message
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/189526271288410112/479417574619086859/Inventory.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name='The Clue', value=card_settings.clue_text, inline=False)

            ready_string = 'Ready to get started, {0}?\n'.format(card_settings.ctx.author.name)
            ready_description_string = 'When you have the mystery item in your inventory, click ✅.'

            #Send it to the user
            card = await card_settings.ctx.author.send(embed=embed)

            #Add all the reactions
            await card.add_reaction('✅')
            await card.add_reaction('❌')
            return(card)


    async def create_combination_card(self, card_settings):
        description_string = "`$" + card_settings.keyname + "`" + " | Step " + str(card_settings.substep_number) + " of " + str(card_settings.steps) + " | :stopwatch: " + str(card_settings.timer) + ' minutes\n'
        if card_settings.question_description:
            description_string+="\n```Solve this combination lock by selecting the reactions below in the correct order. To select a reaction, click it so that it increments from 1 to 2. \nNote: you can not reset a mistake - you must retry the hidden key.```"

        gamename_string = "Grand Game: " + card_settings.gamename

        time = datetime.datetime.utcnow()

        with card_settings.ctx.author.dm_channel.typing():
            #Create the start card embed message
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/189526271288410112/479417522861637643/combinationlock.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name='The Clue', value=card_settings.clue_text, inline=False)

            count = 0
            key_text = ''

            for item in range(len(card_settings.emoji)):
                key_text = key_text + str(card_settings.emoji[item]) + ' ' + card_settings.emoji_answer_key_text[item] + '  |  '
                count += 1
                if count >= 2:
                    count = 0
                    key_text += '\n\n'

            embed.add_field(name='Icon Key', value=key_text, inline=False)

            #Send it to the user
            card = await card_settings.ctx.author.send(embed=embed)

            #Add all the reactions
            for item in range(len(card_settings.emoji)):
                await card.add_reaction(card_settings.emoji[item])
            return(card)


    async def create_earned_key_card(self, card_settings):
        #Format all the strings
        description_string = "```$" + card_settings.keyname + "```" + "\n**Congratulations!** You have now fully `earned` the hidden key `$" + card_settings.keyname + "`!\n\n \n"
        gamename_string = "Grand Game: " + card_settings.gamename

        #TODO: Query the db for leaderboard position
        leaderboard_description_string = 'Your leaderboard progress now reflects that you have earned this key. You are currently in `1st` place!'

        unlocked_next_clue_description_string = 'The clue will appear below. If you take a break and forget where you left off, you can always type: $game_my_last_clue into any ST text channel to have the clue for the next `hidden key` resent to you.'

        time = datetime.datetime.utcnow()

        #Create the earned key card embed message
        embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/192385258736451585/479478074702954496/crossedkeys.png')
        embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.add_field(name=':sparkles: | Your position on the leaderboard has been updated!', value=leaderboard_description_string, inline=False)
        embed.add_field(name=':unlock: | You have unlocked the ability to use the next hidden key!', value=unlocked_next_clue_description_string, inline=False)
        embed.add_field(name=':mag_right: | Clue for your next `$hiddenkey`', value=card_settings.clue_text, inline=False)

        #Send it to the user
        card = await card_settings.ctx.author.send(embed=embed)
        return(card)


    async def run_hidden_key(self, ctx, earned_key_card_settings, start_card_settings=None, question_cards_settings=None):
        #Get the starting time
        start_time = datetime.datetime.utcnow()

        #If there are no additional substeps, just send the earned_card
        if question_cards_settings is None:
            #Send the earned card for this hidden key
                try:
                    earned_key_card = await self.create_earned_key_card(earned_key_card_settings)
                    complete_substep(ctx.author.id, earned_key_card_settings.step_number, 1)
                except discord.Forbidden:
                    return await ctx.send('I do not have permission to DM you. Please enable this in the future.')
        else:
            #Send the start card for this hidden key

            #Get current step
            active_step = get_active_step(ctx.author.id)
            if earned_key_card_settings.step_number == active_step:
                active_substep = get_active_substep(ctx.author.id)
            else:
                active_substep=1

            current_substep_index = active_substep-1

            try:
                start_card = await self.create_start_card(start_card_settings)
            except discord.Forbidden:
                return await ctx.send('I do not have permission to DM you. Please enable this in the future.')

            #The condition check for processing the card answer
            def r_check(r, user):
                return user == ctx.author and r.count > 1

            #Wait on the user to start, then process input
            try:
                ans, user = await self.bot.wait_for('reaction_add', check=r_check, timeout=start_card_settings.timer*60)
            except asyncio.TimeoutError:
                timeout_message = '```You did not answer within the time limit.```' + self.format_retry_message(start_time, start_card_settings.keyname, start_card_settings.cooldown)
                await ctx.author.send(timeout_message)
                return
            else:
                if str(ans) == '✅':
                    question_card = await self.create_question_card(question_cards_settings[current_substep_index])

                if str(ans) == '❌':
                    comeback_message = '```Okay, come back when you are ready.```' + self.format_retry_message(start_time, start_card_settings.keyname, start_card_settings.cooldown)
                    await ctx.author.send(comeback_message)
                    return

            key_is_at_end_state = False

            while not key_is_at_end_state:
                print("{0} is on game step {1} substep {2}".format(ctx.author.name,question_cards_settings[current_substep_index].step_number, question_cards_settings[current_substep_index].substep_number))
                response = await self.check_if_question_answer_is_correct(question_cards_settings[current_substep_index], start_time)
                if response['bot_response_message'] != '':
                    await ctx.author.send(response['bot_response_message'])

                if response['answer_status'] == 'TimeoutError' or response['answer_status'] == 'Incorrect':
                    key_is_at_end_state=True
                    return
                elif response['answer_status'] == 'Correct':
                    #If we are on the last question:
                    if current_substep_index + 1 == len(question_cards_settings):
                        earned_key_card = await self.create_earned_key_card(earned_key_card_settings)

                        complete_substep(ctx.author.id, question_cards_settings[current_substep_index].step_number, question_cards_settings[current_substep_index].substep_number)
                        #TODO: ADD FUNCTION TO UPDATE DATABASE STEP

                        await self.update_leaderboard(ctx)
                        key_is_at_end_state = True
                    else:
                        complete_substep(ctx.author.id, question_cards_settings[current_substep_index].step_number, question_cards_settings[current_substep_index].substep_number)

                        key_is_at_end_state = False

                        current_substep_index +=1
                        question_card = await self.create_question_card(question_cards_settings[current_substep_index])
                elif response['answer_status'] == 'Quit':
                    key_is_at_end_state=True
                    return

    async def check_if_question_answer_is_correct(self, question_card_settings, start_time):
        if question_card_settings.card_type=='choose_one':
            response = await self.check_if_choose_one_answer_is_correct(question_card_settings, start_time)
        elif question_card_settings.card_type=='combination':
            response = await self.check_if_combination_answer_is_correct(question_card_settings, start_time)
        elif question_card_settings.card_type=='text':
            response = await self.check_if_text_answer_is_correct(question_card_settings, start_time)
        elif question_card_settings.card_type=='get_in_game':
            response = await self.check_if_get_in_game_answer_is_correct(question_card_settings, start_time)
        return(response)


    async def check_if_choose_one_answer_is_correct(self, question_card_settings, start_time):
        #The condition check for processing the card answer
        def r_check(r, user):
            return user == question_card_settings.ctx.author and r.count > 1

        try:
            pick_one_answer, user = await self.bot.wait_for('reaction_add', check=r_check, timeout=300.0)
        except asyncio.TimeoutError:
            bot_response_message = '```You did not answer within the time limit.```' + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
            return{ 'answer_status': 'TimeoutError', 'bot_response_message': bot_response_message}
        else:
            if str(pick_one_answer) == question_card_settings.emoji[question_card_settings.correct_item_in_list-1]:
                bot_response_message = '```You were correct!```'
                return{ 'answer_status': 'Correct', 'bot_response_message': bot_response_message}
            else:
                bot_response_message = '```I\'m sorry, you are not correct.```' + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
                return{ 'answer_status': 'Incorrect', 'bot_response_message': bot_response_message}


    async def check_if_combination_answer_is_correct(self, question_card_settings, start_time):

        #Correct combination returns the combination starting from 1, so adjust to get the right index
        tumbler_count = 0
        current_correct_answer = question_card_settings.emoji[question_card_settings.correct_combination[tumbler_count]-1]

        time_until_message_disappears = question_card_settings.timer*60

        #The condition check for processing the card answer
        def r_check(r, user):
            return user == question_card_settings.ctx.author and r.count > 1

        while tumbler_count < len(question_card_settings.correct_combination):
            try:
                answer, user = await self.bot.wait_for('reaction_add', check=r_check, timeout=time_until_message_disappears)
            except asyncio.TimeoutError:
                bot_response_message = '```You did not enter the combination quickly enough. You have {0} minutes to start, but once you start entering the combination, you only have {0} seconds between subsequent tumbler clicks.```'.format(question_card_settings.timer, question_card_settings.timer_between_combo_clicks) + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
                return{ 'answer_status': 'TimeoutError', 'bot_response_message': bot_response_message}
            else:
                time_until_message_disappears = question_card_settings.timer_between_combo_clicks
                print('The clicked answer: {0} The current expected correct answer: {1}'.format(str(answer),str(current_correct_answer)))

                if str(answer) == str(current_correct_answer):
                    tumbler_count = tumbler_count + 1

                    if tumbler_count == len(question_card_settings.correct_combination):
                        bot_response_message = '```You got the combination correct!```'
                        return{ 'answer_status': 'Correct', 'bot_response_message': bot_response_message}
                    else:
                        current_correct_answer = question_card_settings.emoji[question_card_settings.correct_combination[tumbler_count]-1]
                else:
                    tumbler_count = tumbler_count + 1

                    if tumbler_count == len(question_card_settings.correct_combination):
                        bot_response_message = '```The entered combination was not correct.```' + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
                        return{ 'answer_status': 'Incorrect', 'bot_response_message': bot_response_message}
                    else:
                        current_correct_answer = 'This_is_an_unmatchable_string'

    async def check_if_text_answer_is_correct(self, question_card_settings, start_time):

        def m_check(m):
            return m.author == question_card_settings.ctx.author and m.channel == question_card_settings.ctx.author.dm_channel

        try:
            text_answer = await self.bot.wait_for('message', check=m_check, timeout=question_card_settings.timer*60)
        except asyncio.TimeoutError:
            bot_response_message = '```You did not answer within the time limit.```' + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
            return{ 'answer_status': 'TimeoutError', 'bot_response_message': bot_response_message}
        else:
            print('The typed in text answer ({0}) and what the correct answer is ({1})'.format(text_answer.content,question_card_settings.correct_answer_text))
            if self.text_strip_punctuation_and_cleanup(text_answer.content) == self.text_strip_punctuation_and_cleanup(question_card_settings.correct_answer_text):
                bot_response_message = '```You were correct!```'
                return{ 'answer_status': 'Correct', 'bot_response_message': bot_response_message}
            else:
                bot_response_message = '```I\'m sorry, you are not correct.```' + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
                return{ 'answer_status': 'Incorrect', 'bot_response_message': bot_response_message}

    async def check_if_get_in_game_answer_is_correct(self, question_card_settings, start_time):
        #The condition check for processing the card answer
        def r_check(r, user):
            return user == question_card_settings.ctx.author and r.count > 1

        try:
            ans, user = await self.bot.wait_for('reaction_add', check=r_check, timeout=question_card_settings.timer*60)
        except asyncio.TimeoutError:
            bot_response_message = '```You did not answer within the time limit.```' + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
            return{ 'answer_status': 'TimeoutError', 'bot_response_message': bot_response_message}
        else:
            if str(ans) == '✅':
                with question_card_settings.ctx.author.dm_channel.typing():
                    timing_card = await self.create_timing_card(question_card_settings)
                    await asyncio.sleep(60)
                    total, output, item_result = await self.api.simple_search(question_card_settings.ctx, question_card_settings.item_id)
                    await timing_card.delete()
                    if total >= question_card_settings.required_amount:
                        search_result_card = await self.create_search_results_card(question_card_settings, output, item_result)
                        bot_response_message = '```You had the necessary number of the correct item ({0}) on your account. Well done!```'.format(item_result["name"])
                        return{ 'answer_status': 'Correct', 'bot_response_message': bot_response_message}
                    elif total > 0:
                        search_result_card = await self.create_search_results_card(question_card_settings, output, item_result)
                        bot_response_message = "```I\'m sorry, although you did have the correct item ({0}), you did not have the necessary amount.```".format(item_result["name"]) + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
                        return{ 'answer_status': 'Incorrect', 'bot_response_message': bot_response_message}
                    elif total ==0:
                        bot_response_message = "```I\'m sorry, you did not have the correct item.```" + "```We have peered into the mists and did not find the correct item anywhere on your account.```" + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
                        return{ 'answer_status': 'Incorrect', 'bot_response_message': bot_response_message}

            if str(ans) == '❌':
                comeback_message = '```Okay, come back when you are ready.```' + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
                return{ 'answer_status': 'Quit', 'bot_response_message': comeback_message}


    async def create_search_results_card(self, question_card_settings, output, item_result):
        #Format all the strings
        gamename_string = "Grand Game: " + question_card_settings.gamename

        time = datetime.datetime.utcnow()

        #Create the earned key card embed message
        embed = discord.Embed(description="Search results for".format(item_result["name"]) + " " * 120 + u'\u200b', colour=1155738, timestamp=time)
        value = "\n".join(output)
        if len(value) > 1014:
            value = ""
            values = []
            for line in output:
                if len(value) + len(line) > 1013:
                    values.append(value)
                    value = ""
                value += line + "\n"
            if value:
                values.append(value)
            embed.add_field(
                name=item_result["name"],
                value="```ml\n{}```".format(values[0]),
                inline=False)
            for v in values[1:]:
                embed.add_field(
                    name=u'\u200b',  # Zero width space
                    value="```ml\n{}```".format(v),
                    inline=False)
        else:
            embed.add_field(
                name=item_result["name"], value="```ml\n{}\n```".format(value))
        embed.set_footer(text=gamename_string, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=item_result["icon"])

        #Send it to the user
        card = await question_card_settings.ctx.author.send(embed=embed)
        return(card)

    async def create_timing_card(self, card_settings):
        #Format all the strings
        time = datetime.datetime.utcnow()

        description_string = "```An account scan has been successfully queued for {0}.```".format(card_settings.ctx.author.name)
        gamename_string = "Grand Game: " + card_settings.gamename

        #Create the earned key card embed message
        embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/189526271288410112/479417574619086859/Inventory.png')
        embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.add_field(name='Peering into the mists...', value="In order to ensure that the account snapshot seen in the mists is up to date, your results will be delayed by 5 minutes.", inline=False)
        embed.set_image(url='https://cdn.discordapp.com/attachments/480582683852800010/482729023881871371/TurtleTimingShell.gif')
        #Send it to the user
        card = await card_settings.ctx.author.send(embed=embed)
        return(card)

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

    def text_strip_punctuation_and_cleanup(self, string):
        remove = regex.compile(r'[\p{C}|\p{M}|\p{P}|\p{S}|\p{Z}]+', regex.UNICODE)
        cleaned_string = remove.sub(u"", string).strip().lower()
        return cleaned_string

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
        leaderboard_channel_id = leaderboard.channel.id
        leaderboard_name = name
        game_id = get_active_game()

        await save_initialized_leaderboard_to_database(ctx, leaderboard_channel_id, leaderboard_message_id, leaderboard_name)

        return(leaderboard)

    @commands.command(hidden=True,brief='Updates the game leaderboard.')
    @commands.check(turtlecheck.if_seaguard)
    async def game_update_leaderboard(self, ctx, name='Grand Siege Turtle Games'):
        #Make sure the message gets deleted before someone else can see it (in case the general flag doesn't catch it)
        await self.update_leaderboard(ctx, turn=0)

    async def update_leaderboard(self, ctx, turn=0):

        #First try and see if we can find the current leaderboard
        try:
            leaderboard_channel_id = get_active_leaderboard_channel_id()
            leaderboard_message_id = get_active_leaderboard_message_id()
            leaderboard_channel = self.bot.get_channel(leaderboard_channel_id)
            leaderboard = await leaderboard_channel.get_message(leaderboard_message_id)

            updatemessage = await leaderboard_channel.send('We are updating the leaderboard in this channel...')

        except:
            #initialize a new leaderboard
            await ctx.send('Could not find a currently running leaderboard. Initialized a new leaderboard here.')
            print('Leaderboard update failed.')
            return



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
        last_step_number = 15
        max_number_full_display = 5
        max_number_on_leaderboard = 20
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
                    if int(the_grand_game[turtle][3]) == last_step_number:
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
                            for i in range(1,last_step_number-int(the_grand_game[turtle][3])+1):
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

                            field_value_string = field_value_string + str(place_on_leaderboard) + ')  **|  ' + str(the_grand_game[turtle][3]) + '/' + str(last_step_number) + ' ' + str(complete_emoji) + '  |  ' + turtle_name + '** ' + finished_status + ' ' + tiebreak_time + '\n'

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
                await leaderboard.edit(content='Updating leaderboard...', embed=None)
                print('Updating leaderboard...')
                await leaderboard.edit(embed=embed, content=None)
                print('Leaderboard updated.')
            except:
                await ctx.send(embed=embed)
        try:
            await updatemessage.delete()
        except:
            pass

    @commands.command(hidden=True,brief='DEBUG ONLY - MOVES AUTHOR FORWARD ONE SUBSTEP')
    @commands.check(turtlecheck.if_seaguard)
    async def debug_complete_substep(self, ctx):
        player = ctx.author.name
        discord_id = ctx.author.id
        cur_step = get_active_step(discord_id)
        cur_substep = get_active_substep(discord_id)
        await ctx.send(player + " is currently on step " + str(cur_step) + ", substep " + str(cur_substep) + ".  Completing a step now.")

        complete_substep(discord_id, cur_step, cur_substep)

        cur_step = get_active_step(discord_id)
        cur_substep = get_active_substep(discord_id)
        await ctx.send(player + " is currently on step " + str(cur_step) + ", substep " + str(cur_substep) + ".")

def setup(bot):
    bot.add_cog(GrandTurtleGameControls(bot))

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

def get_active_leaderboard_message_id():
    game_id = get_active_game()
    print('The active game_id is {0}'.format(game_id))
    try:
        conn
    except NameError:
        conn = tc.get_conn()
    cur = conn.cursor()
    sqlStr = "SELECT message_id FROM turtle.game_messages WHERE game_id = " + str(game_id) + ";"
    cur.execute(sqlStr)
    result = cur.fetchall()
    try:
        return result[0][0]
    except:
        return -1

def get_active_leaderboard_channel_id():
    game_id = get_active_game()
    try:
        conn
    except NameError:
        conn = tc.get_conn()
    cur = conn.cursor()
    sqlStr = "SELECT channel_id FROM turtle.game_messages WHERE game_id = " + str(game_id) + ";"
    cur.execute(sqlStr)
    result = cur.fetchall()
    try:
        return result[0][0]
    except:
        return -1

async def save_initialized_leaderboard_to_database(ctx, leaderboard_channel_id, leaderboard_message_id, name):
    game_id = get_active_game()
    await delete_active_leaderboard_from_database(ctx)

    try:
        conn
    except NameError:
        conn = tc.get_conn()
    cur = conn.cursor()
    sqlStr = "INSERT INTO turtle.game_messages (game_id, channel_id, message_id, message_name) VALUES (" + str(game_id) + ", " + str(leaderboard_channel_id) + ", "+ str(leaderboard_message_id) + ", '" + name + "');"
    print(sqlStr)
    cur.execute(sqlStr)
    conn.commit()

async def delete_active_leaderboard_from_database(ctx):
    game_id = get_active_game()
    try:
        conn
    except NameError:
        conn = tc.get_conn()
    cur = conn.cursor()
    sqlStr = "DELETE FROM turtle.game_messages WHERE game_id = " + str(game_id) + ";"
    print(sqlStr)
    cur.execute(sqlStr)
    conn.commit()

def complete_substep(discord_id, step_id, substep_id):
    game_id = get_active_game()
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()
    ##TODO:  CHECK THAT THE INPUT IS VALID(STEP EXISTS, NOT ALREADY COMPLETED)


    ###FIRST, COMPLETE THE PLAYER'S SPECIFIED SUBSTEP
    sqlStr = "INSERT INTO turtle.game_substep_completions (discord_id, game_id, step_id, substep_id, time_completed) VALUES (" + str(discord_id) + ", " + str(game_id) + ", " + str(step_id) + ", " + str(substep_id) + ", NOW());"
    print(sqlStr)
    cur.execute(sqlStr)
    conn.commit()

    ##NEXT, CHECK IF THIS COMPLETES A STEP

    #gather max substep completed
    sqlStr = "SELECT max(substep_id) from turtle.game_substep_completions WHERE game_id = " + str(game_id) + " AND discord_id = " + str(discord_id) + " AND step_id = " + str(step_id) + ";"
    print(sqlStr)
    cur.execute(sqlStr)
    result = cur.fetchall()
    #TODO: make this fail gracefully, but for now I think I just want the error to print to console
    max_substep = result[0][0]

    #gather the max substep for this step
    sqlStr = "SELECT substeps FROM turtle.game_steps WHERE game_id = " + str(game_id) + " AND step_id = " + str(step_id) + ";"
    print(sqlStr)
    cur.execute(sqlStr)
    result = cur.fetchall()
    #TODO:  fail gracefully
    num_substeps = result[0][0]


    if num_substeps == max_substep:
        #Step completed!  Update the step table
        sqlStr = "INSERT INTO turtle.game_step_completions (discord_id, game_id, step_id, time_completed) VALUES (" + str(discord_id) + ", " + str(game_id) + ", "+ str(step_id) + ", NOW());"
        print(sqlStr)
        cur.execute(sqlStr)
        conn.commit()
    #else player has more substeps, so don't write a step_completion

    return True

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



def get_active_substep(discord_id):
    game_id = get_active_game()
    active_step = get_active_step(discord_id)
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()

    sqlStr = "SELECT max(substep_id) FROM turtle.game_substep_completions WHERE discord_id = " + str(discord_id) + " AND game_id = " + str(game_id) + " AND step_id = " + str(active_step) + ";"
    cur.execute(sqlStr)
    result = cur.fetchall()
    try:
        if result[0][0] is None:
            return 1  #If no compelted substeps, active substep is 1
        max_completed_substep =  result[0][0]
        return max_completed_substep + 1 # active substep is 1 more than max_completed_substep
    except:
        return None

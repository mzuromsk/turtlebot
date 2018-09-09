import discord
import asyncio
import datetime
import turtlecheck
import cogs.api as api
import grandturtlegame_question_classes as game_class
from discord.ext import commands
import psycopg2
import turtle_credentials as tc
from discord import NotFound
import regex

import logging
logger = logging.getLogger(__name__)

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
    async def game_turn_bot_status_off(self, ctx):
        await self.bot.change_presence(activity=None)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_admin)
    async def game_turn_bot_status_on(self,ctx):
        game_info = await get_active_game_info()
        game_name = game_info[1]
        await self.bot.change_presence(activity=discord.Game(name='Grand Game: {0}'.format(game_name)))

    @commands.command(brief="Briefly proclaim your Grand Game prowess. [Cooldown: 5 min]")
    @commands.cooldown(1,300,commands.BucketType.user)
    async def game_rank(self,ctx):
        try:
            await ctx.message.delete()
        except:
            pass

        most_recent_game_placement = await get_grand_game_placement(ctx.message.author.id)

        if most_recent_game_placement==0:
            await ctx.message.author.send("```Either a new game is currently running, or you did not place in the most recently completed Siege Turtle Grand Game. No game rank finisher for you (for now). Join us for the next one!```")
        elif most_recent_game_placement>3:
            message= await self.create_rank_card(ctx, most_recent_game_placement)
            await asyncio.sleep(10)
            await message.delete()
        elif most_recent_game_placement==3:
            message= await self.create_rank_card(ctx, most_recent_game_placement)
            await asyncio.sleep(15)
            await message.delete()
        elif most_recent_game_placement==2:
            message= await self.create_rank_card(ctx, most_recent_game_placement)
            await asyncio.sleep(15)
            await message.delete()
        elif most_recent_game_placement==1:
            message= await self.create_rank_card(ctx, most_recent_game_placement)
            await asyncio.sleep(20)
            await message.delete()

    async def create_rank_card(self, ctx, place):
        #Format all the strings
        if ctx.message.author.nick is not None:
            description_string = "**{0}**".format(ctx.message.author.nick)
        else:
            description_string= "**{0}**".format(ctx.message.author.name)

        emoji_trophy = discord.utils.get(ctx.author.guild.emojis, name='trophy_icon')

        if place==1:
            image_url = 'https://cdn.discordapp.com/attachments/471547983859679232/487087907434397706/TurtleGamesGold.gif'
            place_description_string = "*A God Walking Amongst Mere Mortals*"
            color_choice = 13942830
        elif place==2:
            image_url = 'https://cdn.discordapp.com/attachments/471547983859679232/487087912891056128/TurtleGamesSilver.gif'
            place_description_string = "*My Guild Hall Smells of Rich Mahogonay*"
            color_choice = 13882323
        elif place==3:
            image_url = 'https://cdn.discordapp.com/attachments/471547983859679232/487087904359841792/TurtleGamesBronze.gif'
            place_description_string = "*I Have Many Leatherbound Books*"
            color_choice = 8938544
        else:
            image_url = 'https://cdn.discordapp.com/attachments/471547983859679232/487087909825150978/TurtleGamesParticipation.gif'
            place_description_string = "*I'm Kind of a Big Deal*"
            color_choice = 3635722

        #Create the end game card embed message
        embed = discord.Embed(description=description_string, colour=color_choice)
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        embed.add_field(name=str(emoji_trophy) + ' | Finished: **#{0}**'.format(place), value=place_description_string, inline=False)

        embed.set_image(url=image_url)
        rank_card = await ctx.send(embed=embed)
        return(rank_card)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def print_active_leaderboard_message_id(self, ctx):
        #await ctx.author.send("active leaderboard id message id:")
        await ctx.author.send(get_active_leaderboard_message_id())

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def game_delete_active_leaderboard_from_database(self, ctx):
        await delete_active_leaderboard_from_database(ctx)

    async def add_turtle_to_game(self, ctx, join_settings):
        #First check to make sure there is a currently running game. If there is, continue, if there is not, message the user and return
        game_id = get_active_game()
        if game_id == -1:
            await ctx.message.author.send("```There is no currently running Grand Game. Keep an eye on the Guild Message of the Day and Discord for future Grand Game announcements.```")
            return

        #Next check to see if the user is currently listed in the game
        #If they are, send them a message asking them to confirm that they'd like to reset their progress. If they do, continue
        if get_active_step(ctx.message.author.id)>1:
            message = await ctx.message.author.send("```You have already made progress in the currently running Grand Game.\nIf you would like to completely restart the current game, click ✅ to confirm a game restart. \nIf you want to maintain your current progress in the game, click ❌ to cancel.```")
            await message.add_reaction('✅')
            await message.add_reaction('❌')

            def r_check(r, user):
                return user == ctx.author and r.count > 1

            try:
                ans, user = await self.bot.wait_for('reaction_add', check=r_check, timeout=300.0)
            except asyncio.TimeoutError:
                await ctx.author.send('Sorry. You took to long to select your choice. If you would like to retry, re-enter the command in a text channel and the bot will re-message you.')
            else:
                if str(ans.emoji) == '✅':
                    await ctx.author.send('Your current progress is being reset.')
                    #Check all the db tables for discord id and delete any entries
                    await message.delete()
                if str(ans.emoji) == '❌':
                    await ctx.author.send('Your current progress in the game has been preserved.')
                    await message.delete()
                    return
        else:
            await ctx.message.author.send("We are getting you ready to join the game! Just a few more things to set up: checking leaderboard data and API keys now.")

        await delete_turtle_from_all_game_progress_databases(ctx)

        #If an API key is going to be needed for this game, check to see if the user has a valid saved API key.
        #If they don't message them asking them to run the setup API command. If they do, continue
        if api.get_api_key(ctx.message.author.id)==None:
            await ctx.message.author.send("```This Grand Game requires that you have a linked GW2 API key to participate. \nIn order to link an API key to your discord account, enter the command $set_api_key.\nFor a video guide on how to create an API Key (and select the correct permissions), enter the command $help_api_key.``````In order to participate in this Grand Game, make sure you allow at least [Account][Inventories][Characters][Progression] permissions when creating your API key.```")
            return

        #Add user to leaderboard with no steps completed and the timestamp of when they started
        await add_turtle_to_leaderboard(ctx)
        await self.update_leaderboard(ctx)

        #Send "Joined Game" Card
        joined_game_card = await self.create_joined_game_card(ctx, join_settings)
        logging.info("{} joined the game: {}".format(ctx.author.name,join_settings.gamename))

    async def create_joined_game_card(self, ctx, card_settings):
        #Format all the strings
        description_string = "__**You have joined Grand Game: {0}!**__".format(card_settings.gamename)
        gamename_string = "Grand Game: " + card_settings.gamename

        time = datetime.datetime.utcnow()
        game_info = await get_active_game_info()
        game_start_time = game_info[3]-datetime.timedelta(hours=4)
        game_end_time = game_info[4]-datetime.timedelta(hours=4)

        embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')

        question_string = ":key2: | " + str(card_settings.steps) + " `$hiddenkeys`"
        question_description_string = "This game has " + str(card_settings.steps) + " `$hiddenkeys`. To finish the game, you must discover and earn all " + str(card_settings.steps) + " in order (a later key only works if you have earned all preceding keys). ```All hidden keys are of the form: $key_insertnameofkeyhere.```  ```Some keys you will earn merely from discovering them, others may require you to answer followup questions to earn.```\n"
        embed.add_field(name=question_string, value=question_description_string, inline=False)

        emoji_chest = discord.utils.get(ctx.author.guild.emojis, name='chest_icon')
        emoji_trophy = discord.utils.get(ctx.author.guild.emojis, name='trophy_icon')
        emoji_golem = discord.utils.get(ctx.author.guild.emojis, name='blue_golem')

        if card_settings.image_url != '' and card_settings.image_url is not None:
           embed.set_image(url=card_settings.image_url)

        leaderboard_channel_id = await get_active_leaderboard_channel_id()
        leaderboard_channel = self.bot.get_channel(leaderboard_channel_id)

        leaderboard_string = str(emoji_trophy) + ' | Game Leaderboard'
        leaderboard_description_string = "The leaderboard for this game was created in text channel `#" + leaderboard_channel.name + "`. It will update periodically with player progress."
        embed.add_field(name=leaderboard_string, value=leaderboard_description_string, inline=False)

        gametime_string = ':hourglass: | Game Duration'
        gametime_description_string = "```This game began: \n{0} \nThis game will end: \n{1}```".format(game_start_time.strftime("%I:%M%p EST %A, %m/%d/%y"), game_end_time.strftime("%I:%M%p EST %A, %m/%d/%y"))
        embed.add_field(name=gametime_string, value=gametime_description_string, inline=False)

        if card_settings.prize_list != [] and card_settings.prize_list is not None:
            prize_string = str(emoji_chest) + ' | Game Prize List'
            place = 1
            prize_description_string = '```'
            for prize in card_settings.prize_list:
                prize_description_string = prize_description_string + str(place) + ") " + prize + "\n"
                place +=1
            prize_description_string+='```'
            embed.add_field(name=prize_string, value=prize_description_string, inline=False)

        if card_settings.link_attachments != [] and card_settings.link_attachments != []:
            help_string = str(emoji_golem) + ' | Potentially helpful links'
            help_description_string = ''
            for link_and_name in card_settings.link_attachments:
                help_description_string += "**"+link_and_name[0] + "**:  " + link_and_name[1] + "\n"
            embed.add_field(name=help_string, value=help_description_string, inline = False)

        embed.add_field(name=':mag_right: | Clue for your first `$hiddenkey`', value=card_settings.clue_text, inline=False)

        #Create the start card embed message

        #Send it to the user
        joined_game_card = await card_settings.ctx.author.send(embed=embed)
        return(joined_game_card)


    async def create_start_card(self, card_settings, active_substep):
        #Format all the strings
        description_string = "```$" + card_settings.keyname + "```" + "\n**Congratulations!** You have `found` the hidden key `$" + card_settings.keyname + "`, but now you have to prove your worth to earn it. This key involves:\n\n \n"
        gamename_string = "Grand Game: " + card_settings.gamename
        if card_settings.substeps==1:
            substeps_string = ':footprints: | ' + str(card_settings.substeps) + ' step '
            substeps_description_string = 'To earn this key, you will have to correctly complete ' + str(card_settings.substeps) + ' question.'
            stopwatch_description_string = 'The questions in this series have a default time limit of ' + str(card_settings.timer) + ' minutes.\n[Unless otherwise indicated]\n\n'
        else:
            substeps_string = ':footprints: | ' + str(card_settings.substeps) + ' steps'
            substeps_description_string = 'To earn this key, you will have to correctly complete ' + str(card_settings.substeps) + ' questions.\n'
            stopwatch_description_string = 'The questions in this series have a default time limit of ' + str(card_settings.timer) + ' minutes.\n[Unless otherwise indicated]\n\n'

        if active_substep > 1:
            substeps_string += ' (Resuming on step {0})'.format(active_substep)

        if card_settings.cooldown==0:
            cooldown_string = ':repeat: | No cooldown'
            cooldown_description_string = 'This hidden key has no cooldown. If you answer any step incorrectly, you can `immediately` reattempt the key by retyping the hidden key ' + '`$' +card_settings.keyname+ '` in any ST text channel'
        else:
            cooldown_string = ':repeat: | ' + str(card_settings.cooldown) + ' minute cooldown'
            cooldown_description_string = 'This hidden key has a ' + str(card_settings.cooldown) + ' minute cooldown (measured from when you entered the key). If you fail, you will have to wait the remaining cooldown period to retry the key.\n'

        stopwatch_string = ':stopwatch: | ' + str(card_settings.timer) + ' minute question time limit'

        ready_string = 'Ready to get started, {0}?\n'.format(card_settings.ctx.author.name)
        ready_description_string = 'When you are ready to begin, click ✅. You have ' + str(card_settings.timer) + ' minutes before this attempt will time out and you must re-enter the key.'

        time = datetime.datetime.utcnow()

        if card_settings.description:
            #Create the start card embed message and show all descriptions
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/192385258736451585/479126995599491078/key.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name=substeps_string, value=substeps_description_string, inline=False)
            embed.add_field(name=cooldown_string, value=cooldown_description_string, inline=False)
            embed.add_field(name=stopwatch_string, value=stopwatch_description_string, inline=False)
            embed.add_field(name=ready_string, value=ready_description_string)

        else:
            #Create the start card embed message and hide descriptions
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/192385258736451585/479126995599491078/key.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name=substeps_string+'\n\n'+cooldown_string+'\n\n'+stopwatch_string+'\n\n'+ready_string, value=ready_description_string)


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

        description_string = "`$" + card_settings.keyname + "`" + " | Step " + str(card_settings.substep_number) + " of " + str(card_settings.substeps) + " | :stopwatch: " + str(card_settings.timer) + ' minutes\n'
        if card_settings.question_description:
            description_string+="```Select your answer from the choices below. You make a selection by clicking the associated reaction.```"
        gamename_string = "Grand Game: " + card_settings.gamename

        time = datetime.datetime.utcnow()

        with card_settings.ctx.author.dm_channel.typing():
            #Create the start card embed message
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/189526271288410112/479417475025469483/SelectOne.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name=':mag_right: | The Clue', value=card_settings.clue_text, inline=False)

            self.add_any_links_files_or_image_to_embed(embed, card_settings)

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

            await self.attach_any_files(card_settings)

            return(card)


    async def create_text_card(self, card_settings):
        #TODO: Edit so that it just accepts a choose_one_card class instance

        description_string = "`$" + card_settings.keyname + "`" + " | Step " + str(card_settings.substep_number) + " of " + str(card_settings.substeps) + " | :stopwatch: " + str(card_settings.timer) + ' minutes\n'
        if card_settings.question_description:
            description_string+="```Type in your answer: it may be a single word or a longer phrase.\n\nNote: Spelling counts, but not punctuation.```"

        gamename_string = "Grand Game: " + card_settings.gamename

        time = datetime.datetime.utcnow()

        with card_settings.ctx.author.dm_channel.typing():
            #Create the start card embed message
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/189526271288410112/479417402107363328/textinput.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name=':mag_right: | The Clue', value=card_settings.clue_text, inline=False)

            self.add_any_links_files_or_image_to_embed(embed, card_settings)

            #Send it to the user
            card = await card_settings.ctx.author.send(embed=embed)
            await self.attach_any_files(card_settings)
        return(card)


    async def create_get_in_game_card(self, card_settings):
        #TODO: Add API key lookup
        description_string = "`$" + card_settings.keyname + "`" + " | Step " + str(card_settings.substep_number) + " of " + str(card_settings.substeps) + " | :stopwatch: " + str(card_settings.timer) + ' minutes\n'
        if card_settings.question_description:
            description_string+="```Figure out the clue and find the corresponding item in game. When you have the item in your inventory, click the checkmark to begin the scan. \n\nNote: Requires a full API key. Scan completes in 5 minutes.```"

        gamename_string = "Grand Game: " + card_settings.gamename

        time = datetime.datetime.utcnow()

        with card_settings.ctx.author.dm_channel.typing():
            #Create the start card embed message
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/189526271288410112/479417574619086859/Inventory.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name=':mag_right: | The Clue', value=card_settings.clue_text, inline=False)
            self.add_any_links_files_or_image_to_embed(embed, card_settings)
            ready_string = 'Ready to get started, {0}?\n'.format(card_settings.ctx.author.name)
            ready_description_string = 'When you have the mystery item in your inventory, click ✅.'

            #Send it to the user
            card = await card_settings.ctx.author.send(embed=embed)

            #Add all the reactions
            await card.add_reaction('✅')
            await card.add_reaction('❌')

            await self.attach_any_files(card_settings)
            return(card)


    async def create_combination_card(self, card_settings):
        description_string = "`$" + card_settings.keyname + "`" + " | Step " + str(card_settings.substep_number) + " of " + str(card_settings.substeps) + " | :stopwatch: " + str(card_settings.timer) + ' minutes\n'
        if card_settings.question_description:
            description_string+="\n```Solve this combination lock by selecting the reactions below in the correct order. To select a reaction, click it so that it increments from 1 to 2. \nNote: you can not reset a mistake - you must complete your attempt and then retry the hidden key.```"

        gamename_string = "Grand Game: " + card_settings.gamename

        time = datetime.datetime.utcnow()

        with card_settings.ctx.author.dm_channel.typing():
            #Create the start card embed message
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/189526271288410112/479417522861637643/combinationlock.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name=':mag_right: | The Clue', value=card_settings.clue_text, inline=False)
            self.add_any_links_files_or_image_to_embed(embed, card_settings)
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

            await self.attach_any_files(card_settings)
            return(card)


    async def create_earned_key_card(self, card_settings):
        #Check to see if we just finished the game by checking the final game step
        game_id = get_active_game()
        number_of_game_steps = get_number_of_game_steps(game_id)

        #Send a card with a earned-key card with a clue for the next key
        if card_settings.step_number==number_of_game_steps:
            logging.info("{0} FINISHED game {1}".format(card_settings.ctx.message.author.name, card_settings.gamename))

            #Format all the strings
            description_string = "```Congratulations! \nYou have finished Grand Game: \n{0}```".format(card_settings.gamename)
            gamename_string = "Grand Game: " + card_settings.gamename

            time = datetime.datetime.utcnow()
            game_info = await get_active_game_info()
            game_start_time = game_info[3]-datetime.timedelta(hours=4)
            game_end_time = game_info[4]-datetime.timedelta(hours=4)
            gametime_string = ':hourglass: | Game Duration'
            gametime_description_string = "```This game began: \n{0} \nThis game will end: \n{1}```".format(game_start_time.strftime("%I:%M%p EST %A, %m/%d/%y"), game_end_time.strftime("%I:%M%p EST %A, %m/%d/%y"))

            emoji_trophy = discord.utils.get(card_settings.ctx.author.guild.emojis, name='trophy_icon')
            emoji_chest = discord.utils.get(card_settings.ctx.author.guild.emojis, name='chest_icon')

            leaderboard_data = await get_leaderboard_data()
            number_of_competitors = len(leaderboard_data)

            place = 1
            for turtle in leaderboard_data:
                if turtle[0] == card_settings.ctx.message.author.id:
                    break
                place+=1
            else:
                place = "```Unknown```"

            leaderboard_description_string = "You finished ranked **#{0}** out of {1} participants and completed all {2} out of {2} game steps.".format(place,number_of_competitors,number_of_game_steps)

            prize_string = str(emoji_chest) + ' | Game Prizes'
            prize_description_string = 'Any earned prizes and rank placements will be awarded when the game ends.'


            #Create the end game card embed message
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name=str(emoji_trophy) + ' | Final Leaderboard Placement', value=leaderboard_description_string, inline=False)
            embed.add_field(name=gametime_string, value=gametime_description_string, inline=False)
            embed.add_field(name=prize_string, value=prize_description_string, inline=False)

        else:
            #Format all the strings
            description_string = "```$" + card_settings.keyname + "```" + "\n**Congratulations!** You have now fully `earned` the hidden key `$" + card_settings.keyname + "`!\n\n \n"
            gamename_string = "Grand Game: " + card_settings.gamename

            emoji_trophy = discord.utils.get(card_settings.ctx.author.guild.emojis, name='trophy_icon')

            leaderboard_description_string = 'Your progress in game has been saved. The leaderboard display will update at the next game checkpoint.'

            unlocked_next_clue_description_string = 'The next clue is provided below. If you take a break and forget where you left off, you can always type: $game_my_last_clue into any ST text channel.'

            time = datetime.datetime.utcnow()

            #Create the earned key card embed message
            embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/192385258736451585/479478074702954496/crossedkeys.png')
            embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.add_field(name=str(emoji_trophy) + ' | Leaderboard', value=leaderboard_description_string, inline=False)
            embed.add_field(name=':unlock: | You have unlocked the ability to use the next hidden key!', value=unlocked_next_clue_description_string, inline=False)
            embed.add_field(name=':mag_right: | Clue for your next `$hiddenkey`', value=card_settings.clue_text, inline=False)

        #Add any images, files, attachments
        self.add_any_links_files_or_image_to_embed(embed, card_settings)


        #Send it to the user
        card = await card_settings.ctx.author.send(embed=embed)
        return(card)

    def add_any_links_files_or_image_to_embed(self, embed, card_settings):
        #If there are links, add a field to keep track of them
        if card_settings.link_attachments != [] and card_settings.link_attachments != []:
            emoji_golem = discord.utils.get(card_settings.ctx.author.guild.emojis, name='blue_golem')
            help_string = str(emoji_golem) + ' | Potentially helpful links'
            help_description_string = ''
            for link_and_name in card_settings.link_attachments:
                help_description_string += "**"+link_and_name[0] + "**:  " + link_and_name[1] + "\n"
            embed.add_field(name=help_string, value=help_description_string, inline = False)

        #If there are files to attach, attach and label them
        if card_settings.file_attachments != [] and card_settings.file_attachments is not None:
            number_of_attachments = len(card_settings.file_attachments)
            if number_of_attachments == 1:
                embed.add_field(name='Potentially Useful File', value='The file is provided below this message.', inline=False)
            else:
                embed.add_field(name='Potentially Useful Files', value='{0} files are provided below this message.'.format(number_of_attachments), inline=False)

        #If there is an image file, include it in the embed
        if card_settings.image_url != '' and card_settings.image_url is not None:
           embed.set_image(url=card_settings.image_url)

    async def attach_any_files(self, card_settings):
        #If there are files to attach, attach and label them
        if card_settings.file_attachments != [] and card_settings.file_attachments is not None:
            number_of_attachments = len(card_settings.file_attachments)
            if number_of_attachments == 1:
                await card_settings.ctx.author.send('```The following file is for step {0} of ${1}```'.format(card_settings.substep_number, card_settings.keyname))
            else:
                await card_settings.ctx.author.send('```The following {0} files are for step {1} of ${2}```'.format(number_of_attachments, card_settings.substep_number, card_settings.keyname))

            count = 1
            for item in card_settings.file_attachments:
                ext = item.split(".")[-1]
                file_item = discord.File(item, filename="File{0}_Step{1}_${2}.{3}".format(count,card_settings.substep_number,card_settings.keyname,ext))
                await card_settings.ctx.author.send(file=file_item)
                count +=1

            if number_of_attachments == 1:
                await card_settings.ctx.author.send('```End of file for step {0} of ${1}. Don\'t forget to scroll back up to view the entire clue! ```'.format(card_settings.substep_number, card_settings.keyname))
            else:
                await card_settings.ctx.author.send('```End of files for step {0} of ${1}. Don\'t forget to scroll back up to view the entire clue!```'.format(card_settings.substep_number, card_settings.keyname))


    async def run_hidden_key(self, ctx, earned_key_card_settings, start_card_settings=None, question_cards_settings=None):
        #Get the starting time
        start_time = datetime.datetime.utcnow()

        #If there are no additional substeps, just send the earned_card
        if question_cards_settings is None:
            #Send the earned card for this hidden key
                try:
                    earned_key_card = await self.create_earned_key_card(earned_key_card_settings)
                    logging.info('{} has earned key {}'.format(ctx.message.author.name,earned_key_card_settings.keyname))
                    complete_substep(ctx.author.id, earned_key_card_settings.step_number, 1)
                except discord.Forbidden:
                    return await ctx.send('I do not have permission to DM you. Please enable this in the future.')
                await update_leaderboard_data(ctx.message.author.id)
                await self.update_leaderboard(ctx)
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
                start_card = await self.create_start_card(start_card_settings, active_substep)
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
                logging.info("{0} is on game step {1} substep {2}".format(ctx.author.name,question_cards_settings[current_substep_index].step_number, question_cards_settings[current_substep_index].substep_number))
                response = await self.check_if_question_answer_is_correct(question_cards_settings[current_substep_index], start_time)
                if response['bot_response_message'] != '':
                    await ctx.author.send(response['bot_response_message'])

                if response['answer_status'] == 'TimeoutError' or response['answer_status'] == 'Incorrect':
                    key_is_at_end_state=True
                    return
                elif response['answer_status'] == 'Correct':
                    #If we are on the last question:
                    if current_substep_index + 1 == len(question_cards_settings):
                        #Send Card to user
                        earned_key_card = await self.create_earned_key_card(earned_key_card_settings)
                        logging.info('{} has earned key {}'.format(ctx.message.author.name,earned_key_card_settings.keyname))

                        #Update leaderboard data
                        complete_substep(ctx.author.id, question_cards_settings[current_substep_index].step_number, question_cards_settings[current_substep_index].substep_number)
                        await update_leaderboard_data(ctx.message.author.id)

                        #Update leaderboard
                        leaderboard_data = await self.update_leaderboard(ctx)

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
            logging.info('{2} | Choose One Question | The clicked answer: {0} The current expected correct answer: {1}'.format(str(pick_one_answer).encode("UTF-8"),str(question_card_settings.emoji[question_card_settings.correct_item_in_list-1]).encode("UTF-8"),question_card_settings.ctx.message.author.name))
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
                logging.info('{2} | Combination Question | The clicked answer: {0} The current expected correct answer: {1}'.format(str(answer).encode("UTF-8"),str(current_correct_answer).encode("UTF-8"),question_card_settings.ctx.message.author.name))

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
            matched_correct_answer = False
            for item in question_card_settings.correct_answer_text:
                if item[0]=='exact':
                    if self.text_strip_punctuation_and_cleanup(text_answer.content) == self.text_strip_punctuation_and_cleanup(item[1]):
                        logging.info("{2} | Exact match for \"{0}\" with answer key \"{1}\"".format(text_answer.content, item[1], question_card_settings.ctx.message.author.name))
                        matched_correct_answer=True
                        break
                    else:
                        logging.info("{2} | FAILED Exact match for \"{0}\" with answer key \"{1}\"".format(text_answer.content, item[1], question_card_settings.ctx.message.author.name))
                elif item[0]=='keyword':
                    if self.text_strip_punctuation_and_cleanup(item[1]) in self.text_strip_punctuation_and_cleanup(text_answer.content):
                        logging.info("{2} | Keyword match for \"{0}\" with answer key \"{1}\"".format(text_answer.content, item[1], question_card_settings.ctx.message.author.name))
                        matched_correct_answer=True
                        break
                    else:
                        logging.info("{2} | FAILED Keyword match for \"{0}\" with answer key \"{1}\"".format(text_answer.content, item[1], question_card_settings.ctx.message.author.name))

            if matched_correct_answer:
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
                logging.info("{} began an account scan on question Step {} Substep {} for item {}".format(question_card_settings.ctx.author.name,question_card_settings.step_number, question_card_settings.substep_number,question_card_settings.item_id))
                with question_card_settings.ctx.author.dm_channel.typing():
                    timing_card = await self.create_timing_card(question_card_settings)

                    max_wait = 5

                    for minute in range(0, max_wait):
                        time_message = await question_card_settings.ctx.author.send('```Approximate time remaining for scan: {0} min```'.format(max_wait-minute))
                        await asyncio.sleep(60)
                        await time_message.delete()


                    total, output, item_result = await self.api.simple_search(question_card_settings.ctx, question_card_settings.item_id)
                    await timing_card.delete()
                    if total >= question_card_settings.required_amount:
                        search_result_card = await self.create_search_results_card(question_card_settings, output, item_result)
                        bot_response_message = '```You had the necessary number of the correct item ({0}) on your account. Well done!```'.format(item_result["name"])
                        logging.info('{} received scan response: '.format(question_card_settings.ctx.message.author.name) + bot_response_message)
                        return{ 'answer_status': 'Correct', 'bot_response_message': bot_response_message}
                    elif total > 0:
                        search_result_card = await self.create_search_results_card(question_card_settings, output, item_result)
                        bot_response_message = "```I\'m sorry, although you did have the correct item ({0}), you did not have the necessary amount.```".format(item_result["name"]) + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
                        logging.info('{} received scan response: '.format(question_card_settings.ctx.message.author.name) + bot_response_message)
                        return{ 'answer_status': 'Incorrect', 'bot_response_message': bot_response_message}
                    elif total ==0:
                        bot_response_message = "```I\'m sorry, you did not have the correct item. \nWe have peered into the mists and did not find the correct item anywhere on your account.```" + self.format_retry_message(start_time, question_card_settings.keyname, question_card_settings.cooldown)
                        logging.info('{} received scan response: '.format(question_card_settings.ctx.message.author.name) + bot_response_message)
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

    @commands.command(hidden=True,brief='Initialize a new leaderboard in this location.')
    @commands.check(turtlecheck.if_seaguard)
    async def game_initialize_leaderboard(self, ctx, name='Grand Siege Turtle Games'):
        #Make sure the message gets deleted before someone else can see it (in case the general flag doesn't catch it)
        try:
            await ctx.message.delete()
        except:
            pass

        leaderboard = await self.initialize_leaderboard(ctx, name)

    #This is a version of the command that can be called by other commands as needed if an active leaderboard can't be found
    async def initialize_leaderboard(self, ctx, game_id, name='Grand Siege Turtle Games'):

        title_string = '__** Leaderboard  |  ' + name + '**__'

        embed = discord.Embed(title=title_string, colour=0x76AFA5, url='https://www.youtube.com/watch?v=9jK-NcRmVcw&mute=1')
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.set_footer(text='No turtles have made it onto the leaderboard. Yet.', icon_url='https://cdn.discordapp.com/attachments/471547983859679232/478072773659328524/108145_time_512x512.png')

        leaderboard = await ctx.send(embed=embed)
        leaderboard_message_id = leaderboard.id
        leaderboard_channel_id = leaderboard.channel.id
        leaderboard_name = name

        await save_initialized_leaderboard_to_database(ctx, leaderboard_channel_id, leaderboard_message_id, leaderboard_name)

        return(leaderboard)

    @commands.command(hidden=True,brief='Updates the game leaderboard.')
    @commands.check(turtlecheck.if_seaguard)
    async def game_update_leaderboard(self, ctx, name='Grand Siege Turtle Games'):
        #Make sure the message gets deleted before someone else can see it (in case the general flag doesn't catch it)
        await self.update_leaderboard(ctx)

    async def update_leaderboard(self, ctx, shutdown=False):

        game_info = await get_active_game_info()
        game_id = game_info[0]
        game_name = game_info[1]
        game_start_time = game_info[3]
        game_start_time_est = game_start_time-datetime.timedelta(hours=4)
        game_end_time = game_info[4]
        game_end_time_est = game_end_time-datetime.timedelta(hours=4)
        game_leaderboard_update_count = game_info[5]

        ######################################################
        #Currently the code assumes the following order from the resulting query
        #discord_id name nickname current_farthest_sucessful_step_number timestamp_most_recent_progress
        the_grand_game = []
        the_grand_game = await get_leaderboard_data()

        ########################################################

        time = datetime.datetime.utcnow()
        elapsed_time = time - game_start_time

        #If we are within 10 minutes of the start of the game
        if elapsed_time.total_seconds() < 10*60 and shutdown==False:
            if game_leaderboard_update_count >= 2:
                #Reset the leaderboard count
                await set_leaderboard_update_count(0)
            else:
                #Increment leaderboard update count and return
                await set_leaderboard_update_count(game_leaderboard_update_count+1)
                return the_grand_game
        elif elapsed_time.total_seconds() < 30*60 and shutdown==False:
            if game_leaderboard_update_count >= 1:
                #Reset the leaderboard count
                await set_leaderboard_update_count(0)
            else:
                #Increment leaderboard update count and return
                await set_leaderboard_update_count(game_leaderboard_update_count+1)
                return the_grand_game

        #First try and see if we can find the current leaderboard
        try:
            leaderboard_channel_id = await get_active_leaderboard_channel_id()
            leaderboard_message_id = await get_active_leaderboard_message_id()
            leaderboard_channel = self.bot.get_channel(leaderboard_channel_id)
            leaderboard = await leaderboard_channel.get_message(leaderboard_message_id)

            updatemessage = await leaderboard_channel.send('We are updating the leaderboard in this channel...')

        except:
            #initialize a new leaderboard
            await ctx.send('Leaderboard update failed. There is no linked, currently running leaderboard for Grand Game: {0}.'.format(game_name))
            logging.warning('Leaderboard update failed.')
            return the_grand_game

        #Leaderboard display options for fancy version
        last_step_number = get_number_of_game_steps(game_id)
        max_number_full_display = 5
        max_number_on_leaderboard = 20
        number_icons_per_line =15

        with leaderboard.channel.typing():

            complete_emoji = discord.utils.get(ctx.author.guild.emojis, name='hpf')
            incomplete_emoji = discord.utils.get(ctx.author.guild.emojis, name='hpe')
            finish_emoji = discord.utils.get(ctx.author.guild.emojis, name='finish')

            if incomplete_emoji is not None and complete_emoji is not None:
                leaderboard_description_string ='**Icon Key**   '+ str(complete_emoji) + ': Step Completed   **||**   '+ str(incomplete_emoji) + ': Step Unfinished \n'
                if time > game_end_time or shutdown:
                    leaderboard_description_string +="```This game has ended. \nCongratulations to the top turtles!```"
                else:
                    leaderboard_description_string +='```Game ends:\n{0}```'.format(game_end_time_est.strftime("%I:%M%p EST %A, %m/%d/%y"))

                leaderboard_icons_succesfully_loaded = True
            else:
                leaderboard_description_string='Each number indicates a completed step in the game.'
                leaderboard_icons_succesfully_loaded = False


            #TODO: Edit this so it looks up the leaderboard name in the lookup table
            leaderboard_title_string = '__**The Leaderboard  |  ' + game_name + '**__'

            #Create Embed
            embed = discord.Embed(title=leaderboard_title_string, colour=0x76AFA5, url='https://www.youtube.com/watch?v=9jK-NcRmVcw&mute=1', description = leaderboard_description_string, timestamp=time)
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
            embed.set_footer(text="All above timestamps in EST | Updated at local time: ")

            #Initialize strings and counters that we need in the leaderboard generation loop

            field_value_string = ''
            chunk_name_string = ''
            place_on_leaderboard = 1
            for turtle in range(len(the_grand_game)):
                tiebreaker=False
                if turtle==0:
                    if len(the_grand_game)==1:
                        pass
                    elif the_grand_game[turtle][3] == the_grand_game[turtle+1][3]:
                        tiebreaker=True
                elif turtle < len(the_grand_game)-1:
                    if the_grand_game[turtle][3] == the_grand_game[turtle+1][3] or the_grand_game[turtle][3] == the_grand_game[turtle-1][3]:
                        tiebreaker=True
                elif turtle == len(the_grand_game)-1:
                    if the_grand_game[turtle][3] ==the_grand_game[turtle-1][3]:
                        tiebreaker=True


                #As long as the turtle has completed at least the first hint, add them to the leaderboard
                if int(the_grand_game[turtle][3]) >= 0:
                    #If there is a nickname for the turtle, use that as turtle_name
                    if the_grand_game[turtle][2] != 'No nickname':
                        turtle_name = str(the_grand_game[turtle][2])
                    else:
                        turtle_name = str(the_grand_game[turtle][1])

                    #If the turtle completed the last question add finished status to string
                    if int(the_grand_game[turtle][3]) == last_step_number:
                        finished_status = '| ' +str(finish_emoji)
                        starting_char = '~~'
                        ending_char = '~~'
                    else:
                        finished_status = ''
                        starting_char = ''
                        ending_char = ''

                    #If there is a tie add tie breaker time to string
                    if tiebreaker:
                        est_tiebreak_time = the_grand_game[turtle][4]-datetime.timedelta(hours=4)
                        tiebreak_time = '*(\@' + str(est_tiebreak_time.strftime("%I:%M%p %A, %m/%d/%y")) + ')*'
                    else:
                        tiebreak_time = ''

                    field_name_string = str(place_on_leaderboard) + ') **' + turtle_name + '** ' + finished_status
                    if len(field_name_string)>25:
                        field_name_string+='\n'
                    field_name_string+= tiebreak_time

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

                            next_turtle_string = str(place_on_leaderboard) + ')  **|  ' + str(the_grand_game[turtle][3]) + '/' + str(last_step_number) + ' ' + str(complete_emoji) + '  |  ' + turtle_name + '** ' + finished_status + ' '
                            if len(next_turtle_string)>60:
                                next_turtle_string += '\n'
                            next_turtle_string += tiebreak_time + '\n'
                            field_value_string = field_value_string + next_turtle_string

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
                logging.info('Updating leaderboard...')
                await leaderboard.edit(embed=embed, content=None)
                logging.info('Leaderboard updated.')
            except:
                await ctx.send(embed=embed)
        try:
            await updatemessage.delete()
        except:
            pass

        return the_grand_game

    @commands.command(hidden=True,brief='DEBUG ONLY - MOVES AUTHOR FORWARD ONE SUBSTEP')
    @commands.check(turtlecheck.if_admin)
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

    async def start_the_game(self, ctx, game_name, game_steps, num_days=2, num_hours=0):
        game_id = await create_new_active_game(game_name, num_days, num_hours)
        await create_game_substeps_in_db(game_id, game_steps)
        await reset_grand_game_placements()
        await self.initialize_leaderboard(ctx, game_id, game_name)
        await self.bot.change_presence(activity=discord.Game(name='Grand Game: {0}'.format(game_name)))

    @commands.command(hidden=True,brief='ADMIN ONLY')
    @commands.check(turtlecheck.if_admin)
    async def game_begin_countdown(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass

        #You must hand list the number of steps and substeps
        #Create a list of length step, where each step value is the number of substeps in that step
        game_info = await get_active_game_info()
        game_name = game_info[1]
        game_start_time = game_info[3]
        game_end_time = game_info[4]
        time = datetime.datetime.utcnow()
        update_interval = 5 #In minutes

        while time < game_end_time:
            time_remaining = game_end_time-time
            intervals_remaining, remainder_in_seconds = divmod(time_remaining.total_seconds(), 60*update_interval)
            if intervals_remaining > 1:
                sleep_time = update_interval*60
                await self.bot.change_presence(activity=discord.Game(name='[Ends in ~ {0}min] Grand Game: {1}'.format(int(intervals_remaining*update_interval), game_name)))
            elif (intervals_remaining*60 + remainder_in_seconds) > 60:
                sleep_time = 30
                minutes, remainder = divmod(time_remaining.total_seconds(), 60)
                await self.bot.change_presence(activity=discord.Game(name='[Ends in {0}min] Grand Game: {1}'.format(int(minutes), game_name)))
            else:
                sleep_time = 10
                if remainder_in_seconds < sleep_time:
                    sleep_time = remainder_in_seconds+1
                await self.bot.change_presence(activity=discord.Game(name='[Ends in {0}s] Grand Game: {1}'.format(int(remainder_in_seconds), game_name)))

            logging.info("Grand Game: {0} ends in {1}".format(game_name,time_remaining))
            await asyncio.sleep(sleep_time)
            time = datetime.datetime.utcnow()

        await self.shutdown_grand_game(ctx, game_name)

    @commands.command(hidden=True,brief='ADMIN ONLY')
    @commands.check(turtlecheck.if_admin)
    async def game_shutdown_now(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass

        game_info = await get_active_game_info()
        game_name = game_info[1]
        await self.shutdown_grand_game(ctx, game_name)

    async def shutdown_grand_game(self, ctx, game_name):
        logging.info("Grand Game: {0} has closed.".format(game_name))

        leaderboard_channel_id = await get_active_leaderboard_channel_id()
        leaderboard_channel = self.bot.get_channel(leaderboard_channel_id)
        final_leaderboard_data = await self.update_leaderboard(ctx, shutdown=True)
        game_id = get_active_game()
        await asyncio.sleep(2)
        #Finally, turn off ALL active games to be safe
        await set_all_games_inactive()

        await leaderboard_channel.send("```Grand Game: {0} has finished! No further progress will be added to the leaderboard.```".format(game_name))
        await self.bot.change_presence(activity=discord.Game(name='Finished Grand Game: {0}'.format(game_name)))

        number_of_game_steps = get_number_of_game_steps(game_id)
        place = 1
        number_of_competitors = len(final_leaderboard_data)
        for turtle in final_leaderboard_data:
            await set_grand_game_placement(turtle[0], place)
            await self.create_endgame_card(ctx, game_name, turtle, place, number_of_competitors, number_of_game_steps)
            place+=1

    async def create_endgame_card(self, ctx, game_name, turtle, place, number_of_competitors, number_of_game_steps):
        #Format all the strings
        description_string = "```Grand Game: {0} has closed!```".format(game_name)
        gamename_string = "Grand Game: " + game_name

        emoji_trophy = discord.utils.get(ctx.author.guild.emojis, name='trophy_icon')
        emoji_rank = discord.utils.get(ctx.author.guild.emojis, name='rank_icon')
        emoji_chest = discord.utils.get(ctx.author.guild.emojis, name='chest_icon')

        leaderboard_description_string = "You finished ranked **#{0}** out of {1} participants and completed {2} out of {3} game steps.".format(place,number_of_competitors,turtle[3],number_of_game_steps)

        unlocked_grand_game_rank_emote_string = 'You have unlocked a rank finisher based on your placement in the game. To use this finisher in any ST text channel, enter the command `$game_rank`. There is a cooldown, so use your newfound powers wisely. Access to all rank finishers resets with the arrival of the next Grand Game.'

        time = datetime.datetime.utcnow()

        if place==1:
            image_url = 'https://cdn.discordapp.com/attachments/471547983859679232/487087907434397706/TurtleGamesGold.gif'
        elif place==2:
            image_url = 'https://cdn.discordapp.com/attachments/471547983859679232/487087912891056128/TurtleGamesSilver.gif'
        elif place==3:
            image_url = 'https://cdn.discordapp.com/attachments/471547983859679232/487087904359841792/TurtleGamesBronze.gif'
        else:
            image_url = 'https://cdn.discordapp.com/attachments/471547983859679232/487087909825150978/TurtleGamesParticipation.gif'

        prize_string = str(emoji_chest) + ' | Game Prizes'
        prize_description_string = 'If you earned an in-game prize based on your placement on the leaderboard, a game administrator will contact you soon to transfer your rewards.\n```Thanks for playing!```'


        #Create the end game card embed message
        embed = discord.Embed(description=description_string, colour=1155738, timestamp=time)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.set_footer(text=gamename_string, icon_url='https://cdn.discordapp.com/attachments/473250851876765699/473597224937324554/unknown.png')
        embed.add_field(name=str(emoji_trophy) + ' | Final Leaderboard Placement', value=leaderboard_description_string, inline=False)
        embed.add_field(name=str(emoji_rank) + ' | You have unlocked a Grand Game rank emote!', value=unlocked_grand_game_rank_emote_string, inline=False)
        embed.add_field(name=prize_string, value=prize_description_string, inline=False)

        embed.set_image(url=image_url)

        #Send it to the user
        discord_handle_for_turtle = self.bot.get_user(turtle[0])
        await discord_handle_for_turtle.send(embed=embed)

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

async def set_all_games_inactive():
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()
    sqlStr = "UPDATE turtle.grand_games SET is_active=FALSE WHERE is_active = TRUE;"
    cur.execute(sqlStr)
    conn.commit()

async def reset_grand_game_placements():
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()
    sqlStr = "UPDATE turtle.turtles SET most_recent_grand_game_placement=0;"
    cur.execute(sqlStr)
    conn.commit()

async def set_grand_game_placement(discord_id, place):
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()
    sqlStr = "UPDATE turtle.turtles SET most_recent_grand_game_placement={1} WHERE discord_id ={0};".format(discord_id, place)
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    conn.commit()

async def get_grand_game_placement(discord_id):
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()
    sqlStr = "SELECT most_recent_grand_game_placement FROM turtle.turtles WHERE discord_id={0};".format(discord_id)
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    conn.commit()
    result = cur.fetchall()
    try:
        return result[0][0]
    except:
        return -1

async def set_leaderboard_update_count(count=0):
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()
    sqlStr = "UPDATE turtle.grand_games SET leaderboard_update_count = {0} WHERE is_active = TRUE;".format(count)
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    conn.commit()

async def create_new_active_game(game_name="Siege Turtle Grand Game", num_days=2, num_hours=0):
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()
    sqlStr = "UPDATE turtle.grand_games SET is_active=FALSE WHERE is_active = TRUE;"
    cur.execute(sqlStr)
    conn.commit()
    sqlStr2 = "INSERT INTO turtle.grand_games (game_name, is_active, start_time, end_time) VALUES (" + "'" + str(game_name) + "'" + ", TRUE, NOW(), NOW() + INTERVAL '" + str(num_days) + " days " + str(num_hours) + " hours')";
    cur.execute(sqlStr2)
    conn.commit()
    sqlStr3 = "SELECT game_id FROM turtle.grand_games WHERE is_active = TRUE;"
    cur.execute(sqlStr3)
    result = cur.fetchall()
    try:
        return result[0][0]
    except:
        return -1

async def create_game_substeps_in_db(game_id, game_steps):
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()
    for step in range(len(game_steps)):
        sqlStr = "INSERT INTO turtle.game_steps (game_id, step_id, substeps) VALUES (" + str(game_id) + ", " + str(step+1) + ", " + str(game_steps[step])+");"
        logging.debug(sqlStr)
        cur.execute(sqlStr)
        conn.commit()

async def get_active_game_info():
    try:
        conn
    except NameError:
        conn = tc.get_conn()
    cur = conn.cursor()
    sqlStr = "SELECT * FROM turtle.grand_games WHERE is_active = TRUE;"
    cur.execute(sqlStr)
    result = cur.fetchall()
    try:
        return result[0]
    except:
        return -1

async def get_active_leaderboard_message_id():
    game_id = get_active_game()
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

async def get_active_leaderboard_channel_id():
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
    logging.debug(sqlStr)
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
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    conn.commit()

async def delete_turtle_from_all_game_progress_databases(ctx):
    game_id = get_active_game()
    try:
        conn
    except NameError:
        conn = tc.get_conn()
    cur = conn.cursor()
    sqlStr = "DELETE FROM turtle.game_substep_completions WHERE game_id = " + str(game_id) + " AND discord_id = " + str(ctx.message.author.id) + ";"
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    conn.commit()
    sqlStr = "DELETE FROM turtle.game_step_completions WHERE game_id = " + str(game_id) + " AND discord_id = " + str(ctx.message.author.id) + ";"
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    conn.commit()
    sqlStr = "DELETE FROM turtle.the_grand_game_players WHERE game_id = " + str(game_id) + " AND discord_id = " + str(ctx.message.author.id) + ";"
    logging.debug(sqlStr)
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
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    conn.commit()

    ##NEXT, CHECK IF THIS COMPLETES A STEP

    #gather max substep completed
    sqlStr = "SELECT max(substep_id) from turtle.game_substep_completions WHERE game_id = " + str(game_id) + " AND discord_id = " + str(discord_id) + " AND step_id = " + str(step_id) + ";"
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    result = cur.fetchall()
    #TODO: make this fail gracefully, but for now I think I just want the error to print to console
    max_substep = result[0][0]

    #gather the max substep for this step
    sqlStr = "SELECT substeps FROM turtle.game_steps WHERE game_id = " + str(game_id) + " AND step_id = " + str(step_id) + ";"
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    result = cur.fetchall()
    #TODO:  fail gracefully
    num_substeps = result[0][0]


    if num_substeps == max_substep:
        #Step completed!  Update the step table
        sqlStr = "INSERT INTO turtle.game_step_completions (discord_id, game_id, step_id, time_completed) VALUES (" + str(discord_id) + ", " + str(game_id) + ", "+ str(step_id) + ", NOW());"
        logging.debug(sqlStr)
        cur.execute(sqlStr)
        conn.commit()
    #else player has more substeps, so don't write a step_completion

    return True

def get_number_of_game_steps(game_id):
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()

    sqlStr = "SELECT max(step_id) FROM turtle.game_steps WHERE game_id = " + str(game_id) + ";"
    cur.execute(sqlStr)
    result = cur.fetchall()
    try:
        if result[0][0] is None:
            return 1
        number_of_steps =  result[0][0]
        return number_of_steps
    except:
        return 1

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

async def update_leaderboard_data(discord_id):
    game_id = get_active_game()
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    active_step = get_active_step(discord_id)
    last_completed_step = active_step-1

    active_state = True

    cur = conn.cursor()
    sqlStr = "UPDATE turtle.the_grand_game_players SET last_completed_step={0}, last_completed_step_time=NOW() WHERE discord_id={1} AND game_id={2};".format(last_completed_step,discord_id,game_id)
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    conn.commit()

async def get_leaderboard_data():
    game_id = get_active_game()
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    cur = conn.cursor()
    #discord_id name nickname current_farthest_sucessful_step_number timestamp_most_recent_progress
    sqlStr = "SELECT discord_id, name, nickname, last_completed_step, last_completed_step_time FROM turtle.the_grand_game_players WHERE game_id={0} ORDER BY last_completed_step DESC, last_completed_step_time ASC;".format(game_id)
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    result = cur.fetchall()
    return result

async def add_turtle_to_leaderboard(ctx):
    game_id = get_active_game()
    try:
        conn
    except NameError:
        conn = tc.get_conn()

    nickname = ctx.message.author.nick
    if nickname is None:
        nickname = 'No nickname'

    active_state = True

    cur = conn.cursor()
    sqlStr = "INSERT INTO turtle.the_grand_game_players (game_id, discord_id, name, nickname, discriminator, last_completed_step, last_completed_step_time, is_active) VALUES (" + str(game_id) + ", " + str(ctx.message.author.id) + ", '" + str(ctx.message.author.name) + "', '" + str(nickname) + "', '" + str(ctx.message.author.discriminator) + "', " + str(0) + ", NOW(), " + str(active_state) + ");"
    logging.debug(sqlStr)
    cur.execute(sqlStr)
    conn.commit()


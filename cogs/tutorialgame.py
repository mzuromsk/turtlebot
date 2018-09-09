import discord
import asyncio
import datetime
import turtlecheck
import cogs.grandturtlegame as grandgame
import grandturtlegame_question_classes as game_class
from discord.ext import commands
import turtle_credentials as tc
from discord import NotFound

import logging
logger = logging.getLogger(__name__)

class TutorialGameControls:
    def __init__(self, bot):
        self.bot = bot
        self.GameControls = grandgame.GrandTurtleGameControls(self.bot)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def pingexamplegame(self, ctx):
        await ctx.send('Pong!')

    @commands.command(hidden=True,brief='ADMIN ONLY')
    @commands.check(turtlecheck.if_admin)
    async def game_start_tutorial(self, ctx):
        #You must hand list the number of steps and substeps
        #Create a list of length step, where each step value is the number of substeps in that step
        game_steps = [1,1,1,1,1,3]
        game_name = "Tutorial"
        num_days = 2
        num_hours = 0
        await self.GameControls.start_the_game(ctx, game_name, game_steps, num_days, num_hours)

    @commands.command(brief="Join the current [ST] Grand Game.", description="Join and start a currently running Grand Game. Note: If you have already started the current game, this command will completely reset your progress. Must be a Seaguard to participate.")
    @commands.check(turtlecheck.if_seaguard )
    async def game_join(self, ctx):
        gamename = 'Tutorial'
        steps = 6
        api_key_required = True

        join_settings = game_class.Join_Card_Settings(ctx, gamename,steps, api_key_required)
        join_settings.prize_list=["Learning How To Play"]
        join_settings.image_url='https://cdn.discordapp.com/attachments/471547983859679232/486011052161499136/Tutorial.png'
        join_settings.link_attachments = [('Tutorial Walkthrough','https://youtu.be/785cyBywYiQ'),('Cypher Tools','http://rumkin.com/tools/cipher/'),('Guild Wars 2 Wiki','http://wiki.guildwars2.com')]
        join_settings.clue_text = '```Your first hidden key is the first guild hall instance to house ST in GW2. Such were golden times.``` ```Remember, the actual hidden key must be entered in the form $key_youranswerhere. \nYou must enter your guess for the hidden key in a ST text channel (not a private message). \nThis is required for the bot to recognize your command correctly and also to remove your hidden key from prying eyes.```'
        await self.GameControls.add_turtle_to_game(ctx,join_settings)

    @commands.command(brief="Request your last completed game step and current key hint.", aliases=['game_my_last_key','game_my_last_step','my_last_clue','my_last_key'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_joined_active_game)
    async def game_my_last_clue(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass

        #REMINDER: MANUALLLY setup lists of key names and clues for the keys. The zeroth clue should be the game_join card clue for the first hidden key
        hiddenkeyclues = []
        hiddenkeyclues.append('Your first hidden key is the first guild hall instance to house ST in GW2. Such were golden times.')
        hiddenkeyclues.append('The next hidden key is the title for core members of Siege Turtles (both in discord, and in game).')
        hiddenkeyclues.append('The song "Fear not this Night" is played at a key point of the original GW2 story, where you cleanse corruption in this region of the game. Your next hidden key is $key_thenameofthisregion.')
        hiddenkeyclues.append('Trophys and trinkets exist galore in GW2. Of the top tier trophies, which one might be most sacred to a turtle? Your next hidden key is $key_thenameofthisT6material.')
        hiddenkeyclues.append('There are absolutely no culinary applications for the magical substance that constitutes the next hidden key. Your next key is $key_nameofthisrubypowderhere.')
        hiddenkeyclues.append('Strangely enough, this iconic city was not destroyed by a dragon per-say, but rather through the work of a Sylvari. A destruction salad appetizer if you will. Your next hidden key: $key_thenameofthiscity.')

        hiddenkeys = []
        hiddenkeys.append('$game_join')
        hiddenkeys.append('$key_gildedhollow')
        hiddenkeys.append('$key_seaguard')
        hiddenkeys.append('$key_orr')
        hiddenkeys.append('$key_armoredscale')
        hiddenkeys.append('$key_bloodstonedust')
        hiddenkeys.append('$key_lionsarch')

        #END MANUAL SETUP OF KEYNAME AND KEYCLUE LISTS

        active_step = grandgame.get_active_step(ctx.message.author.id)
        active_substep = grandgame.get_active_substep(ctx.message.author.id)
        logging.info("{} Requested last game clue | Their active step is {} and active substep is {}".format(ctx.message.author.name, active_step, active_substep))

        #If substep > 1, they left off partway through a hidden key. Let them know that they left off on that key and what step
        if active_substep>1:
            keyname = hiddenkeys[active_step]
            await ctx.message.author.send("You left off on step {0} of key `{1}`. Enter `{1}` into any ST channel to resume where you left off.".format(active_substep, keyname))
        #Otherwise, things are ambiguous (they could have already figured out the new key and tried it and failed, or just gotten the hint for the new key)
        #Be conservative, and only tell them the name of the last key they completed, and the hint for the current key
        else:
            keyname = hiddenkeys[active_step-1]
            keyclue = hiddenkeyclues[active_step-1]
            await ctx.message.author.send("The last game step you completed was `{0}`. \nHere was the clue for the next unearned $hiddenkey: ```{1}```".format(keyname,keyclue))



    @commands.command(hidden=True, aliases=['key_gilded_hollow'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @commands.check(turtlecheck.if_joined_active_game)
    @commands.cooldown(1,120,commands.BucketType.user)
    async def key_gildedhollow(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='key_gildedhollow'
        step_number = 1
        substeps=1
        cooldown=2
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'The next hidden key is the title for core members of Siege Turtles (both in discord, and in game).'

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings)

    @commands.command(hidden=True, aliases=['key_seaguards'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(2)
    @commands.cooldown(1,120,commands.BucketType.user)
    async def key_seaguard(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='key_seaguard'
        step_number = 2
        substeps=1
        cooldown=2
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        start_card_settings.description = False

        step_1_settings = game_class.Text_Card_Settings(ctx, gamename, keyname, step_number, 1, substeps, cooldown, timer, description)
        step_1_settings.clue_text='Listen to the audio file provided below. To earn this key, respond within this message with the name of the song.'
        step_1_settings.correct_answer_text=[('exact','Fear not this night')]
        step_1_settings.file_attachments=['audio/FearNotThisNight.mp3']

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'The song "Fear not this Night" is played at a key point of the original GW2 story, where you cleanse corruption in this region of the game. Your next hidden key is $key_thenameofthisregion.'

        question_cards_settings = [step_1_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True, aliases=['key_ruinsoforr','key_ruins_of_orr','key_ruins_orr','key_ruinsorr'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @commands.cooldown(1,120,commands.BucketType.user)
    @turtlecheck.has_unlocked_hidden_key(3)
    async def key_orr(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='key_orr'
        step_number = 3
        substeps=1
        cooldown=2
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        start_card_settings.description = False

        step_1_settings = game_class.Choose_One_Card_Settings(ctx, gamename, keyname, step_number, 1, substeps, cooldown, timer, description)
        step_1_settings.clue_text='Which of the following is not a zone in Orr?'
        step_1_settings.emoji_answer_key_text = ['Straits of Devastation','Malchor\'s Leap','Fireheart Rise','Cursed Shore']
        step_1_settings.emoji = ['\U0001F1F8','\U0001F1F2','\U0001F1EB','\U0001F1E8']
        step_1_settings.correct_item_in_list = 3
        step_1_settings.icon_key_per_line = 2
        step_1_settings.timer=5

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'Trophys and trinkets exist galore in GW2. Of the top tier trophies, which one might be most sacred to a turtle? Your next hidden key is $key_thenameofthisT6material.'

        question_cards_settings = [step_1_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True, aliases=['key_armoredscales','key_armored_scale','key_armored_scales'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(4)
    @commands.cooldown(1,120,commands.BucketType.user)
    async def key_armoredscale(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='key_armoredscale'
        step_number = 4
        substeps=1
        cooldown=2
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        start_card_settings.description = False

        step_1_settings = game_class.Combination_Card_Settings(ctx, gamename, keyname, step_number, 1, substeps, cooldown, timer, description)
        step_1_settings.clue_text='Rank the following scales in ascending tier order, from lowest tier to highest.'
        step_1_settings.icon_key_per_line = 2

        emoji_smallscale = discord.utils.get(ctx.author.guild.emojis, name='smallscale_icon')
        emoji_scale = discord.utils.get(ctx.author.guild.emojis, name='scale_icon')
        emoji_largescale = discord.utils.get(ctx.author.guild.emojis, name='largescale_icon')
        emoji_armoredscale = discord.utils.get(ctx.author.guild.emojis, name='armoredscale_icon')

        step_1_settings.emoji_answer_key_text = ['Armored Scale','Scale','Small Scale','Large Scale']
        step_1_settings.emoji = [emoji_armoredscale, emoji_scale, emoji_smallscale, emoji_largescale]
        step_1_settings.correct_combination= [3,2,4,1]
        step_1_settings.timer=1

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'There are absolutely no culinary applications for the magical substance that constitutes the next hidden key. Your next key is $key_nameofthisrubypowderhere.'

        question_cards_settings = [step_1_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True, aliases=['key_bloodstone_dust', 'key_bloodstone'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(5)
    @commands.cooldown(1,120,commands.BucketType.user)
    async def key_bloodstonedust(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='key_bloodstonedust'
        step_number = 5
        substeps=1
        cooldown=2
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        start_card_settings.description = False

        step_1_settings = game_class.Get_In_Game_Card_Settings(ctx, gamename, keyname, step_number, 1, substeps, cooldown, timer, description)
        step_1_settings.clue_text='You\'d think ore with the same name as that responsible for the partial destruction of Tyria would be valuable, but turns out it\'s complete garbage. Still, go ahead and make sure you have 100 of the stuff. You never know...'
        step_1_settings.item_id=46733
        step_1_settings.required_amount=100

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'Strangely enough, this iconic city was not destroyed by a dragon per-say, but rather through the work of a Sylvari. A destruction salad appetizer if you will. Your next hidden key: $key_thenameofthiscity.'

        question_cards_settings = [step_1_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True, aliases=['key_lions_arch','key_la','key_lionarch'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(6)
    @commands.cooldown(1,120,commands.BucketType.user)
    async def key_lionsarch(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='key_lionsarch'
        step_number = 6
        substeps=3
        cooldown=2
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        start_card_settings.description = False

        step_1_settings = game_class.Choose_One_Card_Settings(ctx, gamename, keyname, step_number, 1, substeps, cooldown, timer, description)
        step_1_settings.clue_text='Looking at map of LA from a griffon\'s vantage point, what animal is **not** represented (but absolutely should be)?'
        step_1_settings.emoji_answer_key_text = ['Starfish','Lobster','Turtle']

        emoji_starfish = discord.utils.get(ctx.author.guild.emojis, name='starfish')
        emoji_lobster = discord.utils.get(ctx.author.guild.emojis, name='lobster')

        step_1_settings.emoji = [emoji_starfish,emoji_lobster,'\U0001F422']
        step_1_settings.correct_item_in_list = 3
        step_1_settings.icon_key_per_line = 3
        step_1_settings.timer=5

        step_2_settings = game_class.Text_Card_Settings(ctx, gamename, keyname, step_number, 2, substeps, cooldown, timer, description)
        step_2_settings.clue_text='What is the name of the point of interest closest to the pictured location?'
        step_2_settings.correct_answer_text=[('keyword','Deverol Garden')]
        step_2_settings.image_url = 'https://cdn.discordapp.com/attachments/471547983859679232/488059499928748102/LA_Unknown_POI.png'

        step_3_settings = game_class.Get_In_Game_Card_Settings(ctx, gamename, keyname, step_number, 3, substeps, cooldown, timer, description)
        step_3_settings.clue_text='After stepping foot out of the port city you find an orchard. A vendor who would be fitting as a librarian offers tools to help decore. Don\'t skimp.'
        step_3_settings.item_id=23794
        step_3_settings.required_amount=1

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'The game is done.'

        question_cards_settings = [step_1_settings, step_2_settings, step_3_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)


def setup(bot):
    bot.add_cog(TutorialGameControls(bot))



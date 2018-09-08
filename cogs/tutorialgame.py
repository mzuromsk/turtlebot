import discord
import asyncio
import datetime
import turtlecheck
import cogs.grandturtlegame as grandgame
import grandturtlegame_question_classes as game_class
from discord.ext import commands
import turtle_credentials as tc
from discord import NotFound


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
        num_days = 0
        num_hours = 0.5
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
        join_settings.link_attachments = [('Game Guide','https://tinyurl.com/ST-Game-Guide'),('Cypher Tools','http://rumkin.com/tools/cipher/'),('Guild Wars 2 Wiki','http://wiki.guildwars2.com')]
        join_settings.clue_text = '```Your first hidden key is the first private instance to house ST in GW2. Such were golden times.``` ```Remember, the actual hidden key must be entered in the form $game_youranswerhere. \nYou must enter your guess for the hidden key in a ST text channel (not a private message). \nThis is required for the bot to recognize your command correctly and also to remove your hidden key from prying eyes.```'
        await self.GameControls.add_turtle_to_game(ctx,join_settings)

    @commands.command(hidden=True, aliases=['game_gilded_hollow'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @commands.check(turtlecheck.if_joined_active_game)
    @commands.cooldown(1,120,commands.BucketType.user)
    async def game_gildedhollow(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='game_gildedhollow'
        step_number = 1
        substeps=1
        cooldown=2
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'The next hidden key is the title for core members of Siege Turtles (both in discord, and in game).'

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings)

    @commands.command(hidden=True, aliases=['game_seaguards'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(2)
    @commands.cooldown(1,120,commands.BucketType.user)
    async def game_seaguard(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='game_seaguard'
        step_number = 2
        substeps=1
        cooldown=2
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        start_card_settings.description = False

        step_1_settings = game_class.Text_Card_Settings(ctx, gamename, keyname, step_number, 1, substeps, cooldown, timer, description)
        step_1_settings.clue_text='Listen to the audio file provided below. Respond below with the name of this song. Following the input instructions above, make sure you check your spelling.'
        step_1_settings.correct_answer_text=[('exact','Fear not this night')]
        step_1_settings.file_attachments=['audio/FearNotThisNight.mp3']

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'The song "Fear not this Night" is played at a key point of the original GW2 story, where you cleanse corruption in this region of the game. Your next hidden key is $game_thenameofthisregion.'

        question_cards_settings = [step_1_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True, aliases=['game_ruinsoforr','game_ruins_of_orr','game_ruins_orr','game_ruinsorr'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @commands.cooldown(1,120,commands.BucketType.user)
    @turtlecheck.has_unlocked_hidden_key(3)
    async def game_orr(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='game_orr'
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
        earned_key_card_settings.clue_text = 'Trophys and trinkets exist galore in GW2. Of the top tier trophies, which one might be most sacred to a turtle? Your next hidden key is $game_thenameofthisT6material.'

        question_cards_settings = [step_1_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True, aliases=['game_armoredscales','game_armored_scale','game_armored_scales'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(4)
    @commands.cooldown(1,120,commands.BucketType.user)
    async def game_armoredscale(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='game_armoredscale'
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
        earned_key_card_settings.clue_text = 'There are absolutely no culinary applications for the magical substance that constitutes the next hidden key. Your next key is $game_nameofthisrubypowderhere.'

        question_cards_settings = [step_1_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True, aliases=['game_bloodstone_dust', 'game_bloodstone'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(5)
    @commands.cooldown(1,120,commands.BucketType.user)
    async def game_bloodstonedust(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='game_bloodstonedust'
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
        earned_key_card_settings.clue_text = 'Strangely enough, this iconic city was not destroyed by a dragon per-say, but rather through the work of a Sylvari. A destruction salad appetizer if you will. Your next hidden key: $game_thenameofthiscity.'

        question_cards_settings = [step_1_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True, aliases=['game_lions_arch','game_la','game_lionarch'])
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(6)
    @commands.cooldown(1,120,commands.BucketType.user)
    async def game_lionsarch(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Tutorial'
        keyname='game_lionsarch'
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



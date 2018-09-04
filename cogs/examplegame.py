import discord
import asyncio
import datetime
import turtlecheck
import cogs.grandturtlegame as grandgame
import grandturtlegame_question_classes as game_class
from discord.ext import commands
import turtle_credentials as tc
from discord import NotFound


class ExampleGrandGameControls:
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
        game_steps = [1,4,1,1,2,1,1]
        game_name = "Tutorial"
        num_days = 0
        num_hours = 1
        await self.GameControls.start_the_game(ctx, game_name, game_steps, num_days, num_hours)

    @commands.command(brief="Join the current [ST] Grand Game.", description="Join and start a currently running Grand Game. Note: If you have already started the current game, this command will completely reset your progress. Must be a Seaguard to participate.")
    @commands.check(turtlecheck.if_seaguard )
    async def game_join(self, ctx):
        gamename = 'Tutorial'
        steps = 5
        api_key_required = True

        join_settings = game_class.Join_Card_Settings(ctx, gamename,steps, api_key_required)
        join_settings.prize_list=["Learning How To Play"]
        join_settings.image_url='https://cdn.discordapp.com/attachments/471547983859679232/486011052161499136/Tutorial.png'
        join_settings.link_attachments = [('Game Guide','https://tinyurl.com/ST-Game-Guide'),('Cypher Tools','http://rumkin.com/tools/cipher/'),('Guild Wars 2 Wiki','http://wiki.guildwars2.com')]
        join_settings.clue_text = '```Your first hidden key is the first private instance to house ST in GW2. Such were golden times.``````Remember: Your answer must be entered in a ST Discord text channel in the form $game_youranswerhere```'
        await self.GameControls.add_turtle_to_game(ctx,join_settings)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @commands.check(turtlecheck.if_active_game)
    async def game_testkey1(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Test Season'
        keyname='game_testkey1'
        step_number = 1
        substeps=1
        cooldown=5
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'The next key is $game_testkey2.'

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(2)
    async def game_testkey2(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Test Season'
        keyname='game_testkey2'
        step_number = 2
        substeps=4
        cooldown=5
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)

        step_1_settings = game_class.Choose_One_Card_Settings(ctx, gamename, keyname, step_number, 1, substeps, cooldown, timer, description)
        step_1_settings.clue_text='Take a load off and wander through the gardens of the Central Plaza. Some might say the Gods themselves tend to the garden, but which of the gods “fought the hardest and rightfully earned their spot among the six” (More of a Joke about GW: Nightfall)'
        step_1_settings.emoji_answer_key_text = ['Dwayna','Melandru','Kormir','Lyssa','Grenth','Balthazar']
        step_1_settings.emoji = ['\U0001F1E9','\U0001F1F2','\U0001F1F0','\U0001F1F1','\U0001F1EC','\U0001F1E7']
        step_1_settings.correct_item_in_list = 3
        step_1_settings.timer=5

        step_2_settings = game_class.Combination_Card_Settings(ctx, gamename, keyname, step_number, 2, substeps, cooldown, timer, description)
        step_2_settings.clue_text='In order of descending cleave.'
        step_2_settings.icon_key_per_line = 2

        emoji_guard = discord.utils.get(ctx.author.guild.emojis, name='Guardian_icon')
        emoji_thief = discord.utils.get(ctx.author.guild.emojis, name='Thief_icon')

        step_2_settings.emoji_answer_key_text = ['Guardian','Thief','Fire Elementalist','Water Elementalist']
        step_2_settings.emoji = [emoji_guard,emoji_thief,'\U0001F525','\U0001F4A7']
        step_2_settings.correct_combination= [3,1,2,4]
        step_2_settings.timer=1

        step_3_settings = game_class.Text_Card_Settings(ctx, gamename, keyname, step_number, 3, substeps, cooldown, timer, description)
        step_3_settings.clue_text='Exploring near Uzolan’s Mechanical Orchestra you\'ll find yourself wondering \"how do you walk on these stones all day long?\"'
        step_3_settings.correct_answer_text=[('exact','You get used to it.'),('keyword','used')]

        step_4_settings = game_class.Get_In_Game_Card_Settings(ctx, gamename, keyname, step_number, 4, substeps, cooldown, timer, description)
        step_4_settings.clue_text='You\'d think ore associated with the creatures responsible for the partial destruction of Tyria would be valuable, but turns out it is complete garbage. Still, go ahead and make sure you have 500 of the stuff.'
        #step_4_settings.item_id=23794
        step_4_settings.item_id=46733
        step_4_settings.required_amount=500

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'The next one is $game_testkey3.'

        question_cards_settings = [step_1_settings, step_2_settings,step_3_settings, step_4_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(3)
    async def game_testkey3(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Test Season'
        keyname='game_testkey3'
        step_number = 3
        substeps=1
        cooldown=5
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)

        step_1_settings = game_class.Choose_One_Card_Settings(ctx, gamename, keyname, step_number, 1, substeps, cooldown, timer, description)
        step_1_settings.clue_text='Take a load off and wander through the gardens of the Central Plaza. Some might say the Gods themselves tend to the garden, but which of the gods “fought the hardest and rightfully earned their spot among the six” (More of a Joke about GW: Nightfall)'
        step_1_settings.emoji_answer_key_text = ['Dwayna','Melandru','Kormir','Lyssa','Grenth','Balthazar']
        step_1_settings.emoji = ['\U0001F1E9','\U0001F1F2','\U0001F1F0','\U0001F1F1','\U0001F1EC','\U0001F1E7']
        step_1_settings.correct_item_in_list = 3
        step_1_settings.timer=5

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'The next one is $game_testkey4.'

        question_cards_settings = [step_1_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(4)
    async def game_testkey4(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Test Season'
        keyname='game_testkey4'
        step_number = 4
        substeps=1
        cooldown=5
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)


        step_2_settings = game_class.Combination_Card_Settings(ctx, gamename, keyname, step_number, 1, substeps, cooldown, timer, description)
        step_2_settings.clue_text='In order of descending cleave.'
        step_2_settings.icon_key_per_line = 2

        emoji_guard = discord.utils.get(ctx.author.guild.emojis, name='Guardian_icon')
        emoji_thief = discord.utils.get(ctx.author.guild.emojis, name='Thief_icon')

        step_2_settings.emoji_answer_key_text = ['Guardian','Thief','Fire Elementalist','Water Elementalist']
        step_2_settings.emoji = [emoji_guard,emoji_thief,'\U0001F525','\U0001F4A7']
        step_2_settings.correct_combination= [3,1,2,4]
        step_2_settings.timer=1

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'The next one is $game_testkey5.'

        question_cards_settings = [step_2_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(5)
    async def game_testkey5(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Test Season'
        keyname='game_testkey5'
        step_number = 5
        substeps=2
        cooldown=5
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)

        step_3_settings = game_class.Text_Card_Settings(ctx, gamename, keyname, step_number, 1, substeps, cooldown, timer, description)
        step_3_settings.clue_text='Who is the current leader of ST in GW2?'
        step_3_settings.correct_answer_text=[('keyword','River')]

        step_4_settings = game_class.Get_In_Game_Card_Settings(ctx, gamename, keyname, step_number, 2, substeps, cooldown, timer, description)
        step_4_settings.clue_text='After stepping foot out of the port city you find an orchard. A vendor who would be fitting as a librarian offers tools to help decore. Don\'t skimp.'
        #step_4_settings.item_id=23794
        step_4_settings.item_id=23794
        step_4_settings.required_amount=1

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'The next key is $game_testkey6.'

        question_cards_settings = [step_3_settings, step_4_settings]

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings, start_card_settings, question_cards_settings)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(6)
    async def game_testkey6(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Test Season'
        keyname='game_testkey6'
        step_number = 6
        substeps=1
        cooldown=5
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'The next key is $game_testkey7.'

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings)

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    @commands.check(turtlecheck.if_api_key)
    @turtlecheck.has_unlocked_hidden_key(7)
    async def game_testkey7(self, ctx, description=True):
        try:
            await ctx.message.delete()
        except:
            pass

        #Set overall hidden key paramaters
        gamename ='Test Season'
        keyname='game_testkey7'
        step_number = 7
        substeps=1
        cooldown=5
        timer=5

        start_card_settings = game_class.Start_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)

        earned_key_card_settings = game_class.Earned_Key_Card_Settings(ctx, gamename, keyname, step_number, substeps, cooldown, timer)
        earned_key_card_settings.clue_text = 'This is the final one. This would send a celebration card when it\'s done.'

        await self.GameControls.run_hidden_key(ctx, earned_key_card_settings)

def setup(bot):
    bot.add_cog(ExampleGrandGameControls(bot))



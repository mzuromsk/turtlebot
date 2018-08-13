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
    async def game_example_send_picture_clue(self, ctx):

        await ctx.message.delete()
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
            else:
                print(str(ans.content).lower())
                print(correct_answer.lower())
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

        await ctx.message.delete()
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

def setup(bot):
    bot.add_cog(GrandTurtleGameControls(bot))
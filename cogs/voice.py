import discord
import asyncio
import turtlecheck
import random

from discord.ext import commands

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus()


class VoiceControls:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    @commands.command(description="Plays a brief song. Go ahead and blame Jaz for this song; but seriously, why die? [Note: User must be in a voice channel to summon the bot.]", brief="Plays a brief motivational song.")
    @commands.check(turtlecheck.if_seaguard)
    async def ydie(self, ctx):
        if ctx.message.author.voice is not None:
            try:
                self.vc = await ctx.message.author.voice.channel.connect()
            except:
                await self.vc.move_to(ctx.message.author.voice.channel)

            await ctx.message.delete()
            self.vc.play(discord.FFmpegPCMAudio('audio/YDie.mp3'))
            await asyncio.sleep(17)
            await self.vc.disconnect()

    @commands.command(description="Plays a brief track. For when things go bad. [Note: User must be in a voice channel to summon the bot.]", brief="Plays a brief track. Break glass when things go bad.")
    @commands.check(turtlecheck.if_seaguard)
    async def nogodpleaseno(self, ctx):
        if ctx.message.author.voice is not None:
            try:
                self.vc = await ctx.message.author.voice.channel.connect()
            except:
                await self.vc.move_to(ctx.message.author.voice.channel)

            await ctx.message.delete()
            self.vc.play(discord.FFmpegPCMAudio('audio/nogodpleaseno.mp3'))
            await asyncio.sleep(13)
            await self.vc.disconnect()

    @commands.command(description="Plays the Dhuum monologue. [Note: User must be in a voice channel to summon the bot.]", brief="Plays the Dhuum monologue.")
    @commands.check(turtlecheck.if_seaguard)
    async def dhuumspeaks(self, ctx):
        if ctx.message.author.voice is not None:
            try:
                self.vc = await ctx.message.author.voice.channel.connect()
            except:
                await self.vc.move_to(ctx.message.author.voice.channel)

            await ctx.message.delete()
            self.vc.play(discord.FFmpegPCMAudio('audio/DhuumVoiceover.mp3'))
            await asyncio.sleep(19)
            await self.vc.disconnect()

    @commands.command(hidden=True, description="Plays the Dhuum monologue. [Note: User must be in a voice channel to summon the bot.]", brief="Plays the Dhuum monologue.")
    @commands.check(turtlecheck.if_seaguard)
    async def dhuumspeaksfrench(self, ctx):
        if ctx.message.author.voice is not None:
            try:
                self.vc = await ctx.message.author.voice.channel.connect()
            except:
                await self.vc.move_to(ctx.message.author.voice.channel)

            await ctx.message.delete()
            self.vc.play(discord.FFmpegPCMAudio('audio/DhuumVoiceoverFrench.mp3'))
            await asyncio.sleep(20)
            await self.vc.disconnect()


    @commands.command(description="Plays the Dhuum monologue. For when a quiet God of the UW will just not do. [Note: User must be in a voice channel to summon the bot.]", brief="Plays the Dhuum monologue LOUDLY.")
    @commands.check(turtlecheck.if_seaguard)
    async def dhuumspeaksloudly(self, ctx):
        if ctx.message.author.voice is not None:
            try:
                self.vc = await ctx.message.author.voice.channel.connect()
            except:
                await self.vc.move_to(ctx.message.author.voice.channel)

            await ctx.message.delete()
            self.vc.play(discord.FFmpegPCMAudio('audio/DhuumVoiceoverLoud.mp3'))
            await asyncio.sleep(19)
            await self.vc.disconnect()

    @commands.command(description="Plays Lyanna's mantra, as performed by dear leader. [Note: User must be in a voice channel to summon the bot.]", brief="Plays Lyanna's mantra, as performed by dear leader.")
    @commands.check(turtlecheck.if_seaguard)
    async def nahnahnahnah(self, ctx):
        if ctx.message.author.voice is not None:
            try:
                self.vc = await ctx.message.author.voice.channel.connect()
            except:
                await self.vc.move_to(ctx.message.author.voice.channel)

            await ctx.message.delete()
            self.vc.play(discord.FFmpegPCMAudio('audio/riversingsnahnah.mp3'))
            await asyncio.sleep(17)
            await self.vc.disconnect()


    @commands.command(description="Starts a text and vocal food timer. The timer defaults to 30 minutes. The command accepts arguments for the length of time before reminder and how many repetitions as follows: startfoodtimer [time in minutes] [# of reminders]. Defaults to 30 minutes and 4 reminders. [Note: User must be in a voice channel to summon the bot.]", brief="Starts a food timer. Defaults to reminders for 30 minute food.")
    @commands.check(turtlecheck.if_seaguard)
    async def startfoodtimer(self, ctx, timerlength=30, limit=4):
        count = 0
        if ctx.message.author.voice is not None:
            starting_channel = ctx.message.author.voice.channel.name
            print(starting_channel)
            self.keepLooping = True
        else:
            await ctx.send("Join a voice channel to use this command.")
            return

        while self.keepLooping and count < limit:
            if ctx.message.author.voice is not None:
                try:
                    self.vc = await ctx.message.author.voice.channel.connect()
                except:
                    await self.vc.move_to(ctx.message.author.voice.channel)

            try:
                await ctx.send("  Eat your {2} min food & utility!   |  {0}\'s Reminder #{3} of {4}  | Started in channel {1}".format(ctx.message.author.name, starting_channel, timerlength, count+1, limit))
                rnum = random.randint(0,2)
                if rnum<2:
                    self.vc.play(discord.FFmpegPCMAudio('audio/EatFoodBritishLady.mp3'))
                else:
                    self.vc.play(discord.FFmpegPCMAudio('audio/EatFoodBritishGent.mp3'))

                count = count + 1
                await asyncio.sleep(timerlength*60)
                print("{0}\'s Reminder #{2} of {3} | Started in channel {1}".format(ctx.message.author.name, starting_channel, count, limit))


            except:
                await ctx.send("Enter the time in minutes")
                self.keepLooping = False

    @commands.command(description="Turns off all currently running food timers and disconnects the bot from the audio channel.", brief="Turns off all currently running food timers.")
    @commands.check(turtlecheck.if_seaguard)
    async def endfoodtimers(self, ctx):
        self.keepLooping = False
        try:
            await self.vc.disconnect()
        except:
            print('Was not in a voice channel anyways.')

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def pingvoice(self, ctx):
        await ctx.send('Pong!')


def setup(bot):
    bot.add_cog(VoiceControls(bot))

import discord
import asyncio
import random

from discord.ext import commands

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus()


class Control:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    @commands.command()
    async def ydie(self, ctx):
        if ctx.message.author.voice is not None:
            try:
                self.vc = await ctx.message.author.voice.channel.connect()
            except:
                await self.vc.move_to(ctx.message.author.voice.channel)

            await ctx.message.delete()
            self.vc.play(discord.FFmpegPCMAudio('YDie.mp3'), after=lambda e: print('done', e))
            await asyncio.sleep(17)
            await self.vc.disconnect()

    @commands.command()
    async def nogodpleaseno(self, ctx):
        if ctx.message.author.voice is not None:
            try:
                self.vc = await ctx.message.author.voice.channel.connect()
            except:
                await self.vc.move_to(ctx.message.author.voice.channel)

            await ctx.message.delete()
            self.vc.play(discord.FFmpegPCMAudio('nogodpleaseno.mp3'), after=lambda e: print('done', e))
            await asyncio.sleep(19)
            await self.vc.disconnect()

    @commands.command()
    async def dhuumspeaks(self, ctx):
        if ctx.message.author.voice is not None:
            try:
                self.vc = await ctx.message.author.voice.channel.connect()
            except:
                await self.vc.move_to(ctx.message.author.voice.channel)

            await ctx.message.delete()
            self.vc.play(discord.FFmpegPCMAudio('DhuumVoiceover.mp3'), after=lambda e: print('done', e))
            await asyncio.sleep(19)
            await self.vc.disconnect()

    @commands.command()
    async def dhuumspeaksloudly(self, ctx):
        if ctx.message.author.voice is not None:
            try:
                self.vc = await ctx.message.author.voice.channel.connect()
            except:
                await self.vc.move_to(ctx.message.author.voice.channel)

            await ctx.message.delete()
            self.vc.play(discord.FFmpegPCMAudio('DhuumVoiceoverLoud.mp3'), after=lambda e: print('done', e))
            await asyncio.sleep(19)
            await self.vc.disconnect()

    @commands.command()
    async def nahnahnahnah(self, ctx):
        if ctx.message.author.voice is not None:
            try:
                self.vc = await ctx.message.author.voice.channel.connect()
            except:
                await self.vc.move_to(ctx.message.author.voice.channel)

            await ctx.message.delete()
            self.vc.play(discord.FFmpegPCMAudio('riversingsnahnahnahbackupvocals.mp3'), after=lambda e: print('done', e))
            await asyncio.sleep(19)
            await self.vc.disconnect()


    @commands.command()
    async def startfoodtimer(self, ctx, timerlength=30, limit=5):
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
                    self.vc.play(discord.FFmpegPCMAudio('EatFoodBritishLady.mp3'), after=lambda e: print('done', e))
                else:
                    self.vc.play(discord.FFmpegPCMAudio('EatFoodBritishGent.mp3'), after=lambda e: print('done', e))

                count = count + 1
                await asyncio.sleep(timerlength*60)
                print("{0}\'s Reminder #{2} of {3} | Started in channel {1}".format(ctx.message.author.name, starting_channel, count, limit))


            except:
                await ctx.send("Enter the time in minutes")
                self.keepLooping = False

    @commands.command()
    async def endfoodtimers(self, ctx):
        self.keepLooping = False
        try:
            await self.vc.disconnect()
        except:
            print('Was not in a voice channel anyways.')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')


def setup(bot):
    bot.add_cog(Control(bot))

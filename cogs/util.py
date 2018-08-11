import discord
import asyncio
<<<<<<< HEAD
import turtle_credentials as tc
=======
import turtlecheck

>>>>>>> renay/audio_branch
from discord.ext import commands

class UtilityControls:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def pingutility(self, ctx):
        await ctx.send('Pong!')

<<<<<<< HEAD
    @commands.command()
    async def get_roster(self, ctx):
        #TODO:  MAKE THIS WORK WHEN THE ROSTER ISN'T BLANK
        for guild in self.bot.guilds:
            if guild.name == 'Siege Turtles':
                   print('starting ST')
                   for member in guild.members:                       
                        roles = member.roles
                        is_seaguard = False
                        for role in roles:
                            if role.id == 189573500535701504:
                                is_seaguard = True
                        if is_seaguard:
                            print('found seaguard: ' + member.name)
                            turtle = []
                            turtle.append(member.id)
                            turtle.append(member.name)
                            nickname = member.nick
                            if nickname is None:
                                nickname = 'No nickname'
                            turtle.append(nickname)
                            turtle.append(member.discriminator)
                            turtle.append(member.roles)
                            print('checking if exists: ' + member.name)
                            if check_if_turtle_exists(turtle[0]):
                                print('found ' + member.name)#code goes here to update existing turtle
                            else:
                                print('now creating ' + str(turtle[1]))
                                sqlStr = "INSERT INTO turtle.turtles (discord_id, name, nickname, discriminator) VALUES (" + \
                                            str(turtle[0]) + ", '" + turtle[1] + "', '" + turtle[2] + "', '" + turtle[3] + "')"
                                try:
                                    conn
                                except NameError:
                                    conn = tc.get_conn()
                                cur = conn.cursor()
                                cur.execute(sqlStr)
                                conn.commit()
                                print('now adding roles for ' + str(turtle[1]))
                                add_all_roles(turtle[0], turtle[4], conn, cur)
                                print('completed ' + str(turtle[1]))
                                await ctx.send('Finished creating record and roles for: ' + turtle[1])
                                
                                
=======
    @commands.command(description="This shuts down the bot process. Contact a bot administrator [Rev, Renay] if you need the bot shutdown.", brief="Shut down turtlebot. Requires bot administrator privileges.")
    @commands.check(turtlecheck.if_admin)
    async def shutdown(self, ctx):
        await ctx.message.delete()
        await self.bot.logout()
        await self.bot.close()

>>>>>>> renay/audio_branch

def setup(bot):
    bot.add_cog(UtilityControls(bot))

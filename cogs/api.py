import discord
import asyncio
import turtlecheck
from discord.ext import commands
import psycopg2
import turtle_credentials as tc
from collections import OrderedDict
from .exceptions import (APIError, APIBadRequest, APIConnectionError, APIForbidden, APIInactiveError, APIInvalidKey, APINotFound)

class ApiControls:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def pingapi(self, ctx):
        await ctx.send('Pong!')

    async def boss_embed(self, ctx, raids, results):
        def is_killed(boss):
            return "+✔" if boss["id"] in results else "-✖"

        def readable_id(_id):
            _id = _id.split("_")
            dont_capitalize = ("of", "the", "in")
            return " ".join([x.capitalize() if x not in dont_capitalize else x for x in _id])

        not_completed = []
        embed = discord.Embed(title="Bosses")
        for raid in raids:
            for wing in raid["wings"]:
                wing_done = True
                value = ["```diff"]
                for boss in wing["events"]:
                    if boss["id"] not in results:
                        wing_done = False
                        not_completed.append(boss)
                    value.append(is_killed(boss) + readable_id(boss["id"]))
                value.append("```")
                name = readable_id(wing["id"])
                if wing_done:
                    name += " :white_check_mark:"
                else:
                    name += " :x:"
                embed.add_field(name=name, value="\n".join(value))
        if len(not_completed) == 0:
            description = "Everything completed this week :star:"
        else:
            bosses = list(filter(lambda b: b["type"] == "Boss", not_completed))
            events = list(
                filter(lambda b: b["type"] == "Checkpoint", not_completed))
            if bosses:
                suffix = ""
                if len(bosses) > 1:
                    suffix = "es"
                bosses = "{} boss{}".format(len(bosses), suffix)
            if events:
                suffix = ""
                if len(events) > 1:
                    suffix = "s"
                events = "{} event{}".format(len(events), suffix)
            description = (", ".join(filter(None, [bosses, events])) +
                           " not completed this week")
        embed.description = description
        embed.set_footer(text="Green (+) means completed this week. Red (-) "
                         "means not")
        return embed

    @commands.command(hidden=True)
    @commands.check(turtlecheck.if_seaguard)
    async def raid_bosses(self,ctx):

        raids = []
        #TODO: Update this part to just pull the raids list from a cache in the database rather than fetching it again everytime
        raids_index = await self.call_api("raids")
        for raid in raids_index:
            raids.append(await self.call_api("raids/" + raid))

        endpoint = "account/raids"
        try:
            api_key = get_api_key(ctx.author.id)
            results = await self.call_api(endpoint, key=api_key)
        except APIError as e:
            return await self.bot.error_handler(ctx, e)

        embed = await self.boss_embed(ctx, raids, results)
        embed.set_author(name=ctx.author.name)
        await ctx.send("{.mention}, here are your raid bosses:".format(ctx.author), embed=embed)

    async def call_multiple(self, endpoints, key=None):
        res = []
        for e in endpoints:
            res.append(await self.call_api(e, key=key))
        return res
        print(res)

    async def call_api(self, endpoint, key=None):
        headers = {
            'User-Agent': "Turtlebot - a Discord bot",
            'Accept': 'application/json'
        }
        if key:
            headers.update({"Authorization": "Bearer " + key})
        apiserv = 'https://api.guildwars2.com/v2/'
        url = apiserv + endpoint
        async with self.bot.session.get(url, headers=headers) as r:
            if r.status != 200 and r.status != 206:
                try:
                    err = await r.json()
                    err_msg = err["text"]
                except:
                    err_msg = ""
                if r.status == 400:
                    if err_msg == "invalid key":
                        raise APIInvalidKey("Invalid key")
                    raise APIBadRequest("Bad request")
                if r.status == 404:
                    raise APINotFound("Not found")
                if r.status == 403:
                    if err_msg == "invalid key":
                        raise APIInvalidKey("Invalid key")
                    raise APIForbidden("Access denied")
                if r.status == 503 and err_msg == "API not active":
                    raise APIInactiveError("API is dead")
                if r.status == 429:
                    self.log.error("API Call limit saturated")
                    raise APIConnectionError(
                        "Requests limit has been saturated. Try again later.")
                else:
                    raise APIConnectionError("{} {}".format(r.status, err_msg))
            return await r.json()

    async def simple_search(self, ctx, item_id):
        try:
            item_endpoint = "items/"+str(item_id)
            item_result = await self.call_api(item_endpoint)
        except:
            print("Error getting item")
        try:
            endpoints = [
                "account/bank", "account/inventory", "account/materials",
                "characters?page=0&page_size=200"
            ]
            results = await self.call_multiple(endpoints, key=get_api_key(ctx.message.author.id))
            storage_spaces = ("bank", "shared", "material storage")
            storage_spaces = OrderedDict(list(zip(storage_spaces, results)))
            characters = results[3]
        except:
            print("Error getting endpoints")
            return

        def get_amount_in_slot(item):

            if not item:
                return 0
            if item["id"]==item_id:
                if "count" not in item:
                    return 1
                return item["count"]
            return 0

        storage_counts = OrderedDict()
        for k, v in storage_spaces.items():
            count = 0
            for item in v:
                count += get_amount_in_slot(item)
            storage_counts[k] = count
        for character in characters:
            bag_count = 0
            for bag in character["bags"]:
                bag_count += get_amount_in_slot(bag)
            bags = [
                bag["inventory"] for bag in filter(None, character["bags"])
            ]
            bag_total = 0
            for bag in bags:
                for item in bag:
                    bag_total += get_amount_in_slot(item)
            equipment = 0
            for piece in character["equipment"]:
                equipment += get_amount_in_slot(piece)
            count = bag_total + equipment + bag_count
            storage_counts[character["name"]] = count
        seq = [k for k, v in storage_counts.items() if v]
        total = 0
        output = []
        if not seq:
            return total, output, item_result
        else:
            longest = len(max(seq, key=len))
            if longest < 8:
                longest = 8
            output = ["LOCATION{}COUNT".format(" " * (longest - 5)), "--------{}|-----".format("-" * (longest - 6))]
            storage_counts = OrderedDict(sorted(storage_counts.items(), key=lambda kv: kv[1], reverse=True))
            table_string = ''
            for k, v in storage_counts.items():
                if v:
                    total += v
                    output.append("{} {} | {}".format(k.upper(), " " * (longest - len(k)), v))
            output.append("--------{}------".format("-" * (longest - 10)))
            output.append("TOTAL:{}{}".format(" " * (longest - 2), total))

            return total, output, item_result


    @commands.command(description="After entering this command, the bot will direct message the user to request a GW2 API key. This key will be saved in a database and linked with the discord account. Future bot commands will query the GW2 API for your account.", brief = "Set a GW2 API key to be used for API discord commands.")
    @commands.check(turtlecheck.if_seaguard)
    async def set_api_key(self, ctx):
        await ctx.message.delete()
        out = 'Enter the `GW2 API key` that you wish to link with your discord account into the message below then send.\n```md\n# Notes: Your API key will be saved to an online database and linked to your discord account. You only need to update your API code if you would like to change permissions. \nOnly bot administers will have access to the database [Rev, Renay]. \n# You may choose to limit your permissions for your provided API key, but this may block some bot functionality.\nTo get a GW2 API Key, go here: https://account.arena.net/applications.```'
        try:
            message = await ctx.author.send(out)
        except discord.Forbidden:
            return await ctx.send('I do not have permission to DM you. Please enable this in the future.')

        def m_check(m):
            return m.author == ctx.author and m.channel == message.channel

        try:
            ans = await self.bot.wait_for('message', check=m_check, timeout=300.0)
        except asyncio.TimeoutError:
            await ctx.author.send('Sorry. You took to long to enter your key. If you would like to retry, re-enter the command in a text channel and the bot will re-message you.')
        else:
            api_key = ans.content
            discord_id = ctx.author.id
            if await self.check_valid_api_key(api_key):
                with ctx.author.dm_channel.typing():
                    checking_message = await ctx.author.send('Checking API key permissions...')
                    if await self.check_api_key_works(api_key):
                        try:
                            try:
                                conn
                            except NameError:
                                conn = tc.get_conn()
                            cur = conn.cursor()
                            #get the id of any existing key for this person
                            sqlStr = "SELECT id FROM turtle.api_keys WHERE discord_id = " + str(discord_id)
                            cur.execute(sqlStr)
                            result = cur.fetchall()
                            try:
                                to_be_deleted = result[0][0]
                                if to_be_deleted is None:
                                    to_be_deleted = -1
                            except:
                                to_be_deleted = -1
                            sqlStr = "INSERT INTO turtle.api_keys (discord_id, api_key) VALUES (" + str(discord_id) + ", '" + api_key + "');"
                            cur.execute(sqlStr)
                            conn.commit()
                            #now that we've successfully inserted, delete the previous key
                            if to_be_deleted != -1:
                                sqlStr = "DELETE FROM turtle.api_keys WHERE id = " + str(to_be_deleted)
                                print(sqlStr)
                                cur.execute(sqlStr)
                                conn.commit()
                            await ctx.author.send('You entered the following GW2 API key: `{0}` ```\nThis key has been succesfully linked to your discord username. If you would like to update it in the future, just re-run this command from any text channel.```'.format(ans.content))
                        except:
                           await ctx.author.send('Something went wrong.  Tell Rev, he wrote this part')
                    else:
                        await ctx.author.send('```The API key was not saved. Turtle-bot tested the API key and found that it did not have the required permissions. Make sure you allow at least [Account][Characters][Inventories][Progression] permissions when creating your API key.```')
            else:
                await ctx.author.send('```That API key looks like it is the wrong length, or something.  Questions? Ask Rev or Renay to take a look.```')

        await message.delete()

    @commands.command(description="After entering this command, the bot will direct message the user to confirm that you would like to delete your GW2 API key.", brief = "Delete your GW2 API key.")
    @commands.check(turtlecheck.if_seaguard)
    async def clear_api_key(self, ctx):
        await ctx.message.delete()
        out = 'Please confirm that you would like to delete your key (if you change your mind at a later date, you will have to re-set it). ```\nClick ✅ to confirm, ❌ to cancel```'
        try:
            message = await ctx.author.send(out)
            await message.add_reaction('✅')
            await message.add_reaction('❌')
        except discord.Forbidden:
            return await ctx.send('I do not have permission to DM you. Please enable this in the future.')

        def r_check(r, user):
            return user == ctx.author and r.count > 1

        try:
            ans, user = await self.bot.wait_for('reaction_add', check=r_check, timeout=300.0)
        except asyncio.TimeoutError:
            await ctx.author.send('Sorry. You took to long to select your choice. If you would like to retry, re-enter the command in a text channel and the bot will re-message you.')
        else:
            if str(ans.emoji) == '✅':
                sqlStr = "DELETE FROM turtle.api_keys WHERE discord_id = " + str(ctx.author.id)
                try:
                    conn
                except NameError:
                    conn = tc.get_conn()
                cur = conn.cursor()
                cur.execute(sqlStr)
                conn.commit()
                await ctx.author.send('Your GW2 API key has been deleted.')
            if str(ans.emoji) == '❌':
                await ctx.author.send('Your GW2 API key has been preserved...for now.')
        await message.delete()

    async def check_valid_api_key(self, key):
        try:
            return len(key) == 72
        except:
            return False
        return False

    async def check_api_key_works(self,key):
        try:
            endpoints = ["account/bank", "account/inventory", "account/materials", "characters?page=0&page_size=200","account/raids"]
            results = await self.call_multiple(endpoints, key=key)
            return True
        except:
            return False


def get_api_key(discord_id):
    try:
        sqlStr = "SELECT api_key FROM turtle.api_keys WHERE discord_id = "  + str(discord_id)
        try:
            conn
        except NameError:
            conn = tc.get_conn()
        cur = conn.cursor()
        cur.execute(sqlStr)
        result = cur.fetchall()
        try:
            return result[0][0]
        except:
            return None
    except:
        return None

def setup(bot):
    bot.add_cog(ApiControls(bot))




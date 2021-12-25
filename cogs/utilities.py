import discord
import platform
import random
import requests
from discord.ext import commands

# Local imports
from utils.util import Pag

class MemberRoles(commands.Converter):
    async def convert(self, ctx, argument):
        member = await super().convert(ctx, argument)
        return [role.name for role in member.roles[1:]]

class utilities(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.colors = random.choice(self.client.color_list)

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Commands
    @commands.command(description="Show ping of the bot", aliases=['latency'])
    async def ping(self, ctx):
        embed = discord.Embed(title="Pong!", description=f"{round(self.client.latency * 1000)} ms",
                            thumbnail=ctx.bot.user.avatar_url, color=self.colors, timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)

    @commands.command(description="Ways to support me", aliases=['vote', 'invite', 'beansfight'])
    async def support(self, ctx):
        embed = discord.Embed(title="Support Me!!", description="Thank you for everyone who supported!",
                            color=self.colors, timestamp=ctx.message.created_at)
        embed.add_field(name="Invite", value="[Click Here](https://discord.com/api/oauth2/authorize?client_id=840647743654723614&permissions=8&scope=bot)")
        embed.add_field(name="Vote", value="[Click Here](https://top.gg/bot/840647743654723614)")
        embed.add_field(name="Download Beans Fight", value="[Andriod Download](https://play.google.com/store/apps/details?id=com.KhalouchDev.BeansFight)")
        embed.set_footer(text="$help")

        await ctx.send(embed=embed)

    @commands.command(description="See the weather in other cities", usage="<city>")
    async def weather(self, ctx, *, city:str):
        base_url = "http://api.openweathermap.org/data/2.5/weather?"

        if not city:
            return await ctx.send("Please specify a city")
        elif city.lower() == "isreal" or city.lower() == "israil":
            return await ctx.send(":middle_finger:")

        city_name = city
        complete_url = base_url + "appid=" + self.client.weather_api_key + "&q=" + city_name
        response = requests.get(complete_url)
        x = response.json()
        channel = ctx.message.channel

        if x["cod"] != "404":
            async with channel.typing():
                y = x["main"]
                current_temperature = y["temp"]
                current_temperature_celsiuis = str(round(current_temperature - 273.15))
                current_pressure = y["pressure"]
                current_humidity = y["humidity"]
                z = x["weather"]
                weather_description = z[0]["description"]

                weather_description = z[0]["description"]
                embed = discord.Embed(title=f"Weather in {city_name}",
                                color=ctx.guild.me.top_role.color,
                                timestamp=ctx.message.created_at,)
                embed.add_field(name="Descripition", value=f"**{weather_description}**", inline=False)
                embed.add_field(name="Temperature(C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
                embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
                embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**", inline=False)
                embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
                embed.set_footer(text=f"Requested by {ctx.author.name}")

            await channel.send(embed=embed)
        else:
            await channel.send("City not found.")

    @commands.command(description="Check out the stats of this server", aliases=['serverinfo'])
    @commands.guild_only()
    async def serverStats(self, ctx):
        botlist = []
        memberlist = []
        roleslist = []
        for member in ctx.guild.members:
            if member.bot:
                botlist.append(member)
            else:
                memberlist.append(member)
                
        for role in ctx.guild.roles:
            roleslist.append(role.name)

        embed = discord.Embed(title=ctx.guild.name, description=ctx.guild.description if ctx.guild.description else "\uFEFF",
                            thumbnail=ctx.guild.icon_url, color=self.colors, timestamp=ctx.message.created_at)
        embed.add_field(name="Member count", value=len(memberlist), inline=True)
        embed.add_field(name="Bot count", value=len(botlist), inline=True)
        embed.add_field(name="Roles", value=f"```{', '.join(roleslist) if ctx.guild.roles else 'No Roles found'}```", inline=False)
        embed.add_field(name="Owner", value=f"<@!{ctx.guild.owner_id}>", inline=True)
        embed.add_field(name="Created at", value=ctx.guild.created_at)
        embed.set_footer(text=f"ID: {ctx.guild.id}")

        await ctx.send(embed=embed)

    #Review [Perms]
    @commands.command(description="Information about a member", usage="<member>")
    @commands.guild_only()
    async def memberinfo(self, ctx, member: commands.MemberConverter=None):
        permslist = []
        roleslist = []        
        if not member:
            member = ctx.message.author
        for role in member.roles:
            roleslist.append(role.name)
        for perm in member.guild_permissions:
            permslist.append(str(perm))

        embed = discord.Embed(title=f"{member.name}#{member.discriminator}", description=member.mention,
                            thumbnail=member.avatar_url, color=self.colors, timestamp=ctx.message.created_at)
        embed.add_field(name="Joined", value=member.joined_at, inline=True)
        embed.add_field(name="Created at", value=member.created_at, inline=True)
        embed.add_field(name="Guild roles", value=f"```{', '.join(roleslist)}```", inline=False)
        embed.add_field(name="Guild Permissions", value=', '.join(permslist), inline=False)
        embed.set_footer(text=f"ID: {member.id}")

        await ctx.send(embed=embed)

    #Review [Channel Creation time]
    @commands.command(description="Shows the stats of the channel")
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.guild_only()
    async def channelstats(self, ctx):
        channel = ctx.channel
        embed = discord.Embed(title=f"Stats for **{channel.name}**", description=f"{'Category: {}'.format(channel.category.name) if channel.category else 'This channel is not in a category'}", color=random.choice(self.client.color_list))
        embed.add_field(name="Channel Guild", value=ctx.guild.name, inline=False)
        embed.add_field(name="Channel Id", value=channel.id, inline=False)
        embed.add_field(name="Channel Topic", value=f"{channel.topic if channel.topic else 'No topic.'}", inline=False)
        embed.add_field(name="Channel Position", value=channel.position, inline=False)
        embed.add_field(name="Channel Slowmode Delay", value=channel.slowmode_delay, inline=False)
        embed.add_field(name="Channel is nsfw?", value=channel.is_nsfw(), inline=False)
        embed.add_field(name="Channel is news?", value=channel.is_news(), inline=False)
        embed.add_field(name="Channel Creation Time", value=channel.created_at, inline=False)
        embed.add_field(name="Channel Permissions Synced", value=channel.permissions_synced, inline=False)
        embed.add_field(name="Channel Hash", value=hash(channel), inline=False)

        await ctx.send(embed=embed)

    @commands.command(description="Information about me", aliases=['botInfo'])
    async def about(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.client.guilds)
        memberCount = len(set(self.client.get_all_members()))

        embed = discord.Embed(title=f'Cube Bot Stats', color=random.choice(self.client.color_list), timestamp=ctx.message.created_at)

        embed.add_field(name='Bot Version: ', value=self.client.version)
        embed.add_field(name='Python Version: ', value=pythonVersion)
        embed.add_field(name='Discord.py Version: ', value=dpyVersion)
        embed.add_field(name='Total Guilds: ', value=serverCount)
        embed.add_field(name='Total Users: ', value=memberCount)
        embed.add_field(name='Bot Developer: ', value='<@658338910312857640>')
        embed.set_thumbnail(url=str(self.client.user.avatar_url))

        embed.set_footer(text=f'$help')

        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(utilities(client))

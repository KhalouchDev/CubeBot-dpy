import discord
from discord.ext import commands

class config(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['changePrefix'], description='Change the prefix of the server', usage="<prefix>")
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.default)
    @commands.guild_only()
    async def setPrefix(self, ctx, *, prefix=None):
        """
        Set a custom prefix for a guild
        """
        if prefix is None:
            return await ctx.send("Please give a prefix")
        elif prefix.startswith("<@!") and prefix.endswith(">"):
            return await ctx.send("Please choose another prefix")

        await self.client.prefixes.upsert({"_id": ctx.guild.id, "prefix": prefix})
        await ctx.send(f"The server's prefix has been set to `{prefix}`")

    @commands.command(aliases=['removePrefix', 'dp'], description='Reset the prefix of the server')
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.default)
    @commands.guild_only()
    async def deletePrefix(self, ctx):
        """
        Reset prefix for a guild
        """
        await self.client.prefixes.unset({"_id": ctx.guild.id, "prefix": 1})
        await ctx.send(f"The server's prefix has been set to `{self.client.defaultPrefix}`")

    @commands.group(name="set", invoke_without_command=True, description="Use with subcommands", usage="<subcommand>")
    async def _set(self, ctx):
        await ctx.send("Invalid sub-command passed")

    @_set.command(name="logsChannel",aliases=["logschannel"], description="Set a logs channel for the bot!", invoke_without_command=True)
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.default)
    @commands.guild_only()
    async def _logsChannel(self, ctx, channel: discord.TextChannel):
        
        #Insert data in database
        await self.client.logsChannel.upsert({"_id": ctx.guild.id, "logsChannelID": channel.id})
        await ctx.send(f"#{channel.name} has been set as Logs channel!")

    @_set.command(name="welcomeChannel",aliases=["welcomechannel"], description="Set a channel to welcome new members in!", invoke_without_command=True)
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.default)
    @commands.guild_only()
    async def _welcomeChannel(self, ctx, channel: discord.TextChannel):
        
        #Insert data in database
        await self.client.welcomeChannel.upsert({"_id": ctx.guild.id, "welcomeingChannelID": channel.id})
        await ctx.send(f"#{channel.name} has been set as Welcoming channel!")

    @_set.command(name="goodbyeChannel",aliases=["goodbyechannel"], description="Set a channel to say bye for members leaving!", invoke_without_command=True)
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.default)
    @commands.guild_only()
    async def _goodbyeChannel(self, ctx, channel: discord.TextChannel):
        
        #Insert data in database
        await self.client.goodbyeChannel.upsert({"_id": ctx.guild.id, "goodbyeChannelID": channel.id})
        await ctx.send(f"#{channel.name} has been set as goodbye message channel!")

    @_set.command(name="joinDM", aliases=["onJoinDM"], descreption="Sends members a DM when they Join")
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 5, commands.BucketType.default)
    @commands.guild_only()
    async def _joinDM(self, ctx, *, DM: str):
        #Insert data in database
        await self.client.onMemberJoinDM.upsert({"_id": ctx.guild.id, "DMcontent": DM})
        await ctx.send(f"`{DM}` has been set!")
        

def setup(client):
    client.add_cog(config(client))
import random
import datetime
import discord
from discord.ext import commands

class events(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
        
    @commands.Cog.listener()
    async def on_member_join(self, member):

        onMemberJoinDmCOLLECTION = await self.clioent.onMemberJoinDM.find(member.guild.id)
        if onMemberJoinDmCOLLECTION:
            dm = onMemberJoinDmCOLLECTION['DMcontent']
            try:
                await member.send(dm)
            except:
                pass

        # We find the channel specified by mods for sending welcomes
        welcomeChannelCOLLECTION = await self.client.welcomeChannel.find(member.guild.id)

        if welcomeChannelCOLLECTION:
            welcomingChannel = self.client.get_channel(welcomeChannelCOLLECTION['welcomeingChannelID'])
            
            embed = discord.Embed(description="Welcome to out Guild!", color=random.random.choice(self.client.color_list))
            embed.set_thumbnail(url=member.avatar_url)
            embed.author(name=member.name, icon_url=member.avatar_url)
            embed.set_footer(text=member.guild, icon_url=member.guild.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            
            await welcomingChannel.send(embed=embed)
        
        else:
            return

        # If member is muted, leaves and re-joinds the guild, he get the mute role back
        try:
            if self.client.muted_users[member.id]:
                role = discord.utils.get(member.guild.roles, name="Muted")
        
        except KeyError:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # On member remove we find a channel called general and if it exists,
        # send an embed saying goodbye from our guild
        data = await self.client.goodbyeChannel.find(member.guild.id)
        
        if not data:
            return

        goodbyeChannel = self.client.get_channel(data['goodbyeChannelID'])
        embed = discord.Embed(
                description="Goodbye from all of us..",
                color=random.choice(self.client.color_list),
            )
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
        embed.timestamp = datetime.datetime.utcnow()

        await goodbyeChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.cog_name == "ownerOnly":
            return

        if await self.client.command_usage.find(ctx.command.qualified_name) is None:
            await self.client.command_usage.upsert({"_id": ctx.command.qualified_name, "usage_count": 1})
        else:
            await self.client.command_usage.increment(ctx.command.qualified_name, 1, "usage_count")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore these errors
        ignored = (commands.CommandNotFound, commands.DisabledCommand)
        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.UserInputError):
            await ctx.send("Please fill in all required arguments")

        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("Role not found")

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command cannot be used in DMs")
        
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Member not found")
        
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("Role not found")

        elif isinstance(error, commands.CommandOnCooldown):
            # If the command is currently on cooldown trip this
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f" You must wait {int(s)} seconds to use this command!")
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(f" You must wait {int(m)} minutes and {int(s)} seconds to use this command!")
            else:
                await ctx.send(f" You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!")
        elif isinstance(error, commands.CheckFailure):
            # If the command has failed a check, trip this
            await ctx.send("You can't use this.")
        # Implement further custom checks for errors here...
        raise error


def setup(client):
    client.add_cog(events(client))
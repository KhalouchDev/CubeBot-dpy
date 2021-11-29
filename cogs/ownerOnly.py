import os 
import random
import discord
import asyncio
import traceback
from discord.ext import commands

import utils.jjson
from utils.util import Pag

class ownerOnly(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    #Commands
    @commands.command(description='Logs the bot out')
    @commands.is_owner()
    async def logout(self, ctx):
        await ctx.send(f"Hey {ctx.author.mention}, I am logging out ow :wave:")
        await self.client.logout()

    @commands.command(name="commandsStats", aliases=["commandusage, commandsInfo"], description="Show an overall usage for each command!")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.is_owner()
    async def command_stats(self, ctx):
        '''
        Shows the stats of the commands
        '''
        data = await self.client.command_usage.get_all()
        command_map = {item["_id"]: item["usage_count"] for item in data}

        # get total commands run
        total_commands_run = sum(command_map.values())

        # Sort by value
        sorted_list = sorted(command_map.items(), key=lambda x: x[1], reverse=True)

        pages = []
        cmd_per_page = 10

        for i in range(0, len(sorted_list), cmd_per_page):
            message = "Command Name: `Usage % | Num of command runs`\n\n"
            next_commands = sorted_list[i: i + cmd_per_page]

            for item in next_commands:
                use_percent = item[1] / total_commands_run
                message += f"**{item[0]}**: `{use_percent: .2%} | Ran {item[1]} times`\n"

            pages.append(message)

        await Pag(title="Command Usage Statistics!", color=0xC9B4F4, entries=pages, length=1).start(ctx)

    @commands.command(description="Enable a command", usage="<command>")
    @commands.is_owner()
    async def enable(self, ctx, *, command):
        command = self.bot.get_command(command)
        if command is None:
            return await ctx.send("Command not found")
        
        command.enabled = True
        await ctx.send(f"Enabled `{command.qualified_name}`")

    @commands.command(description="Disable a command", usage="<command>")
    @commands.is_owner()
    async def disable(self, ctx, *, command):
        command = self.bot.get_command(command)
        if command is None:
            return await ctx.send("Command not found")
        elif ctx.command == command or command.name == "enabled":
            return await ctx.send("You can't disbale this command")
        
        command.enabled = False
        await ctx.send(f"Disbaled `{command.qualified_name}`")

    @commands.command(description="Hide a command", usage="<command>")
    @commands.is_owner()
    async def hide(self, ctx, *, command):
        command = self.bot.get_command(command)
        if command is None:
            return await ctx.send("Command not found")
        
        command.hidden = True
        await ctx.send(f"Hid `{command.qualified_name}`")

    @commands.command(description="Unhide a command", usage="<command>")
    @commands.is_owner()
    async def unhide(self, ctx, *, command):
        command = self.bot.get_command(command)
        if command is None:
            return await ctx.send("Command not found")
        
        command.hidden = False
        await ctx.send(f"Unhid `{command.qualified_name}`")
    
    @commands.command(name="reload", description="Reload all/one of the bots cogs")
    @commands.is_owner()
    async def reload(self, ctx, cog=None):
        if not cog:
            #No cog provided, reload everything
            async with ctx.typing():
                embed = discord.Embed(title="Reloading all cogs!", color=0x808080, timestamp=ctx.message.created_at)
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.client.unload_extention(f"cogs.{ext[:-3]}")
                            self.client.load_extiontion(f"cogs.{ext[:-3]}")
                            embed.add_field(name=f"Reloaded `{ext}`", value='\uFEFF', inline=False)
                        except Exception as e:
                            embed.add_field(name=f"Failed tp reload: `{ext}`", value=e, inline=False)
                        await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        else:
            # Reload the specified cog
            async with ctx.typing():
                embed = discord.Embed(title=f"Reloading {cog}", color=0x808080, timestamp=ctx.message.created_at)
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # If file doesnt exist
                    embed.add_field(name=f"Failed tp reload: `{ext}`", value="This cog doesn't exist", inline=False)
                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.client.unload_extention(f"cogs.{ext[:-3]}")
                        self.client.load_extention(f"cogs.{ext[:-3]}")
                        embed.add_field(name=f"Reloaded `{ext}`", value="\uFEFF", inline=False)
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(name=f"Failed to reload: `{ext}`", value=desired_trace, inline=False)
                await ctx.send(embed=embed)

    @commands.command(description="Unload all/one of the bot's cogs")
    @commands.is_owner()
    async def unload(self, ctx, cog=None):
        if not cog:
            # No cog, means we unload all cogs
            async with ctx.typing():
                embed = discord.Embed(title="Unloading all cogs!", color=0x808080, timestamp=ctx.message.created_at)
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.client.unload_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(name=f"Unloaded: `{ext}`", value='\uFEFF', inline=False)
                        except Exception as e:
                            embed.add_field(
                                name=f"Failed to unload: `{ext}`",
                                value=e,
                                inline=False
                            )
                        await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        else:
            # unload the specific cog
            async with ctx.typing():
                embed = discord.Embed(title=f"Unloading {cog}!", color=0x808080, timestamp=ctx.message.created_at)
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # if the file does not exist
                    embed.add_field(
                        name=f"Failed to unload: `{ext}`",
                        value="This cog does not exist.",
                        inline=False
                    )

                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.client.unload_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Unloaded: `{ext}`",
                            value='\uFEFF',
                            inline=False
                        )
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(
                            name=f"Failed to Unload: `{ext}`",
                            value=desired_trace,
                            inline=False
                        )
                await ctx.send(embed=embed)

    @commands.command(description="Load all/one of the bot's cogs")
    @commands.is_owner()
    async def load(self, ctx, cog=None):
        if not cog:
            # No cog, means we load all cogs
            async with ctx.typing():
                embed = discord.Embed(title="Loading all cogs!", color=0x808080, timestamp=ctx.message.created_at)
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.client.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(name=f"Loaded: `{ext}`", value='\uFEFF', inline=False)
                        except Exception as e:
                            embed.add_field(name=f"Failed to Load: `{ext}`", value=e,inline=False)
                        await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        else:
            #load the specific cog
            async with ctx.typing():
                embed = discord.Embed(title=f"Loading {cog}", color=0x808080, timestamp=ctx.message.created_at)
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # if the file does not exist
                    embed.add_field(name=f"Failed to load: `{ext}`", value="This cog does not exist.", inline=False)

                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.client.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(name=f"Loaded: `{ext}`", value='\uFEFF', inline=False)
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(name=f"Failed to load: `{ext}`", value=desired_trace, inline=False)
                await ctx.send(embed=embed)


    @commands.command(description="Blacklist a use from using the bot")
    @commands.is_owner()
    async def blacklist(self, ctx, user: commands.MemberConverter):
        """
        Blacklist someone from the bot
        """
        if ctx.message.author.id == user.id:
            await ctx.send("Hey, you cannot blacklist yourself!")
            return

        self.client.blacklisted_users.append(user.id)
        data = utils.jjson.read_json("blacklist")
        data["blacklistedUsers"].append(user.id)
        utils.jjson.write_json(data, "blacklist")
        await ctx.send(f"Blacklisted {user.name}.")

    @commands.command(description="Remove a user from blacklist")
    @commands.is_owner()
    async def unblacklist(self, ctx, user: commands.MemberConverter):
        """
        Unblacklist someone from the bot
        """
        self.client.blacklisted_users.remove(user.id)
        data = utils.jjson.read_json("blacklist")
        data["blacklistedUsers"].remove(user.id)
        utils.jjson.write_json(data, "blacklist")
        await ctx.send(f"Unblacklisted {user.name}.")

    def setup(client):
        client.add_cog(ownerOnly(client))

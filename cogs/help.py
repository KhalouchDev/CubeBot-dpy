import discord
import random
from discord.ext import commands

notShowCogs = ["ownerOnly", "events"]

# Unimported part
class MyHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    def get_command_name(self, command):
        return command.qualified_name

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="**Help Command**", color=random.choice(self.context.bot.color_list))

        for cog in mapping:
            try:
                if cog.qualified_name in notShowCogs:
                    continue
                embed.add_field(name=f"**{cog.qualified_name.capitalize()}**", value=f"`{self.clean_prefix}help {cog.qualified_name}`", inline=True)
            except:
                pass

        embed.set_thumbnail(url=str(self.context.bot.user.avatar_url))
        embed.set_footer(text="[Vote On Topgg](https://top.gg/bot/840647743654723614)")
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        if cog.qualified_name in notShowCogs:
            return

        empty = ""

        embed = discord.Embed(title=cog.qualified_name.capitalize(), color=random.choice(self.context.bot.color_list))
        embed.set_footer(text="[Vote On Topgg](https://top.gg/bot/840647743654723614)")

        for command in cog.get_commands():
            commandAliases = ", ".join(command.aliases) if command.alaises else "No Alaises Found"
            embed.add_field(name=f"**```{command.name}```**", value=f'**{command.description}**\nAliases: `{commandAliases}`', color=random.choice(self.context.bot.color_list))
        
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        groupAliases = ", ".join(group.aliases) if group.aliases else "No Aliases Found"
        embed = discord.Embed(title=f"**{group.name}**", description=f"{group.description}\nAliases: `{groupAliases}`", color=random.choice(self.context.bot.color_list))
        embed.set_footer(text=random.choice("[Vote On Topgg](https://top.gg/bot/840647743654723614)", "$help"))
        for index, command in enumerate(group.commands):
            commandAliases = ", ".join(command.aliases) if command.aliases else "No Aliases Found"
            if command.usage is not None:
                embed.add_field(name=f"**{command.qualified_name}**", value=f"{command.description}\nAliases: `{commandAliases}`\nFormat: `{self.clean_prefix}{group.name} {command.name} {command.usage}`")
            else:
                embed.add_field(name=f"**{command.qualified_name}**", value=f"{command.description}\nAliases: `{commandAliases}`\nFormat: `{self.clean_prefix}{group.name} {command.name}`")

        channel = self.get_destination()
        await channel.send(embed=embed)
    
    async def send_command_help(self, command):
        embed = discord.Embed(title=f"**{self.get_command_name(command)}**", description=f"{command.description}", color=random.choice(self.context.bot.color_list))
        embed.set_footer(text=random.choice("[Vote On Topgg](https://top.gg/bot/840647743654723614)", "$help"))
        aliase = command.aliases

        if aliase:
            commandAliases = ", ".join(command.aliases)
            embed.add_field(name="Aliases: ", value=f"**`{commandAliases}`**", inline=False)
        else:
            embed.add_field(name="Aliases: ", value=f"No Aliases Found", inline=False)

        if command.usage is not None:
            embed.add_field(name="Format:", value=f"**`{self.clean_prefix}{command.qualified_name} {command.usage}`**", inline=False)
        else:
            embed.add_field(name="Format:", value=f"**`{self.clean_prefix}{command.qualified_name}`**", inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", description=error, color=random.choice(self.context.bot.color_list))
        embed.set_footer(text="If you think this is a bug, report it using the 'reportBug' command")
        channel = self.get_destination()
        await channel.send(embed=embed)
        
class help(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Setting the cog for the help
        help_command = MyHelp()
        help_command.cog = self # Instance of YourCog class
        client.help_command = help_command


def setup(client):
    client.add_cog(help(client))

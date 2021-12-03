import re
import random
import datetime
import asyncio
import discord

from dateutil.relativedelta import relativedelta
from discord.errors import Forbidden, HTTPException, InvalidArgument
from discord.ext.commands.core import check
from discord.ext import commands, tasks
import discord
from copy import deepcopy

#local import
from utils.util import Pag

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d|))+?")
time_dict = {'h': 3600, 's': 1, 'm': 60, 'd': 86400}


class timeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0

        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(f"{value} is an invalid time key, use d|h|m|s")
            except ValueError:
                raise commands.BadArgument(f"{value} is not a number")
        return round(time)

class moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.colors = random.choice(self.client.color_list)
        self.mute_task = self.check_current_mutes.start()

    def cog_unloaded(self):
        self.mute_task.cancel()

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Tasks
    @tasks.loop(minutes=5)
    async def check_current_mutes(self):
        currentTime = datetime.datetime.now()
        mutes = deepcopy(self.client.muted_users)
        
        for key, value in mutes.items():
            if value['muteDuration'] is None:
                continue

            unmuteTime = value['mutedAt'] + relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                guild = self.lient.get_guild(value['guildId'])
                member = guild.get_member(value['_id'])

                role = discord.utils.get(guild.roles, name='Muted')
                if not role:
                    await guild.create_role(name="Muted")

                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Unmuted {member.display_name}")

                await self.client.mutes.delete(member.id)
                try:
                    self.client.muted_users.pop(member.id)
                except KeyError:
                    pass

    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.client.wait_until_ready()


    # Commands
    @commands.command(description="Clears specific number of messages", aliases=['purge'], usage="<amount>")
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.guild_only()
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount+1)
        await ctx.send(f"{amount} messages have been cleared", delete_after=10)

    @commands.command(description="Kicks a member", usage="<member> [reason]")
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member:commands.MemberConverter, *, reason="No reason provided"):
        if member.id == ctx.bot.user.id:
            return await ctx.send("I can't kick myself :)")

        embed = discord.Embed(title=f"`{member.name}` has been kicked from the server", description=reason,
                            thumbnail=member.avatar_url, color=self.colors,
                            timestamp=datetime.datetime.utcnow())
        await ctx.send(embed=embed)
        await member.kick(reason=reason)

        DMembed = discord.Embed(title=f"You have been kicked from `{ctx.guild.name}`", description=reason,
                            thumbnail=ctx.guild.icon_url, color=self.colors,
                            timestamp=datetime.datetime.utcnow())
        try:
            await member.send(embed=DMembed)
        except:
            pass

    @commands.command(description="Bans a member", usage="<member> [reason]")
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: commands.MemberConverter, *, reason="No reason provided"):
        if member.id == ctx.bot.user.id:
            return await ctx.send("I can't ban my self :)")
        
        embed = discord.Embed(title=f"`{member.name}` has been banned from the server", description=reason,
                            thumbnail=member.avatar_url, color=self.colors,
                            timestamp=datetime.datetime.utcnow())
        await ctx.send(embed=embed)
        await member.ban(reason=reason)
        
        DMembed = discord.Embed(title=f"You have been banned from `{ctx.guild.name}`", description=reason,
                            thumbnail=ctx.guild.icon_url, color=self.colors,
                            timestamp=datetime.datetime.utcnow())
        try:
            await member.send(embed=embed)
        except:
            pass

    @commands.command(description="Unbans a member", usage="<member> [reason]")
    @commands.has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, member: commands.MemberConverter, *, reason = "No reason provided"):
        member = await self.client.fetch_user(int(member))
        if not member:
            return await ctx.send(f"`{member.name}` is not banned")

        await ctx.guild.unban(member, reason=reason)
        
        embed = discord.Embed(title=f"Unbanned `{member.name}`", description=reason,
                            thumbnail=member.avatar_url, color=self.colors,
                            timestamp=datetime.datetime.utcnow())
        await ctx.send(embed=embed)

        DMembed = discord.Emebed(title=f"You have been unbanned from `{ctx.guild.name}`", description=reason,
                                thumbnail=ctx.guild.icon_url, color=self.colors,
                                timestamp=datetime.datetime.utcnow())
        try:
            await member.send(embed=DMembed)
        except:
            pass

    @commands.command(description="Mutes a member", usage="<user> [time] [reason]")
    @commands.has_guild_permissions(kick_members=True) #Change
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def mute(self, ctx, member: commands.MemberConverter, time: timeConverter = None, *, reason="No reason provided"):
        if member.id == ctx.bot.user.id:
            return await ctx.send("I can't mute myself :)")
        
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, speak=False, send_messages=False,
                                            read_message_history=True, read_messages=True)
        try:
            if self.client.muted_users[member.id]:
                return await ctx.send(f"`{member.name}` is already muted")
        except KeyError:
            pass

        data = {'_id': member.id, 'mutedAt': datetime.datetime.now(), 'muteDuration': time or None,
                'muteBy': ctx.author.id, 'guildId': ctx.guild.id}
        await self.client.mutes.upsert(data)
        self.client.meted_users[member.id] = data

        await member.add_roles(role)

        embed = discord.Embed(title=f"`{member.name}` has been muted", description=reason,
                            thumbnail=member.avatar_url, color=self.colors,
                            timestamp=datetime.datetime.utcnow())
        DMembed = discord.Embed(title=f"You have bee muted in `{ctx.guild.name}`", description=reason,
                                thumbnail=ctx.guild.icon_url, color=self.colors,
                                timestamp=datetime.datetime.utcnow())
        if not time:
            pass
        else:
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(time, 60)

            if int(hours):
                embed.add_field(name="Muted for: ", value=f"{hours} hours, {minutes} minutes, {seconds} seconds")
                DMembed.add_field(name="Muted for: ", value=f"{hours} hours, {minutes} minutes, {seconds} seconds")
            elif int(minutes):
                embed.add_field(name="Muted for: ", value=f"{minutes} minutes, {seconds} seconds")
                DMembed.add_field(name="Muted for: ", value=f"{hours} hours, {minutes} minutes, {seconds} seconds")
            elif int(seconds):
                embed.add_field(name="Muted for: ", value=f"{seconds} seconds")
                DMembed.add_field(name="Muted for: ", value=f"{hours} hours, {minutes} minutes, {seconds} seconds")
        await ctx.send(embed=embed)
        try:
            await member.send(embed=DMembed)
        except:
            pass

        if time and time < 300:
            await asyncio.sleep(time)

            if role in member.roles:
                unmuteDM = discord.Embed(title=f"You have been unmutted in `{ctx.guild.name}`", description=f"\uFEFF",
                                        thumbnail=ctx.guild.icon_url, color=self.colors,
                                        timestamp=datetime.datetime.utcnow())
                await member.remove_roles(role)
                await member.send(embed=unmuteDM)
            
            await self.client.mutes.delete(member.id)
            try:
                self.client.muted_users.pop(member.id)
            except KeyError:
                pass

    @commands.command(description="Unmute a member", usage="<member> [reason]")
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def unmute(self, ctx, member:commands.MemberConverter, *, reason="No reason provided"):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            return
        
        await self.client.mutes.delete(member.id)
        try:
            self.client.muted_users.pop(member.id)
        except KeyError:
            pass

        # If member is not muted
        if role not in member.roles:
            return await ctx.send(f"`{member.name}` is not muted")

        # Remove the muted role
        embed = discord.Embed(title=f"`{member.name}` has been unmuted", description=reason,
                            thumbnail=member.avatar_url, color=self.colors,
                            timestamp=datetime.datetime.utcnow())
        DMembed = discord.Embed(title=f"You have been unmuted in `{ctx.guild.name}`", description=reason,
                                thumbnail=ctx.guild.icon_url, color=self.colors,
                                timestamp=datetime.datetime.utcnow())

        await member.remove_roles(role)
        await ctx.send(embed=embed)
        try:
            await member.send(embed=DMembed)
        except:
            pass

    @commands.command(description="Send a member to prison", usage='<member> [reason]', enabled=False, hidden=True)
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.guild_only()
    async def prison(self, ctx, member:commands.MemberConverter, *, reason="No reason provided"):
        if member.id == ctx.bot.user.id:
            return await ctx.send("I can't send myself to prison")
        
        prisonChannel = discord.utils.get(member.guild.text_channels, name="prisoners-talk")
        if not prisonChannel:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.guild.me: discord.PermissionOverwrite(read_messaged=True)
            }
            await ctx.guild.create_text_channel(name="prisoners-talk", overwrites=overwrites)

        prisonerRole = discord.utils.get(ctx.guild.roles, name="Prisoner")
        if not prisonerRole:
            prisonerRole = await ctx.guild.create_role(name="Prisoner")
            for channel in ctx.guild.channels:
                if channel.name != "prisoners-talk":
                    await channel.set_permissions(prisonerRole, speak=False, send_messages=False,
                                                read_messaged=False, read_message_history=False)
        try:
            await member.edit_(roles=[])
            embed = discord.Embed(title=f"`{member.name}` has been sent to prison", description=reason,
                                thumbnail=member.avatar_url, color=self.colors, timestamp=datetime.datetime.utcnow())
            DMembed = discord.Embed(title=f"You have been sent to prison in `{ctx.guild.name}` server", description=reason,
                                    thumbnail=ctx.guild.icon_url, color=self.colors, timestamp=datetime.datetime.utcnow())

            await ctx.send(embed=embed)
            try:
                await member.send(embed=DMembed)
            except:
                pass
        except Forbidden:
            await ctx.send(f"I don't have the required perms to send `{member.name}` to prison")
        except HTTPException:
            await ctx.send("Operation failed")

    @commands.command(description="Remove a member from prison", usage="<member> [reason]", enabled=False, hidden=True)
    @commands.has_guild_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_roles=True, manage_channels=True)
    @commands.guild_only()
    async def unprison(self, ctx, member: commands.MemberConverter, reason="No reason provided"):
        prisonerRole = discord.utils.get(ctx.guild.roles, name="Prisoner")
        if not prisonerRole:
            return

        try:
            await member.remove_roles(prisonerRole)
            embed = discord.Embed(title=f"`{member.name}` has been removed to prison", description=reason,
                                thumbnail=member.avatar_url, color=self.colors, timestamp=datetime.datetime.utcnow())
            DMembed = discord.Embed(title=f"You have been sent to prison in `{ctx.guild.name}` server", description=reason,
                                    thumbnail=ctx.guild.icon_url, color=self.colors, timestamp=datetime.datetime.utcnow())
            await ctx.send(embed=embed)
            try:
                await member.send(embed=DMembed)
            except:
                pass
        except Forbidden:
            await ctx.send(f"I don't have the required perms to remove `{member.name}` from prison")
        except HTTPException:
            await ctx.send("Operation failed")

    @commands.group(description="Group of commands to help in role management", aliases=['roles'], invoke_wihtout_command=True, usage="<subcommand>")
    @commands.guild_only()
    async def role(self, ctx):
        await ctx.send("Invalid sub-command passed")

    @role.command(description="Remove a role from a member", usage="<member> <role> [reason]")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def remove(self, ctx, member:commands.MemberConverter, role:commands.RoleConverter, *, reason="No reason provided"):
        if role not in member.roles:
            return await ctx.send(f"`{member.name}` doesn't have the `{role.name}` role")

        try:
            await member.remove_role(role)
            embed = discord.Embed(title=f"Removed `{role.name}` role from `{member.name}`", description=reason,
                                thumbnail=member.avatar_url, color=self.colors, timestamp=datetime.datetime.utcnow())
            DMembed = discord.Embed(title=f"`{role.name}` was removed from you in `{ctx.guild.name}` server", description=reason,
                                    thumbnail=ctx.guild.icon_url, color=self.colors, timestamp=datetime.datetime.utcnow())
            await ctx.send(embed=embed)
            try:
                await member.send(embed=DMembed)
            except:
                pass
        except Forbidden:
            await ctx.send(f"I don't have the required perms to remove the `{role.name}` role from `{member.name}`")
        except HTTPException:
            await ctx.send("Operation failed")

    @role.command(description="Clear all roles of a member", usage="<member> [reason]")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def clear(self, ctx, member:commands.MemberConverter, *, reason="No reason provided"):
        try:
            embed = discord.Embed(title=f"Cleared a total of `{len(member.roles)}` roles from `{member.name}`", description=reason,
                                thumbnail=member.avatar_url, color=self.colors, timestamp=datetime.datetime.utcnow())
            DMembed = discord.Embed(title=f"All your roles have been cleared in `{ctx.guild.name}` server", description=reason,
                                    thumbnail=ctx.guild.icon_url, color=self.colors, timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Roles removed: ", value="```"+", ".join(member.roles)+"```")
            DMembed.add_field(name="Roles removed: ", value="```"+", ".join(member.roles)+"```")

            await member.edit(roles=[])
            await ctx.send(embed=embed)
            try:
                await member.send(embed=DMembed)
            except:
                pass

        except Forbidden:
            await ctx.send(f"I don't have the required perms to clear the roles of `{member.name}`")
            
        except HTTPException:
            await ctx.send("Operation failed")

    @commands.command(descrition="Create an new role", usage="<name> [permissions] [color] [hoist] [mentionable]", enabled=False, hidden=True)
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def createrole(self, ctx, name:str="new role"):
        try:
            await ctx.guild.create_role(name=name)
            await ctx.send(f"Created new role with name {name}")
        except Forbidden:
            await ctx.send(f"I don't have the required perms to create a role")
        except HTTPException:
            await ctx.send("Operation failed")
        except InvalidArgument:
            await ctx.send("An invalid keyword argument was given")

    @commands.command(description="Warn a member", usage="<member> [reason]")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def warn(self, ctx, member:commands.MemberConverter, *, reason):
        if member.id == ctx.author.id:
            return await ctx.send(f"You can't wanr yourseld :facepalm:")
        elif member.id == ctx.bot.user.id:
            return await ctx.send(f"I can't wanr my self :)")

        current_warn_count = len(await self.client.warns.find_many_by_custom({"user_id": member.id,
                                                                            "guild_id": member.guild.id})) + 1
        
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id, "number": current_warn_count,}
        warn_data = {"reason": reason, "timestamp": ctx.message.created_at, "warned_by": ctx.author.id}

        await self.client.wanrns.upsert_custom(warn_filter, warn_data)

        embed = discord.Embed(title=f"`{member.name}` has been warned", description=reason,
                            thumbnail=member.avatar_url, color=self.colors,
                            timestamp=datetime.datetime.utcnow())
        DMembed = discord.Embed(title=f"You have been warned in `{member.guild.name}`", description=reason,
                                thumbnail=ctx.guild.icon_url, color=self.colors,
                                timestamp=datetime.datetime.utcnow())
        
        await ctx.send(member.mention, embed=embed)
        try:
            await member.send(embed=DMembed)
        except:
            pass

    @commands.command(description="Remove a warning from a member", usage="<member> [warning number] [reason]")
    @commands.has_guild_permissions(manage_guild=True)
    @commands.guild_only()
    async def deletewarn(self, ctx, member:commands.MemberConverter, warn: int = None, *, reason="No reason provided"):
        filter_dict = {"user_id": member.id, "guild_id": member.guild.id}
        if warn:
            filter_dict["number"] = warn

        was_deleted = await self.client.warns.delete_by_custom(filter_dict)
        if was_deleted and was_deleted.acknowleged:
            if warn:
                return await ctx.send(f"Deleted warn number `{warn}` from `{member.name}`")

            return await ctx.send(f"Deleted `{was_deleted.deleted_count}` warns for `{member.name}`")

        await ctx.send(f"Warn number `{warn}` was not found for `{member.display_name}`")
    
    @commands.command(description="List all warns of a member (can be used by all members)", usage="<member>")
    @commands.guild_only()
    async def warns(self, ctx, member:commands.MemberConverter):
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id}
        warns = await self.client.warns.find_many_by_custom(warn_filter)

        if not bool(warns):
            return await ctx.send(f"`{member.name}` has no warns")

        warns = sorted(warns, key=lambda x: x['number'])

        pages = []
        for warn in warns:
            description = f"""
            Warn Number: `{warn['number']}`
            Warn Reason: `{warn['reason']}`
            Warned By: `<@!{warn['warned_by']}>`
            Warn Date: `{warn['timestamp'].strftime("%I:%M %p %B %d, %Y")}`
                            """
            pages.append(description)

        await Pag(title=f"`{member.name}'s` warns", color=self.colors, entries=pages, length=1).start(ctx)


def setup(client):
    client.add_cog(moderation(client))
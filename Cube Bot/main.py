# Standard imports
import os
import json
import logging

# Third party libraries
import discord
import topgg
from pathlib import Path
import motor.motor_asyncio
from discord.ext import commands

# Local code
from utils.mongo import Document

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f'{cwd}\n-----')

async def get_prefix(client, message):
    # If dm's
    if not message.guild:
        return commands.when_mentioned_or(client.defaultPrefix)(client, message)

    try:
        data = await client.prefixes.find(message.guild.id)

        # Make sure we have a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(client.defaultPrefix)(client, message)
        return commands.when_mentioned_or(data["prefix"])(client, message)
    except:
        return commands.when_mentioned_or(client.defaultPrefix)(client, message)

# Defining stuff
defaultPrefix = '&'
secret_file = json.load(open(cwd+'/client_config/secrets.json'))
owner_id = 658338910312857640
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix=defaultPrefix, case_insensitive=True, owner_id=owner_id, intents=intents)

client.config_token = secret_file["token"]
client.connection_url = secret_file["mongo"]
client.joke_api_key = secret_file["x-rapidapi-key"]
client.weather_api_key = secret_file["weather-api-key"]

logging.basicConfig(level=logging.INFO)

client.version = 2.0

client.owner_id = owner_id
client.defaultPrefix = defaultPrefix
client.blacklisted_users = []
client.muted_users = {}
client.cwd = cwd

client.colors = {   #define color list
    'AQAU': 0x1ABC9C,
    'GREEN': 0x2ECC71,
    'BLUE': 0x3498DB,
    'PURPLE': 0x9B59B6,
    'LUMINOUS_VIVID_PINK': 0xE91E63,
    'GOLD': 0xF1C40F,
    'ORANGE': 0xE67E22,
    'RED': 0xE74C3C,
    'NAVY': 0x34495E,
    'DARK_AQUA': 0x11806A,
    'DARK_BLUE': 0x206694,
    'DARK_PURPLE': 0x71368A,
    'DARK_VIVD_PINK': 0xAD1457,
    'DARK_GOLD': 0xC27C0E,
    'DARK_ORANGE': 0xA84300,
    'DARK_RED': 0x992D22,
    'DARK_NAVI': 0x2C3E50
}
client.color_list = [c for c in client.colors.values()]

#Events
@client.event
async def on_ready():
    print(f'-----\nLogged in as: {client.user.name} : {client.user.id}\n-----\nMy current prefix is: {client.defaultPrefix}\n-----')
    await client.change_presence(activity=discord.Game(f'{client.defaultPrefix}help'))

    currentMutes = await client.mutes.get_all()

    for mute in currentMutes:
        client.muted_users[mute["_id"]] = mute

    print("Intialized Database\n-----")
    print(f"Currently in {len(client.guilds)} guilds\n-----")
    print(f"{client.user.name} is ready!")

@client.event
async def on_message(message):
    # Ignore messages sent by yourself
    if message.author.bot:
        return

    # A wat to blacklist users from the bot by not processing commands
    # if the author is in the blacklist_users list
    if message.author.id in client.blacklisted_users:
        return

    # Whenever the bot is tagged, respond with its prefix
    if message.content.startswith(f"<@!{client.user.id}>") and len(message.content) == len(f"<@!{client.user.id}>"):
        data = await client.prefixes.find_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = client.defaultPrefix
        else:
            prefix = data["prefix"]
        await message.channel.send(f"My prefix here is `{prefix}`")

    await client.process_commands(message)

if __name__ == '__main__':
    # When running this file, if it is the 'main' file
    # I.E. its not being imported from another python file run this

    # defing database objects
    client.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(client.connection_url))
    client.db = client.mongo["electron"]
    client.prefixes = Document(client.db, "prefixes")
    client.mutes = Document(client.db, "mutes")
    client.warns = Document(client.db, "warns")
    client.logsChannel = Document(client.db, "logsChannel")
    client.welcomeChannel = Document(client.db, "welcomeChannel")
    client.goodbyeChannel = Document(client.db, "goodbyeChannel")
    client.onMemberJoinDM = Document(client.db, "memberJoinDM")
    client.command_usage = Document(client.db, "command_usage")
    client.suggestions = Document(client.db, "suggestions")
    client.bugReports = Document(client.db, "bugs")

    # Running cogs
    for file in os.listdir(cwd+"/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            client.load_extension(f"cogs.{file[:-3]}") # Run the file

client.run(client.config_token) # Run the bot

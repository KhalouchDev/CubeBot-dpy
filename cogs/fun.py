from re import I
import random
import discord

from discord.ext import commands
from aiohttp import ClientSession

class fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.colors = random.choice(client.color_list)

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Commands
    @commands.command(description="I see you forgot the soviet anthem...")
    async def sovietAnthem(self, ctx):
        anthem = f"""
                ```
Союз нерушимый республик свободных
Сплотила навеки Великая Русь.
Да здравствует созданный волей народов
Единый, могучий Советский Союз!

Припев:
Славься, Отечество наше свободное,
Дружбы народов надёжный оплот!
Знамя советское, знамя народное
Пусть от победы к победе ведёт!

Сквозь грозы сияло нам солнце свободы,
И Ленин великий нам путь озарил:
Нас вырастил Сталин — на верность народу,
На труд и на подвиги нас вдохновил!

Припев:
Славься, Отечество наше свободное,
Счастья народов надёжный оплот!
Знамя советское, знамя народное
Пусть от победы к победе ведёт!

Мы армию нашу растили в сраженьях.
Захватчиков подлых с дороги сметём!
Мы в битвах решаем судьбу поколений,
Мы к славе Отчизну свою поведём!

Припев:
Славься, Отечество наше свободное,
Славы народов надёжный оплот!
Знамя советское, знамя народное
Пусть от победы к победе ведёт!
                ```
                """

        await ctx.send(anthem)

    @commands.command(name="8ball", description="Just normal 8ball...")
    async def _8ball(self, ctx, *, question):
        answers = ["It is certain", "It is decidedly so", "Without a doubt", "Yes - definitely", "You may rely on it",
                   "As I see, Yes", "Most likely", "Outlook good", "Yes", "Signs point to yes", "Reply hazy. try again",
                   "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
                   "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtfull"]
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(answers)}')
        
    @commands.command()
    async def thumbsup(self, ctx):
        await ctx.send(f"░░░░░░░░░░░░░░░░░░░░░░█████████░░░░░░░░░\n░░███████░░░░░░░░░░███▒▒▒▒▒▒▒▒███░░░░░░░\n░░█▒▒▒▒▒▒█░░░░░░░███▒▒▒▒▒▒▒▒▒▒▒▒▒███░░░░\n░░░█▒▒▒▒▒▒█░░░░██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██░░\n░░░░█▒▒▒▒▒█░░░██▒▒▒▒▒██▒▒▒▒▒▒██▒▒▒▒▒███░\n░░░░░█▒▒▒█░░░█▒▒▒▒▒▒████▒▒▒▒████▒▒▒▒▒▒██\n░░░█████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██\n░░░█▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒▒▒▒▒▒██\n░██▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒██▒▒▒▒▒▒▒▒▒▒██▒▒▒▒██\n██▒▒▒███████████▒▒▒▒▒██▒▒▒▒▒▒▒▒██▒▒▒▒▒██\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒████████▒▒▒▒▒▒▒██\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██░\n░█▒▒▒███████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██░░░\n░██▒▒▒▒▒▒▒▒▒▒████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█░░░░░\n░░████████████░░░█████████████████░░░░░░")

    @commands.command(description="pp", usage="[member]")
    async def pp(self, ctx, member:commands.MemberConverter = None):
        randomChoice = ["", "=", "==", "===", "====", "=====", "======", "======="]

        if not member:
            member = ctx.author
        embed = discord.Embed(title="**pp size machine**", color = self.colors)
        embed.add_field(name=f"{member.name}'s pp", value=f"8{random.choice(randomChoice)}D", inline=False)
        await ctx.send(embed=embed)

    @commands.command(description="I see you forgot the english alphabet....")
    async def alphabets(self, ctx):
        alphabet = ["a", "b", "c", "d", "e", "f", "g","h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        embed = discord.Embed(title="_The English alphabets_", description="Never forget the alphabets again!",
                            color=self.colors)
        embed.add_field(name=', '.join(alphabet), value=f"\uFEFF")

        await ctx.send(embed=embed)

    @commands.command(description="stea- Look at someones avatar", aliases=['pfp'], usage="[member]")
    async def avatar(self, ctx, member:commands.MemberConverter = None):
        if not member:
            member = ctx.author
        
        embed = discord.Embed(title=f"{member.name}'s avatar", color=self.colors)
        embed.set_image(url=member.avatar_url)
        embed.set_footer(text=f"{member.name}'s ID: {member.id}")

        await ctx.send(embed=embed)

    @commands.command(description="Look at the servers avatar", aliases=["guildIcon"])
    async def serverIcon(self, ctx):
        if not ctx.guild.icon:
            return await ctx.send("This server has no icon")
        embed = discord.Embed(title=f"`{ctx.guild.name}`'s icon", color=self.colors)
        embed.set_image(url=ctx.guild.icon_url)
        embed.set_footer(text=f"Guild ID: {ctx.guild.id}")

        await ctx.send(embed=embed)

    @commands.command(description="Find out who is gay in the server")
    async def whosGay(self, ctx):

        memberList = []

        for member in ctx.guild.members:
            if not member.bot:
                memberList.append(member.name)
        gay = random.choice(memberList)
        await ctx.send(f"`{gay}` is gay")

    @commands.command(description="How much of a gay are you?", usage="[member]")
    async def gayrate(self, ctx, member:commands.MemberConverter = None):
        randomValue = random.randint(1, 101) #Choose a random value between 0 and 100

        if not member:
            member = ctx.author
        
        await ctx.send(f"`{member.name}` is {randomValue}% gay")

    @commands.command(description="How much of a simp are you?", usage="[member]")
    async def simprate(self, ctx, member:commands.MemberConverter = None):
        randomValue = random.randint(1, 101)

        if not member:
            member = ctx.author

        await ctx.send(f"`{member.name}` is {randomValue}% simp")

    @commands.command(description="Are you a nird?", aliases=["smartrate"], usage="[member]")
    async def nirdrate(self, ctx, member:commands.MemberConverter = None):
        randomValue = random.randint(1, 101)

        if not member:
            member = ctx.author
        if randomValue == 100:
            return await ctx.send(f"`{member.name}` is a big nird :brain:")

        await ctx.send(f"`{member.name}` is {randomValue}% nird")

    @commands.command(description="Take some dadjokes", aliases=['dadjokes'])
    async def dadjoke(self, ctx):
        url = "https://dad-jokes.p.rapidapi.com/random/joke"

        headers = {
            'x-rapidapi-key': "bc5e15ace2msh7a484e5730f3f7dp1f8048jsn341f62c25600",
            'x-rapidapi-host': "dad-jokes.p.rapidapi.com"
        }

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                r = await response.json()
                r = r["body"][0]
                await ctx.send(f"**{r['setup']}**\n\n||{r['punchline']}||")


def setup(client):
    client.add_cog(fun(client))

import os
import discord
import subprocess
import time

from discord.ext import commands, tasks
import subprocess
from dotenv import load_dotenv
import time
import threading
from requests import get

load_dotenv()

TOKEN = os.getenv('TEST_TOKEN')
serverChannel = os.getenv('TEST_STATUS')
notifyChannel = os.getenv('TEST_NOTIFY')
advChannel = os.getenv('TEST_ADV')
roleID = os.getenv('TEST_ROLE')

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

curPlayers = []
version = ""
playerCount = 0
ip = ""
advancement = ""
check = 0

def search(output):
    global curPlayers
    global ip
    global version
    global playerCount
    global advancement
    global check
    
    lines = output.split("\r\n")
    for line in lines:
        advancement = "blank"
        if "version" in line:
            print(line)
            version = line.split()[-1]

        elif "joined the game" in line and "<" not in line and ">" not in line:
            playerCount += 1
            line = line.split()
            del line[:3]
            print(line)
            curPlayers.append(line[0])

        elif "left the game" in line and "<" not in line and ">" not in line:
            playerCount -= 1
            line = line.split()
            del line[:3]
            print(line)
            curPlayers.remove(line[0])

        elif "the advancement" in line: #and "<" not in line and ">" not in line:
            line = line.split()
            del line[:3]
            advancement = " ".join(str(x) for x in line)
            check = 1
            print(advancement)



def serverSubprocess():
    global version
    with subprocess.Popen(['startserver.bat'], stdout=subprocess.PIPE) as process:
        while process.poll() == None:
            output = process.stdout.read1().decode('utf-8')
            search(output)
            time.sleep(1)

@bot.event
async def on_ready():
    global ip
    await bot.change_presence(activity=discord.CustomActivity(name='Server is Online'))
    channel =  bot.get_channel(int(notifyChannel))

    notification = discord.utils.get(channel.guild.roles, id=int(roleID))
    embed = discord.Embed(title=":desktop: Server is Online :desktop:", color = discord.Color.from_rgb(91,135,49))
    embed.add_field(name="", value=f'{notification.mention}')
    await channel.send(embed=embed)

    ip = get('https://api.ipify.org').content.decode('utf8')

    advance.start()
    

@bot.command()
async def server(ctx):
    if ctx.channel.id == int(serverChannel):
        embed = discord.Embed(title=":green_circle:  Server Info", color = discord.Color.from_rgb(91,135,49))
        embed.add_field(name="Player Count :busts_in_silhouette:", value=str(playerCount) + "/20", inline = True)
        embed.add_field(name="Version :hammer_and_wrench:", value= version, inline = True)
        embed.add_field(name="Server Adress :placard:", value= ip, inline = True)
        embed.add_field(name="Online Players:", value='\n'.join(curPlayers), inline = False)
        await ctx.send(embed=embed)

@bot.command()
async def notify(ctx):
    if ctx.channel.id == int(serverChannel):
        author = ctx.message.author
        guild = ctx.guild
        rolename = "notifications"
        role = discord.utils.get(guild.roles,name=rolename)

        if role in author.roles:
            await author.remove_roles(role)
            embed = discord.Embed(color = discord.Color.from_rgb(221, 46, 68))
            embed.add_field(name="", value=" :outbox_tray: You have been removed from Notifications :outbox_tray: ")
            await ctx.send(embed=embed)
        else:
            await author.add_roles(role)
            embed = discord.Embed(color = discord.Color.from_rgb(29, 131, 72))
            embed.add_field(name="", value=" :inbox_tray: You have been added to Notifications :inbox_tray: ")
            await ctx.send(embed=embed)

@tasks.loop(seconds=0.5)
async def advance():
    global check
    global advancement
    channel = bot.get_channel(int(advChannel))
    if check == 1:
        await channel.send(advancement)
   
subprocessThread = threading.Thread(target=serverSubprocess)
subprocessThread.start()

bot.run(TOKEN)


import os
import discord
import subprocess
import time

from discord.ext import commands
import subprocess
from dotenv import load_dotenv
import time
import threading
from requests import get

load_dotenv()

TOKEN = os.getenv('TOKEN')
statusChannel = os.getenv('STATUS')
notifyChannel = os.getenv('NOTIFY')
advChannel = os.getenv('TEST_ADV')

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

curPlayers = []
version = ""
playerCount = 0
ip = ""
advancement = ""

def search(output):
    global curPlayers
    global ip
    global version
    global playerCount
    global advancement
    
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

        """elif "the advancement" in line: #and "<" not in line and ">" not in line:
            line = line.split()
            del line[:3]
            advancement = " ".join(str(x) for x in line)
            print(advancement)"""



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
    await channel.send("@notifications Server is Online")
    ip = get('https://api.ipify.org').content.decode('utf8')

@bot.command()
async def server(ctx):
    if ctx.channel.id == int(statusChannel):
        embed = discord.Embed(title=":green_circle:  Server Info", color = discord.Color.from_rgb(91,135,49))
        embed.add_field(name="Player Count :busts_in_silhouette:", value=str(playerCount) + "/20", inline = True)
        embed.add_field(name="Version :hammer_and_wrench:", value= version, inline = True)
        embed.add_field(name="Server Adress :placard:", value= ip, inline = True)
        embed.add_field(name="Online Players:", value='\n'.join(curPlayers), inline = False)
        await ctx.send(embed=embed)

@bot.command()
async def notify(ctx):
    if ctx.channel.id == int(notifyChannel):
        author = ctx.message.author
        guild = ctx.guild
        rolename = "notifications"
        role = discord.utils.get(guild.roles,name=rolename)

        if role in author.roles:
            await author.remove_roles(role)
            embed = discord.Embed(color = discord.Color.from_rgb(29, 131, 72))
            embed.add_field(name="", value=" :outbox_tray: You have been removed from Notifications :outbox_tray: ")
            await ctx.send(embed=embed)
        else:
            await author.add_roles(role)
            embed = discord.Embed(color = discord.Color.from_rgb(29, 131, 72))
            embed.add_field(name="", value=" :inbox_tray: You have been added to Notifications :inbox_tray: ")
            await ctx.send(embed=embed)
            
subprocessThread = threading.Thread(target=serverSubprocess)
subprocessThread.start()
bot.run(TOKEN)


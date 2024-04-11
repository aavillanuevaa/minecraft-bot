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

TOKEN = os.getenv('TESTTOKEN')

statusChannel = 1216537851844366456
notifyChannel = 1228059375491350638

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

curPlayers = []
version = ""
playerCount = 0
ip = ""

def search(output):
    global curPlayers 
    global ip 
    global version 
    global playerCount 

    lines = output.split("\r\n")
    for line in lines:
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
    channel =  bot.get_channel(notifyChannel)
    await channel.send("@everyone Server is Online")
    ip = get('https://api.ipify.org').content.decode('utf8')

@bot.command()
async def server(ctx):
    if ctx.channel.id == statusChannel:
        embed = discord.Embed(title=":green_circle:  Server Info", color = discord.Color.from_rgb(91,135,49))
        embed.add_field(name="Player Count :busts_in_silhouette:", value=str(playerCount) + "/20", inline = True)
        embed.add_field(name="Version :hammer_and_wrench:", value= version, inline = True)
        embed.add_field(name="Server Adress :placard:", value= ip, inline = True)
        embed.add_field(name="Online Players:", value='\n'.join(curPlayers), inline = False)
        await ctx.send(embed=embed)

subprocessThread = threading.Thread(target=serverSubprocess)
subprocessThread.start()
bot.run(TOKEN)


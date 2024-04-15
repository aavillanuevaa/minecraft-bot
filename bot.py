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

TOKEN = os.getenv('TOKEN')
serverChannel = os.getenv('STATUS')
notifyChannel = os.getenv('NOTIFY')
advChannel = os.getenv('ADV')
roleID = os.getenv('ROLE')

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
        check = 0

        #look for version
        if "version" in line:
            print(line)
            version = line.split()[-1]

        #look for connection
        elif "joined the game" in line and "<" not in line and ">" not in line:
            playerCount += 1
            line = line.split()
            del line[:3]
            print(line)
            curPlayers.append(line[0])
        
        #look for disconnection
        elif "left the game" in line and "<" not in line and ">" not in line:
            playerCount -= 1
            line = line.split()
            del line[:3]
            print(line)
            curPlayers.remove(line[0])

        #look for advancements
        elif "the advancement" in line and "<" not in line and ">" not in line:
            line = line.split()
            del line[:3]
            advancement = " ".join(str(x) for x in line)
            print(advancement)
            check = 1
            time.sleep(1)
            



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

@tasks.loop(seconds=1) #backround loop every 1 second
async def advance():
    global check
    global advancement
    channel = bot.get_channel(int(advChannel))
    if check == 1:

        #string editiing
        advancement = advancement.split()
        first = advancement[0]
        del advancement[:1]
        advancement = " ".join(str(x) for x in advancement)

        #embed setup
        embed = discord.Embed(title =':medal: New Advancement :medal:',color = discord.Color.from_rgb(241, 196, 15))
        embed.add_field(name= first, value="")
        embed.add_field(name= advancement, value = "", inline = True)

        await channel.send(embed=embed)

#start subprocess
subprocessThread = threading.Thread(target=serverSubprocess)
subprocessThread.start()

#run bot
bot.run(TOKEN)


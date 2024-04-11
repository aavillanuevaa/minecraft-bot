import os
import discord
import subprocess
import time

from discord.ext import commands
import subprocess
from dotenv import load_dotenv
import time
import threading

load_dotenv()


TOKEN = os.getenv('TESTTOKEN')
botChannel = 1216537851844366456
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

curPlayers = ""
ip = ""
version = ""
count = 0
 

def search(out):
    global version
    if "version" in out:
        version = out.split("version",1)[1]



def serverSubprocess():
    global version
    test = 0
    with subprocess.Popen(['startserver.bat'], stdout=subprocess.PIPE) as process:
        while process.poll() == None:
            output = process.stdout.read1().decode('utf-8')
            print(output)
            version = str(test)
            test+=1
            '''lines = output.split("\r\n")
            for line in lines:
                print(line)'''
            time.sleep(1)
    
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.CustomActivity(name='Server is Online'))
    channel =  bot.get_channel(1216537851844366456)
    await channel.send("@everyone Server is Online")

@bot.command()
async def server(ctx):
    if ctx.channel.id == botChannel:
        embed = discord.Embed(title=":green_circle:  Server Info", color = discord.Color.from_rgb(91,135,49))
        embed.add_field(name="Player Count :busts_in_silhouette:", value=str(count) + "/20", inline = True)
        embed.add_field(name="Version :hammer_and_wrench:", value= version, inline = True)
        embed.add_field(name="Server Adress :placard:", value= ip, inline = True)
        embed.add_field(name="Online Players:", value='\n'.join(curPlayers), inline = False)
        await ctx.send(embed=embed)

subprocessThread = threading.Thread(target=serverSubprocess)
subprocessThread.start()
bot.run(TOKEN)


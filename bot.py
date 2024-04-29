import os
import discord
import subprocess
import time
import atexit
import time
import threading
import asyncio

from collections import deque
from discord.ext import commands, tasks
from subprocess import CREATE_NEW_CONSOLE
from dotenv import load_dotenv
from requests import get

load_dotenv()

bot = None

class Bot:
    curPlayers = []
    version = ""
    playerCount = 0
    ip = ""
    advancement = ""
    chatlog = ""
    discordBot = None
    testing = 0
    # if deque: not empty
    # if not deque: is empty

    advQueue = deque() #empty -> if not queue --> True | add --> .append() | remove .popleft()
    msgQueue = deque()
    

    def __init__(self, testing=0):
        self.testing = testing

        #TOKEN SETUP
        tokens = ['TOKEN','STATUS','NOTIFY','ADV','ROLE', 'CHAT'] 
        packed_tokens = [os.getenv(token + "_TEST" if testing else token+"_PROD") for token in tokens] #packing tokens
        self.TOKEN, self.serverChannel, self.notifyChannel, self.advChannel, self.roleID, self.chatChannel= packed_tokens #unpacks tokens

        #starting bot
        self.discordBot = commands.Bot(command_prefix="/", intents=discord.Intents.all()) 
    
    def start(self):
        self.discordBot.run(self.TOKEN)

    def search(self, output):
        lines = output.split("\r\n")
        for line in lines:

            #checks for player chat 
            if len(line) < 1: continue

            if  ("<" in line and ">" in line and self.testing == 0):
                line = line.split()
                del line[:3]
                chat =  " ".join(str(x) for x in line)
                print(chat)
                self.msgQueue.append(chat)

            #look for version
            elif "version" in line:
                line = line.split()

                print(line)
                self.version = line[-1]
            
            #look for connection
            elif "joined the game" in line: 
                line = line.split()
                
                del line[:3]
                line =  " ".join(str(x) for x in line)

                print(line)
                self.playerCount += 1
                self.curPlayers.append(line[0])
                self.msgQueue.append(line)
            
            #look for disconnection
            elif "left the game" in line:
                line = line.split()
                
                del line[:3]
                line =  " ".join(str(x) for x in line)

                print(line)
                self.playerCount -= 1
                self.curPlayers.remove(line[0])
                self.msgQueue.append(line)

            #look for advancements
            elif "the advancement" in line: 
                advancement = line
                print(advancement)
                self.advQueue.append(advancement)


    ###### BACKROUND LOOPS ######
    @tasks.loop(seconds=1) 
    async def advance(self):
        if not self.advQueue: return #if its empty

        channel = self.discordBot.get_channel(int(self.advChannel))
    
        #string editiing
        while self.advQueue: #empty the queue 
            advancement = self.advQueue.popleft()
            advancement = advancement.split()
            del advancement[:3]
            first = advancement.pop(0)
            advancement = " ".join(str(x) for x in advancement)

            #embed setup
            embed = discord.Embed(title =':medal: New Advancement :medal:',color = discord.Color.from_rgb(241, 196, 15))
            embed.add_field(name= first, value="")
            embed.add_field(name= advancement, value = "", inline = True)

            await channel.send(embed=embed)

    @tasks.loop(seconds=1)
    async def chat(self):
        if not self.msgQueue: return

        channel = self.discordBot.get_channel(int(self.chatChannel))

        while self.msgQueue: #empty the queue 
            chatlog = self.msgQueue.popleft()

            #regular messages
            if ("<" in chatlog and ">" in chatlog):
                await channel.send(chatlog)
            else:#joined and leaving players
                if ("joined" in chatlog):
                    embed = discord.Embed(title ='',color = discord.Color.from_rgb(46, 204, 113))
                    embed.add_field(name= chatlog, value="")
                    await channel.send(embed=embed)
                else:
                    embed = discord.Embed(title ='',color = discord.Color.from_rgb(231, 76, 60))
                    embed.add_field(name= chatlog, value="")
                    await channel.send(embed=embed)



bot = Bot()


###### SUBPROCESS ######
def serverSubprocess():
    global bot
    with subprocess.Popen(['startserver.bat'], stdout=subprocess.PIPE) as process:
        while process.poll() == None:
            output = process.stdout.read1().decode('utf-8')
            
            if bot: bot.search(output) 
            time.sleep(1)

###### DISCORD STUFF ######
@bot.discordBot.event
async def on_ready():
    #global ip
    global bot
    await bot.discordBot.change_presence(activity=discord.CustomActivity(name='Server is Online'))
    channel =  bot.discordBot.get_channel(int(bot.notifyChannel))

    notification = discord.utils.get(channel.guild.roles, id=int(bot.roleID))
    embed = discord.Embed(title=":desktop: Server is Online :desktop:", color = discord.Color.from_rgb(91,135,49))
    embed.add_field(name="", value=f'{notification.mention}')
    await channel.send(embed=embed)

    bot.ip = get('https://api.ipify.org').content.decode('utf8')
    bot.advance.start()
    bot.chat.start()

@bot.discordBot.command()
async def server(ctx):
    if ctx.channel.id == int(bot.serverChannel):
        embed = discord.Embed(title=":green_circle:  Server Info", color = discord.Color.from_rgb(91,135,49))
        embed.add_field(name="Player Count :busts_in_silhouette:", value=str(bot.playerCount) + "/20", inline = True)
        embed.add_field(name="Version :hammer_and_wrench:", value= bot.version, inline = True)
        embed.add_field(name="Server Adress :placard:", value= bot.ip, inline = True)
        embed.add_field(name="Online Players:", value='\n'.join(bot.curPlayers), inline = False)
        await ctx.send(embed=embed)

@bot.discordBot.command()
async def notify(ctx):
    if ctx.channel.id == int(bot.serverChannel):
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

#start subprocess
subprocessThread = threading.Thread(target=serverSubprocess)
subprocessThread.start()

bot.start()


atexit.register(exit_handler)


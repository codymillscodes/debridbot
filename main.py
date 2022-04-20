import discord
from discord.ext import commands
import json
import requests
import os

# Get configuration.json
with open("configuration.json", "r") as config: 
	data = json.load(config)
	token = data["token"]
	prefix = data["prefix"]
	owner_id = data["owner_id"]


class Greetings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self._last_member = None

# Intents
intents = discord.Intents.default()
# The bot
bot = commands.Bot(command_prefix='$', intents = intents, owner_id = owner_id)

# Load cogs
if __name__ == '__main__':
	for filename in os.listdir("Cogs"):
		if filename.endswith(".py"):
			bot.load_extension(f"Cogs.{filename[:-3]}")

@bot.event
async def on_ready():
	print(f"We have logged in as {bot.user}")
	print(discord.__version__)
    print(bot.get_commands())
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name =f"{bot.command_prefix}help"))

bot.run(token)

"""
@bot.command(name='magnet', help='add magnet link')
async def addMagnet(ctx, arg):
    url = 'https://api.alldebrid.com/v4/magnet/upload?agent=' + DHOST + '&apikey=' + debrid_key + '&magnets[]=' + arg
    r = requests.get(url)
    
    t = json.loads(r.text)["data"]["magnets"]
    ident = str(t[0]["id"])
    response = ''
    
    if t[0]["ready"]:
        url = 'https://api.alldebrid.com/v4/magnet/status?agent=' + DHOST + '&apikey=' + debrid_key + '&id=' + ident
        r = requests.get(url)       
        t = json.loads(r.text)["data"]["magnets"]["links"]
        
        locked = str(t[0]["link"])
        url = 'https://api.alldebrid.com/v4/link/unlock?agent=' + DHOST + '&apikey=' + debrid_key + '&link=' + locked
        r = requests.get(url)       
        t = json.loads(r.text)["data"]
        
        embed = discord.Embed(title=t["filename"], description=t["link"])
        
        await ctx.send(embed=embed)
        # await ctx.send(str(t["filename"]))
        # await ctx.send(str(t["link"]))
    else:
        await ctx.send("hold up")
        
@bot.command(name='unlock', help='unlock link')
async def unlockLink(ctx, arg, arg2):
    url = 'https://api.alldebrid.com/v4/link/unlock?agent=' + DHOST + '&apikey=' + debrid_key + '&link=' + arg
    r = requests.get(url)
    
    t = json.loads(r.text)["data"]
    embed = discord.Embed(title=t["filename"], description=t["link"])
    
    await ctx.send(embed=embed)
@bot.command(name='saved', help='Responds with saved links')
async def getSavedLinks(ctx):
    url = 'https://api.alldebrid.com/v4/magnet/status?agent=' + DHOST + '&apikey=' + debrid_key
    r = requests.get(url)
    r.status_code
    response = ''
    
#cuts it down to the magnets part of the json
    links = json.loads(r.text)["data"]["magnets"]

#print filenames
#print(links[1]["filename"])
    for i, v in enumerate(links[:10]):
        temp = (i, v["filename"])
        response = response + '\n' + str(temp)
    await ctx.send(response)
bot.run(TOKEN)

# GET 'https://api.alldebrid.com/user/links?agent=' + 'DHOST' + '&apikey=' + 'debrid_key'
#https://api.alldebrid.com/v4/magnet/status?agent=Debridbot&apikey=qc778sk7AqUhB7xCVDgU

# links:
#   download 
#       delayed
#   stream

#magnets:
#   torrent search api
#       pick best torrent
#   status
#logs
#exceptions
#clean up """
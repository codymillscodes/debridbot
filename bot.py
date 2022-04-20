import os
import json
import requests
import discord
from dotenv import load_dotenv
from discord.ext.commands import Bot
from py1337x import py1337x

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEBRID = os.getenv('DEBRID_APIKEY')
DHOST = os.getenv('DEBRID_HOST')
torrents = py1337x(proxy='1337x.to', cache='cache', cacheTime=5000)
bot = Bot(command_prefix='$')

@bot.command(name='search', help='search 1337x')
async def search(ctx, arg):
    torrentResults = torrents.search(arg, sortBy='seeders', order='desc')
    await ctx.send(torrents.info(torrentId=torrentResults['items'][0]['torrentId'])['magnetLink'])
    

@bot.command(name='magnet', help='add magnet link')
async def addMagnet(ctx, arg):
    url = 'https://api.alldebrid.com/v4/magnet/upload?agent=' + DHOST + '&apikey=' + DEBRID + '&magnets[]=' + arg
    r = requests.get(url)
    
    t = json.loads(r.text)["data"]["magnets"]
    ident = str(t[0]["id"])
    response = ''
    
    if t[0]["ready"]:
        url = 'https://api.alldebrid.com/v4/magnet/status?agent=' + DHOST + '&apikey=' + DEBRID + '&id=' + ident
        r = requests.get(url)       
        t = json.loads(r.text)["data"]["magnets"]["links"]
        
        locked = str(t[0]["link"])
        url = 'https://api.alldebrid.com/v4/link/unlock?agent=' + DHOST + '&apikey=' + DEBRID + '&link=' + locked
        r = requests.get(url)       
        t = json.loads(r.text)["data"]
        
        embed = discord.Embed(title=t["filename"], description=t["link"])
        
        await ctx.send(embed=embed)
        # await ctx.send(str(t["filename"]))
        # await ctx.send(str(t["link"]))
    else:
        await ctx.send("hold up")

#cuts it down to the magnets part of the json
    links = json.loads(r.text)["data"]["magnets"]

#print filenames
#print(links[1]["filename"])
    for i, v in enumerate(links[:10]):
        temp = (i, v["filename"])
        response = response + '\n' + str(temp)
    await ctx.send(response)
bot.run(TOKEN)

# @bot.command(name='unlock', help='unlock link')
# async def unlockLink(ctx, arg, arg2):
#     url = 'https://api.alldebrid.com/v4/link/unlock?agent=' + DHOST + '&apikey=' + DEBRID + '&link=' + arg
#     r = requests.get(url)
    
#     t = json.loads(r.text)["data"]
#     embed = discord.Embed(title=t["filename"], description=t["link"])
    
#     await ctx.send(embed=embed)
# @bot.command(name='saved', help='Responds with saved links')
# async def getSavedLinks(ctx):
#     url = 'https://api.alldebrid.com/v4/magnet/status?agent=' + DHOST + '&apikey=' + DEBRID
#     r = requests.get(url)
#     r.status_code
#     response = ''

# GET 'https://api.alldebrid.com/user/links?agent=' + 'DHOST' + '&apikey=' + 'DEBRID'
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
#clean up
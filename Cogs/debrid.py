import discord
from discord.ext import commands
import json
import requests
import os
from py1337x import py1337x

with open("configuration.json", "r") as config: 
	data = json.load(config)
	debrid_key = data["debrid_key"]
	debrid_host = data["debrid_host"]

torrents = py1337x(proxy='1337x.to', cache='cache', cacheTime=5000)

class DebridCog(commands.Cog, name="debrid commands"):
    def __init__(self, bot:commands.Bot):
	    self.bot = bot

@commands.command(name='search', help='search 1337x')
async def search(ctx, arg):
    torrentResults = torrents.search(arg, sortBy='seeders', order='desc')
    await ctx.send(torrents.info(torrentId=torrentResults['items'][0]['torrentId'])['magnetLink'])


@commands.command(name='magnet', help='add magnet link')
async def addMagnet(self, ctx, arg):
    url = str("https://api.alldebrid.com/v4/magnet/upload?agent=" + debrid_host + '&apikey=' + debrid_key + '&magnets[]=' + arg)
    r = requests.get(url)
    t = json.loads(r.text)["data"]["magnets"]
    ident = str(t[0]["id"])

    if t[0]["ready"]:
        url = str('https://api.alldebrid.com/v4/magnet/status?agent=' + debrid_host + '&apikey=' + debrid_key + '&id=' + ident)
        r = requests.get(url)       
        t = json.loads(r.text)["data"]["magnets"]["links"]
        
        locked = str(t[0]["link"])
        url = str('https://api.alldebrid.com/v4/link/unlock?agent=' + debrid_host + '&apikey=' + debrid_key + '&link=' + locked)
        r = requests.get(url)       
        t = json.loads(r.text)["data"]
    
        embed = discord.Embed(title=t["filename"], description=t["link"])
        
        await ctx.send(embed=embed)
        # await ctx.send(str(t["filename"]))
        # await ctx.send(str(t["link"]))
    else:
        await ctx.send("hold up")

def setup(bot:commands.Bot):
	bot.add_cog(DebridCog(bot))
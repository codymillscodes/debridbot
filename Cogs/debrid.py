import json

import discord
import requests
from discord.ext import commands
from py1337x import py1337x

with open("configuration.json", "r") as config:
    data = json.load(config)
    debrid_key = data["debrid_key"]
    debrid_host = data["debrid_host"]

torrents = py1337x(proxy="1337x.to", cache="cache", cacheTime=5000)

class DebridCog(commands.Cog, name="debrid commands"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def addMagnet(ctx, magnet):
        url = str(
            "https://api.alldebrid.com/v4/magnet/upload?agent="
            + debrid_host
            + "&apikey="
            + debrid_key
            + "&magnets[]="
            + magnet
        )
        print("magnet added")
        return json.loads(requests.get(url).text)["data"]["magnets"]
#       add and return magnet link


    def unlockLink(ctx, link): 
        url = str(
            "https://api.alldebrid.com/v4/link/unlock?agent="
            + debrid_host
            + "&apikey="
            + debrid_key
            + "&link="
            + link
        )
        print("unlocking")
        return json.loads(requests.get(url).text)["data"]["link"]

    def getMagnetId(ctx, magnet):
        return str(magnet[0]["id"])

    def getUnhostedLink(ctx, magnetId):
        url = str(
                "https://api.alldebrid.com/v4/magnet/status?agent="
                + debrid_host
                + "&apikey="
                + debrid_key
                + "&id="
                + magnetId
        )
        print("got unhosted link")
        t = json.loads(requests.get(url).text)["data"]["magnets"]["links"][0]["link"]
        print(t)
        return t

    def magnetStatus(ctx, magnetId):
        url = str(
                "https://api.alldebrid.com/v4/magnet/status?agent="
                + debrid_host
                + "&apikey="
                + debrid_key
                + "&id="
                + magnetId
        )
        ready = json.loads(requests.get(url).text)["data"]["magnets"]["status"]
        print(ready)
        if ready == "Ready":
            return True
        else:
            return False

    @commands.command(name="search", help="search 1337x")
    async def search(self, ctx, arg):
        print("search: " + ctx.message.content[8:])
        magnetLink = torrents.info(
            torrentId=torrents.search(
                arg, sortBy="seeders", order="desc"
                )['items'][0]['torrentId']
                )['magnetLink']
        
        print("Magnet sent")
        id = self.getMagnetId(self.addMagnet(magnetLink))
        print(id)
        if self.magnetStatus(id):
            link = self.unlockLink(self.getUnhostedLink(id))
        else:
            print("uhhhhhh")

        #embed = discord.Embed(title=t["filename"], description=t["link"])
        print("Link sent")
        #await ctx.send(embed=embed)
        # await ctx.send(str(t["filename"]))
        await ctx.send(link)

#    @commands.command(name="magnet", help="add magnet link")
#    async def addMagnet(self, ctx, arg)

def setup(bot: commands.Bot):
    bot.add_cog(DebridCog(bot))

import json
import datetime
import discord
import requests
import asyncio
from hurry.filesize import size
from discord.ext import commands
from py1337x import py1337x

with open("configuration.json", "r") as config:
    data = json.load(config)
    debrid_key = data["debrid_key"]
    debrid_host = data["debrid_host"]

torrents = py1337x(proxy="1337x.to", cache="cache", cacheTime=5000)

def debridURL(domain, action, arg):
    return str(f"https://api.alldebrid.com/v4/{domain}/{action}?agent={debrid_host}&apikey={debrid_key}&{arg}")

class DebridCog(commands.Cog, name="debrid commands"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def addMagnet(ctx, magnet):
        url = debridURL("magnet", "upload", "magnets[]=") + magnet
        print("magnet added")
        return json.loads(requests.get(url).text)

    def unlockLink(ctx, link): 
        url = debridURL("link", "unlock", "link=") + link
        print("unlocking")
        return json.loads(requests.get(url).text)["data"]

    def getMagnetId(ctx, magnet):
        print(magnet)
        return str(magnet['data']['magnets'][0]["id"])

    def getFilename(ctx, magnetId):
        url = debridURL("magnet", "status", "id=") + magnetId
        t = json.loads(requests.get(url).text)['data']['magnets']['filename']
        print(t)
        return t

    def getSize(ctx, magnetId):
        url = debridURL("magnet", "status", "id=") + magnetId
        t = json.loads(requests.get(url).text)['data']['magnets']['size']
        print(size(t))
        return size(t)

    def getUnhostedLinks(ctx, magnetId):
        url = debridURL("magnet", "status", "id=") + magnetId
        print("got unhosted link")
        t = json.loads(requests.get(url).text)["data"]["magnets"]["links"]
        print(t)
        return t

    def buildLinkInfo(ctx, magnetID):
        link = DebridCog.getUnhostedLinks(ctx = ctx, magnetId = magnetID)
        linkInfo = []
        for link in link:
            l = DebridCog.unlockLink(ctx = ctx, link = link["link"])
            linkInfo.append({'name':link["filename"], 'link':l["link"], 'size':int(link["size"])})
        print(linkInfo)
        return linkInfo

    def magnetStatus(ctx, magnetId):
        url = debridURL("magnet", "status", "id=") + magnetId
        ready = json.loads(requests.get(url).text)["data"]["magnets"]["status"]
        print(ready)
        if ready == "Ready":
            return True
        else:
            return False

    def search1337(ctx, query):
        return torrents.search(query, sortBy='seeders', order='desc')

    @commands.command(name = "status", help = "check status of active downloads")
    async def status(self, ctx, status='active'): #$apiEndpointOnlyActive = "https://api.alldebrid.com/v4/magnet/status?agent=myAppName&apikey=someValidApikeyYouGenerated&status=active";
        url = debridURL('magnet', 'status', f'status={status}')
        print(url)
        activeStatus = json.loads(requests.get(url).text)['data']
        print(activeStatus)
        x=0
        statusEmbed = discord.Embed()
        statusEmbed.set_footer(text = str(ctx.message.author) + " | " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        statusEmbed.set_author(name="Active Torrents")
        for torrent in activeStatus["magnets"]:
            x = x+1
            statusEmbed.add_field(name=torrent['filename'], value=f"{('{0:.2f}'.format(100 * torrent['downloaded'] / torrent['size']) or 0)}% {torrent['status']} | Size: {size(torrent['size'])} | Speed: {size(torrent['downloadSpeed'])} | Seeders: {torrent['seeders']}")
            if x == 10:
                break
        await ctx.send(embed=statusEmbed)

    @commands.command(name="search", help="search 1337x")
    async def search(self, ctx, arg, pick = None):
        resultEmbed = discord.Embed()
        resultEmbed.set_footer(text = str(ctx.message.author) + " | " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        x = 0
        print("starting search")
        results = self.search1337(ctx.message.content[8:])
        print("building embed")
        for torrent in results["items"]:
            x = x + 1
            resultEmbed.add_field(name = f"{x}. {torrent['name']}", value = f"Seeders: {torrent['seeders']} | Leechers: {torrent['leechers']} | Size: {torrent['size']}", inline = False)
            if x == 5:
                break
        resultEmbed.add_field(name = "----------------", value = "You should pick the one with the most seeder and reasonable filesize. Pay attention to the quality. You dont want a cam or TS.\n*$pick 1-5*", inline = False)
        await ctx.send(embed = resultEmbed)
        def check(m):
            return m.author == ctx.author and m.content.startswith('$pick')
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=600)
            print(msg.content)
            print(msg.content[6:])
            pick = int(msg.content[6:]) - 1
            if int(msg.content[6:]) > x:
                await ctx.send("WRONG")
            else:
                magnetLink = torrents.info(torrentId=results["items"][pick]['torrentId'])['magnetLink']
                print(magnetLink)
                id = self.getMagnetId(self.addMagnet(magnetLink))
                print(f"magnet added. id: {id}")
                if self.magnetStatus(id):
                    filez = self.buildLinkInfo(id)
                    linkEmbed = discord.Embed()
                    linkEmbed.set_author(name = self.getFilename(id))
                    linkEmbed.set_footer(text = f"{str(ctx.message.author)} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("set footer")
                    for info in filez:
                        print(f"{info['name']}  {info['link']}  {size(info['size'])}")
                        linkEmbed.add_field(name = info["name"], value = f"{info['link']} | size: {size(info['size'])}", inline = False)
                    await ctx.send(embed=linkEmbed)
                else:
                    print("shits not ready")
                    link = "PENDING"

                
        except asyncio.TimeoutError:
            await ctx.send("TOO SLOW")

def setup(bot: commands.Bot):
    bot.add_cog(DebridCog(bot))

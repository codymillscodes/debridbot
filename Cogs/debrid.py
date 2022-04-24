import json
import datetime
import discord
import requests
import asyncio
from hurry.filesize import size
from discord.ext import commands
from py1337x import py1337x
import logging as log

log.basicConfig(filename='debrid-debug.log', encoding='utf-8', level=log.DEBUG)

with open("configuration.json", "r") as config:
    data = json.load(config)
    debrid_key = data["debrid_key"]
    debrid_host = data["debrid_host"]

torrents = py1337x(proxy="1337x.to", cache="cache", cacheTime=5000)

def debridURL(domain, action, arg):
    log(f"[debridURL]:Serving Debrid URL. vars: {domain} {action} {arg}")
    return str(f"https://api.alldebrid.com/v4/{domain}/{action}?agent={debrid_host}&apikey={debrid_key}&{arg}")

class DebridCog(commands.Cog, name="debrid commands"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot #771867774087725146/ 967698346959568926

    def addMagnet(ctx, magnet):
        url = debridURL("magnet", "upload", "magnets[]=") + magnet
        log(f"[addMagnet]Adding magnet: {magnet}")
        log(f"[addMagnet]Context: {ctx}")
        j = json.loads(requests.get(url).text)
        log(f"[addMagnet]JSON: {j}")
        return j

    def unlockLink(ctx, link): 
        url = debridURL("link", "unlock", "link=") + link
        log(f"[unlockLink]Unlocking link: {link}")
        j = json.loads(requests.get(url).text)["data"]
        log(f"[unlockLink]JSON: {j}")
        return j


    def getMagnetId(ctx, magnet):
        id = str(magnet['data']['magnets'][0]["id"])
        log(f"[getMagnetID]Got magnet ID: {str(id)}")
        return id

    def getFilename(ctx, magnetId):
        url = debridURL("magnet", "status", "id=") + magnetId
        t = json.loads(requests.get(url).text)['data']['magnets']['filename']
        log(f"[getFilename]Retrieving filename for {magnetId}: {t}")
        return t

    def getUnhostedLinks(ctx, magnetId):
        url = debridURL("magnet", "status", "id=") + magnetId
        t = json.loads(requests.get(url).text)["data"]["magnets"]["links"]
        log(f"[getUnhostedLinks]Got link for {magnetId}")
        log(f"[getUnhostedLink]JSON: {t}")
        return t

    def buildLinkInfo(ctx, magnetID):
        link = DebridCog.getUnhostedLinks(ctx = ctx, magnetId = magnetID)
        linkInfo = []
        log(f"[buildLinkinfo]Building link Embed for {magnetID}")
        log(f"[buildLinkinfo]buildLinkInfo received context: {ctx}")
        for link in link:
            l = DebridCog.unlockLink(ctx = ctx, link = link["link"])
            log("[buildLinkinfo]Unlocked JSON: "+str(l))
            linkInfo.append({'name':link["filename"], 'link':l["link"], 'size':int(link["size"])})
        log('[buildLinkinfo]'+str(linkInfo))
        return linkInfo

    def magnetStatus(ctx, magnetId):
        url = debridURL("magnet", "status", "id=") + magnetId
        ready = json.loads(requests.get(url).text)["data"]["magnets"]["status"]
        log(f"[magnetStatus]Checking status for {magnetId}")
        log(f"[magnetStatus]{magnetId} ready flag: {ready}")
        if ready == "Ready":
            return True
        else:
            return False

    def search1337(ctx, query):
        log(f"[search1337]Searching 1337x for {query}")
        results = torrents.search(query, sortBy='seeders', order='desc')
        log(f"[search1337]Results: {results}")
        return results

    @commands.command(name = "status", help = "check status of active downloads")
    async def status(self, ctx, status='active'): #$apiEndpointOnlyActive = "https://api.alldebrid.com/v4/magnet/status?agent=myAppName&apikey=someValidApikeyYouGenerated&status=active";
        log(f"[command.status]Status invoked by {ctx.message.author}")
        log(f"[command.status]Context obj: {ctx}")
        url = debridURL('magnet', 'status', f'status={status}')
        log(f"[command.status]Status URL: {url}")
        activeStatus = json.loads(requests.get(url).text)['data']
        log(f"[command.status]Status JSON: {activeStatus}")
        x=0
        statusEmbed = discord.Embed()
        statusEmbed.set_footer(text = str(ctx.message.author) + " | " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        statusEmbed.set_author(name="Active Torrents")
        for torrent in activeStatus["magnets"]:
            x = x+1
            statusFieldName = torrent['filename']
            statusFieldValue = f"{('{0:.2f}'.format(100 * torrent['downloaded'] / torrent['size']) or 0)}% {torrent['status']} | Size: {size(torrent['size'])} | Speed: {size(torrent['downloadSpeed'])} | Seeders: {torrent['seeders']}"
            log(f"[command.status]File: {statusFieldName}")
            log(f"[command.status]Info: {statusFieldValue}")
            statusEmbed.add_field(name=statusFieldName, value=statusFieldValue, inline=False)
            log("[command.status]statusEmbed field added.")
            if x == 10:
                log("[command.status]statusEmbed loop broken.")
                break
        await ctx.send(embed=statusEmbed)

    @commands.command(name="search", help="search 1337x")
    async def search(self, ctx, arg):
        log(f"[command.search]{ctx.message.content}:Search invoked by {ctx.author.id}")
        log("[command.search]Searching for "+ctx.message.content[8:])
        #log(pick + " picked.")
        log("[command.search]Context obj: " + str(ctx))
        resultEmbed = discord.Embed()
        resultEmbed.set_footer(text = str(ctx.message.author) + " | " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        x = 0
        log("[command.search]Starting search.")
        results = self.search1337(ctx.message.content[8:])
        log("[command.search]Building resultEmbed.")
        for torrent in results["items"]:
            x = x + 1
            resultEmbedName = torrent['name']
            resultEmbedValue = f"Seeders: {torrent['seeders']} | Leechers: {torrent['leechers']} | Size: {torrent['size']}"
            log(f"[command.search]File: {resultEmbedName}")
            log("[command.search]"+resultEmbedValue)
            resultEmbed.add_field(name = f"{x}. {resultEmbedName}", value = resultEmbedValue, inline = False)
            log("[command.search]resultEmbed field added.")
            if x == 5:
                log("[command.search]resultEmbed loop broken.")
                break
        resultEmbed.add_field(name = "----------------", value = "You should pick the one with the most seeder and reasonable filesize. Pay attention to the quality. You dont want a cam or TS.\n*$pick 1-5*", inline = False)
        await ctx.send(embed = resultEmbed)
        log("[command.search]resultEmbed sent.")
        def check(m):
            return m.author == ctx.author and m.content.startswith('$pick')
        try:
            log("[command.search]Waiting for $pick")
            msg = await self.bot.wait_for('message', check=check, timeout=600)
            log(f"[{msg.content}] {int(msg.content[6:]) - 1} picked.")
            pick = int(msg.content[6:]) - 1
            if int(msg.content[6:]) > x:
                log("[command.search]Result chosen out of bounds.")
                await ctx.send("WRONG")
            else:
                log("[command.search]Getting magnet info.")
                magnetLink = torrents.info(torrentId=results["items"][pick]['torrentId'])['magnetLink']
                id = self.getMagnetId(self.addMagnet(magnetLink))
                log(f"[command.search]Got ID: {id} for {magnetLink}")
                if self.magnetStatus(id):
                    log("[command.search]Got the OK to build linkEmbed.")
                    filez = self.buildLinkInfo(id)
                    linkEmbed = discord.Embed()
                    linkEmbed.set_author(name = self.getFilename(id))
                    linkEmbed.set_footer(text = f"{str(ctx.message.author)} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    for info in filez:
                        log(f"{info['name']}  {info['link']}  {size(info['size'])}")
                        linkEmbed.add_field(name = info["name"], value = f"{info['link']} | size: {size(info['size'])}", inline = False)
                    await ctx.send(embed=linkEmbed)
                    log("[command.search]linkEmbed sent.")
                else:
                    log("[command.search]Torrent not ready.")
                    await ctx.send(f"The torrent isn't ready. \n*Likely because it needs to be downloaded. Try again in a few minutes. I'm working making on this bit easier.*")

                
        except asyncio.TimeoutError:
            log("[command.search]$pick timed out.")
            await ctx.send("TOO SLOW")


def setup(bot: commands.Bot):
    bot.add_cog(DebridCog(bot))
    

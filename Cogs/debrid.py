import json
import datetime
import time
import discord
import requests
import asyncio
from hurry.filesize import size
from discord.ext import commands
from py1337x import py1337x
#import logging as log

#log.basicConfig(filename='debrid-debug.log', encoding='utf-8', level=log.DEBUG)

with open("configuration.json", "r") as config:
    data = json.load(config)
    debrid_key = data["debrid_key"]
    debrid_host = data["debrid_host"]

torrents = py1337x(proxy="1337x.to", cache="cache", cacheTime=5000)

def debridURL(domain, action, arg):
    #log.info(f"[debridURL]:Serving Debrid URL. vars: {domain} {action} {arg}")
    return str(f"https://api.alldebrid.com/v4/{domain}/{action}?agent={debrid_host}&apikey={debrid_key}&{arg}")

class DebridCog(commands.Cog, name="debrid commands"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot #771867774087725146/ 967698346959568926
        self.log_channel = None
        self.logged = 0
        self.logFile = ''
        self.notReady = []

    def addMagnet(ctx, magnet):
        url = debridURL("magnet", "upload", "magnets[]=") + magnet
        #log.info(f"[addMagnet]Adding magnet: {magnet}")
        #log.debug(f"[addMagnet]Context: {ctx}")
        j = json.loads(requests.get(url).text)
        #log.debug(f"[addMagnet]JSON: {j}")
        return j

    def unlockLink(ctx, link): 
        url = debridURL("link", "unlock", "link=") + link
        #log.info(f"[unlockLink]Unlocking link: {link}")
        j = json.loads(requests.get(url).text)["data"]
        #log.debug(f"[unlockLink]JSON: {j}")
        return j


    def getmagnetID(ctx, magnet):
        id = str(magnet['data']['magnets'][0]["id"])
        #log.info(f"[getmagnetID]Got magnet ID: {str(id)}")
        return id

    def getFilename(ctx, magnetID):
        url = debridURL("magnet", "status", "id=") + magnetID
        t = json.loads(requests.get(url).text)['data']['magnets']['filename']
        #log.info(f"[getFilename]Retrieving filename for {magnetID}: {t}")
        return t

    def getUnhostedLinks(ctx, magnetID):
        url = debridURL("magnet", "status", "id=") + magnetID
        t = json.loads(requests.get(url).text)["data"]["magnets"]["links"]
        #log.info(f"[getUnhostedLinks]Got link for {magnetID}")
        #log.debug(f"[getUnhostedLink]JSON: {t}")
        return t

    def buildLinkInfo(ctx, magnetID):
        link = DebridCog.getUnhostedLinks(ctx = ctx, magnetID = magnetID)
        linkInfo = []
        #log.info(f"[buildLinkinfo]Building link Embed for {magnetID}")
        #log.info(f"[buildLinkinfo]buildLinkInfo received context: {ctx}")
        for link in link:
            l = DebridCog.unlockLink(ctx = ctx, link = link["link"])
            #log.debug("[buildLinkinfo]Unlocked JSON: "+str(l))
            linkInfo.append({'name':link["filename"], 'link':l["link"], 'size':int(link["size"])})
        #log.debug('[buildLinkinfo]'+str(linkInfo))
        return linkInfo

    def magnetStatus(ctx, magnetID):
        url = debridURL("magnet", "status", "id=") + magnetID
        ready = json.loads(requests.get(url).text)["data"]["magnets"]["status"]
        #log.info(f"[magnetStatus]Checking status for {magnetID}")
        #log.info(f"[magnetStatus]{magnetID} ready flag: {ready}")
        if ready == "Ready":
            return True
        else:
            return False

    def search1337(ctx, query):
        #log(f"[search1337]Searching 1337x for {query}")
        results = torrents.search(query, sortBy='seeders', order='desc')
        #log.info(f"[search1337]Results: {results}")
        return results

    async def addNotReady(self, ctx, magnetID):
        self.notReady.insert(0, magnetID)
        await self.log(f"Added {magnetID} to notReady[]", True)
        #self.log(f"Added {id}to notReady list.")

    async def checkReady(self, ctx):
        await self.log("checking ready")
        while len(self.notReady) <= 0:
            await self.log("hey theres some shit in notReady[]", True)
            for id in self.notReady:
                time.sleep(.5)
                await self.log("Checking not ready")
                if asyncio.create_task(self.magnetStatus(id)):
                    filez = self.buildLinkInfo(id)
                    linkEmbed = discord.Embed(title='', description=f"{ctx.author.mention}")
                    #linkEmbed.set_author(name = self.getFilename(id))
                    linkEmbed.set_footer(text = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    dl_channel = ctx.guild.get_channel(967969069108179044)
                    for info in filez:
                        await self.log(f"{info['name']}  {info['link']}  {size(info['size'])}")
                        linkEmbed.add_field(name = info["name"], value = f"{info['link']} | size: {size(info['size'])}", inline = False)
                    asyncio.create_task(dl_channel.send(embed=linkEmbed))
                    self.notReady.remove(id)



    @commands.command(name = 'log')
    async def log(self, l, now = False):
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #logEmbed = discord.Embed()
        #logEmbed.add_field()
        self.logFile = f"{self.logFile} [{time}]:{l}\n"
        if self.logged >=5 or now == True:
            self.logged = 0
            asyncio.create_task(self.log_channel.send(f"```{self.logFile}```"))
            self.logFile = ''
        else:
            self.logged = self.logged + 1

    @commands.command(name='start', help = 'set start vars')
    async def start(self, ctx):
        self.log_channel = ctx.guild.get_channel(967698346959568926)
        await self.log('Start command', now = True)
        
    @commands.command(name = "status", help = "check status of active downloads")
    async def status(self, ctx, status='active'): #$apiEndpointOnlyActive = "https://api.alldebrid.com/v4/magnet/status?agent=myAppName&apikey=someValidApikeyYouGenerated&status=active";
        await self.log(f"[command.status]Status invoked by {ctx.message.author}")
        await self.log(f"[command.status]Context obj: {ctx}")
        url = debridURL('magnet', 'status', f'status={status}')
        await self.log(f"[command.status]Status URL: {url}")
        activeStatus = json.loads(requests.get(url).text)['data']
        await self.log(f"[command.status]Status JSON: {activeStatus}")
        x=0
        statusEmbed = discord.Embed()
        statusEmbed.set_footer(text = str(ctx.message.author) + " | " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        statusEmbed.set_author(name="Active Torrents")
        for torrent in activeStatus["magnets"]:
            x = x+1
            statusFieldName = torrent['filename']
            statusFieldValue = f"{('{0:.2f}'.format(100 * torrent['downloaded'] / torrent['size']) or 0)}% | {torrent['status']} | Size: {size(torrent['size'])} | Speed: {size(torrent['downloadSpeed'])} | Seeders: {torrent['seeders']}"
            await self.log(f"[command.status]File: {statusFieldName}")
            await self.log(f"[command.status]Info: {statusFieldValue}")
            statusEmbed.add_field(name=statusFieldName, value=statusFieldValue, inline=False)
            await self.log("[command.status]statusEmbed field added.")
            if x == 10:
                await self.log("[command.status]statusEmbed loop broken.")
                break
        await ctx.send(embed=statusEmbed)

    @commands.command(name="search", help="search 1337x")
    async def search(self, ctx, arg):
        await self.log(f"[command.search]{ctx.message.content}:Search invoked by {ctx.author.id}")
        await self.log("[command.search]Searching for "+ctx.message.content[8:])
        #log(pick + " picked.")
        await self.log("[command.search]Context obj: " + str(ctx))
        resultEmbed = discord.Embed()
        resultEmbed.set_footer(text = str(ctx.message.author) + " | " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        x = 0
        await self.log("[command.search]Starting search.")
        results = self.search1337(ctx.message.content[8:])
        await self.log("[command.search]Building resultEmbed.")
        for torrent in results["items"]:
            x = x + 1
            resultEmbedName = torrent['name']
            resultEmbedValue = f"Seeders: {torrent['seeders']} | Leechers: {torrent['leechers']} | Size: {torrent['size']}"
            await self.log(f"[command.search]File: {resultEmbedName}")
            await self.log("[command.search]"+resultEmbedValue)
            resultEmbed.add_field(name = f"{x}. {resultEmbedName}", value = resultEmbedValue, inline = False)
            await self.log("[command.search]resultEmbed field added.")
            if x == 5:
                await self.log("[command.search]resultEmbed loop broken.")
                break
        resultEmbed.add_field(name = "----------------", value = "You should pick the one with the most seeder and reasonable filesize. Pay attention to the quality. You dont want a cam or TS.\n*$pick 1-5*", inline = False)
        await ctx.send(embed = resultEmbed)
        await self.log("[command.search]resultEmbed sent.")
        def check(m):
            return m.author == ctx.author and m.content.startswith('$pick')
        try:
            await self.log("[command.search]Waiting for $pick")
            msg = await self.bot.wait_for('message', check=check, timeout=600)
            await self.log(f"[{msg.content}] {int(msg.content[6:]) - 1} picked.")
            pick = int(msg.content[6:]) - 1
            if int(msg.content[6:]) > x:
                await self.log("[command.search]Result chosen out of bounds.")
                await ctx.send("WRONG")
            else:
                await self.log("[command.search]Getting magnet info.")
                magnetLink = torrents.info(torrentId=results["items"][pick]['torrentId'])['magnetLink']
                id = self.getmagnetID(self.addMagnet(magnetLink))
                await self.log(f"[command.search]Got ID: {id} for {magnetLink}")
                if self.magnetStatus(id):
                    await self.log("[command.search]Got the OK to build linkEmbed.")
                    filez = self.buildLinkInfo(id)
                    linkEmbed = discord.Embed(title='', description=f"{ctx.author.mention}")
                    #linkEmbed.set_author(name = self.getFilename(id))
                    linkEmbed.set_footer(text = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    dl_channel = ctx.guild.get_channel(967969069108179044)
                    for info in filez:
                        await self.log(f"{info['name']}  {info['link']}  {size(info['size'])}")
                        linkEmbed.add_field(name = info["name"], value = f"{info['link']} | size: {size(info['size'])}", inline = False)
                    await dl_channel.send(embed=linkEmbed)
                    await self.log("[command.search]linkEmbed sent.")
                else:
                    await self.addNotReady(ctx=ctx, magnetID=id)
                    asyncio.create_task(self.checkReady(ctx=ctx))
                    await self.log("[command.search]Torrent not ready.")
                    await ctx.send(f"The torrent isn't ready. \n*Likely because it needs to be downloaded. Try again in a few minutes. I'm working on making on this bit easier.*")

                
        except asyncio.TimeoutError:
            await self.log("[command.search]$pick timed out.")
            await ctx.send("TOO SLOW")


def setup(bot: commands.Bot):
    bot.add_cog(DebridCog(bot))
    

import discord
from discord.ext import commands
import time

class LogCog(commands.Cog, name="log"):
	def __init__(self, bot:commands.bot):
		self.bot = bot
	
    @commands.command(name = 'log')
    async def log(ctx, msg):
        log_channel = ctx.get_channel(967698346959568926)
        await log_channel.send(msg)

def setup(bot:commands.Bot):
	bot.add_cog(LogCog(bot))
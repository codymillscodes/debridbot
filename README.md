# debridbot

todo:
history
status

@client.command()
async def examplecommand(ctx):
    await message.channel.send("Example Question?")
    
    def check(msg):
        return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id

    answermsg = await client.wait_for('message', check = check)

    if "yes" in answermsg.content.lower() or "no" in answermsg.content.lower():
        await ctx.send("example answer")

    else:
        await ctx.send("Invalid response")


        quotient = 3 / 5

percent = quotient * 100

print(percent)


100 * float(part)/float(whole)
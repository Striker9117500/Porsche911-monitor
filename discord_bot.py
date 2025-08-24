import discord, os, json
from scraper import run_scraper

intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

@bot.slash_command(name="latest", description="Show latest Porsche 911 listings")
async def latest(ctx):
    cars = run_scraper()
    if not cars:
        await ctx.respond("No cars found right now.")
    else:
        msg = "\n".join([f"{c['year']} {c['title']} - ${c['price']} ({c['url']})" for c in cars])
        await ctx.respond(msg)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))

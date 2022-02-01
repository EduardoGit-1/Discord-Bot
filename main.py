import discord
import music
from discord.ext import commands
from dotenv import load_dotenv
import os

cogs = [music]
bot = commands.Bot(command_prefix='!')
intents = discord.Intents.all()

for cog in cogs:
    cog.setup(bot)

load_dotenv()
token = os.getenv('TOKEN')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def join(ctx):
    try:
        voice_channel = ctx.author.voice.channel 
    except:
        voice_channel = None

    if voice_channel is None:
        await ctx.send("You're not in a voice channel.")
    
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)


@bot.command()
async def test(ctx):
    await ctx.send("test")


bot.run(token)
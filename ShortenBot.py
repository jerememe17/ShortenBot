import discord
from discord.ext import commands
import youtube_dl
import random
import os

TOKEN = ''

bot = commands.Bot(command_prefix='!')

players = {}

async def choose_soundbite(polly):
    clip_list = os.listdir('{}/{}'.format(os.getcwd(), polly))
    clip_choice = random.choice(clip_list)
    return clip_choice

async def play_soundbite(ctx, polly):
    channel = ctx.message.author.voice.voice_channel
    try:
        await bot.join_voice_channel(channel)
    except discord.errors.InvalidArgument:
        await bot.send_message(ctx.message.channel, 'You must be in a voice channel to do this.')
    except discord.errors.ClientException:
        await bot.send_message(ctx.message.channel, 'ShortenBot is already playing in the channel!')
    else:
        server = ctx.message.server
        voice_client = bot.voice_client_in(server)
        clip = await choose_soundbite(polly)
        player = voice_client.create_ffmpeg_player('{}/{}'.format(polly, clip))
        players[server.id] = player
        player.start()
        while (player.is_done() == False):
            continue
        await voice_client.disconnect()

@bot.event
async def on_ready():
   print(bot.user.name + ' running')

@bot.command(pass_context=True)
async def shorten(ctx):
    await play_soundbite(ctx, 'Shorten')

@bot.command(pass_context=True)
async def advise(ctx):
    helpcmd = discord.Embed(
        colour = discord.Colour.red()
    )

    helpcmd.set_author(name = 'Bill Shorten Help Commands')

    helpcmd.add_field(name = '!shorten', value = 'Plays a juicy soundbite from Bill Shorten', inline=False)
    helpcmd.add_field(name = '!spill', value = 'Bill Shorten will bugger off', inline=False)
    helpcmd.add_field(name = '!advise', value = 'Bill Shorten tells you how to work him')

    await bot.say(embed = helpcmd)

@bot.command(pass_context=True)
async def spill(ctx):
    try:
        server = ctx.message.server
        voice_client = bot.voice_client_in(server)
        await voice_client.disconnect()
    except AttributeError:
        await bot.send_message(ctx.message.channel, 'Bill Shorten is not in a channel!')

bot.run(TOKEN)

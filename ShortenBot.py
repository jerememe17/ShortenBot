import discord
from discord.ext import commands
import random, os, time, asyncio, configparser

# polly = politician

TOKEN = 'NDgyMTM4MzI2MzUxMDg1NTY5.XSWsFQ.z--IE5TQpmBqVV0lEc1NyfY6gPk'

bot = discord.Client()

def get_valid_commands():
    result = []
    for file in os.listdir():
        if os.path.isdir(file): # get dir
            if not file.startswith('.'): # ignore hidden dir
                if not file == "env": # ignore environment
                    result.append(file)

def get_name_from_config(politician):
    config = configparser.ConfigParser()
    config.read(politician + '/about.cfg')

async def join_voice_channel(message):
    '''
    Joins the voice channel that the caller is currently in
    '''
    v_caller = message.author.voice
    if v_caller == None:
        raise discord.errors.InvalidArgument
    v_channel = v_caller.channel
    return await v_channel.connect()

async def choose_soundbite(polly):
    '''
    Select a random soundbite to play
    '''
    clip_list = os.listdir('{}/{}'.format(os.getcwd(), polly))
    clip_list.remove('about.cfg')
    clip_choice = random.choice(clip_list)
    return clip_choice

async def play_soundbite(message, polly):
    '''
    Play the random soundbite
    '''
    try:
        v_client = await join_voice_channel(message)
    except discord.errors.InvalidArgument:
        await message.channel.send('You must be in a voice channel to do this.')
    except discord.errors.ClientException:
        await message.channel.send('ShortenBot is already playing in the channel!')
    else:
        clip = await choose_soundbite(polly)
        audio = discord.FFmpegPCMAudio('{}/{}'.format(polly, clip))

        # define the callback function for leaving the channel
        def leave_voice_channel(error):
            '''
            Leave the voice channel
            '''
            coro = v_client.disconnect(force=True)
            fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
            try:
                fut.result()
            except:
                pass
        
        v_client.play(audio, after=leave_voice_channel)

@bot.event
async def on_ready():
    '''
    Inform server that bot is ready
    '''
    print(bot.user.name + ' running')

@bot.event
async def on_message(message):
    '''
    Handle messages
    '''
    if message.content.startswith('!advise'):
        await advise(message)
    elif message.content.startswith('!spill'):
        await spill(message)
    elif message.content.startswith('!shorten'):
        await shorten(message)

async def shorten(message):
    '''
    Play a Bill Shorten soundbite
    '''
    await play_soundbite(message, 'shorten')

async def advise(message):
    '''
    Help menu for the bot
    '''
    text_channel = message.channel
    helpcmd = discord.Embed(
        colour = discord.Colour.red()
    )

    helpcmd.set_author(name = 'Bill Shorten Help Commands')

    #for politician in get_valid_commands():
        
    helpcmd.add_field(name = '!shorten', value = 'Plays a juicy soundbite from Bill Shorten', inline=False)
    helpcmd.add_field(name = '!spill', value = 'Bill Shorten will bugger off', inline=False)
    helpcmd.add_field(name = '!advise', value = 'Bill Shorten tells you how to work him')

    await text_channel.send(embed = helpcmd)

async def spill(message):
    '''
    Force the bot to leave the voice channel
    '''
    text_channel = message.channel
    voice_channel = message.author.voice.channel
    client = discord.utils.get(bot.voice_clients)
    if len(bot.voice_clients) == 0:
        await text_channel.send('Bill Shorten is not in a channel!')
    elif client.channel.id == voice_channel.id:
        await client.disconnect()

bot.run(TOKEN)

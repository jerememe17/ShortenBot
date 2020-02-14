import discord
import random, os, time, asyncio, configparser

# polly = politician

TOKEN = os.environ.get('DISCORD_TOKEN')

bot = discord.Client()
perms = discord.Permissions(70256640)

def get_valid_commands():
    '''
    Get the valid politician command names
    '''
    result = []
    for dir in os.listdir('politicians'):
        if os.path.isdir(os.getcwd() + '/politicians/' + dir): # get dir
            result.append(dir)
    return result

def parse_config(politician):
    config = configparser.ConfigParser()
    config.read('politicians/' + politician + '/about.cfg')
    return config

def get_name_from_config(config):
    '''
    Get the name of the politician from their config file
    '''
    #print (config.sections())
    return config['INFO']['NAME']

def get_party_from_config(config):
    '''
    Get the politician's party from their config file
    '''
    return config['INFO']['PARTY']

def get_role_from_config(config):
    '''
    Get the politician's role from their config file
    '''
    return config['INFO']['POSITION']

def get_avatar(polly):
    return 'politicians/{}/avatar.jpeg'.format(polly)

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
    clip_list = os.listdir('{}/politicians/{}/soundbites'.format(os.getcwd(), polly))
    for f in clip_list:
        f_name, f_ext = os.path.splitext(f)
        if f_ext != '.mp3':
            clip_list.remove(f)
    if len(clip_list) == 0:
        raise ValueError
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
        try:
            clip = await choose_soundbite(polly)
        except ValueError:
            await message.channel.send('This politician has no soundbites!')
            await v_client.disconnect()
        else:
            audio = discord.FFmpegPCMAudio('{}/politicians/{}/soundbites/{}'.format(os.getcwd(), polly, clip))

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
    elif message.content.startswith('!'):
        await create_command(message)

async def create_command(message):
    '''
    Check if valid politician command, and call the soundbite player if it is
    '''
    for polly in get_valid_commands():
        if message.content[1:].startswith(polly):
            await receive_command(message, polly)
            return
    # Default, not valid command
    await message.channel.send('This is not a valid command! Type !advise for more information')
    print(os.getcwd())

async def receive_command(message, polly):
    '''
    Set the bot up and play a soundbite
    '''
    config = parse_config(polly)
    name = get_name_from_config(config)
    await message.guild.me.edit(nick=name)
    await play_soundbite(message, polly)
    await message.guild.me.edit(nick="Bill Shorten")

async def advise(message):
    '''
    Help menu for the bot
    '''
    text_channel = message.channel
    helpcmd = discord.Embed(
        colour = discord.Colour.red()
    )

    helpcmd.set_author(name = 'Bill Shorten Help Commands')

    for politician in get_valid_commands():
        config = parse_config(politician)
        helpcmd.add_field(name = '!{}'.format(politician), value = 'Plays a juicy soundbite from {}'.format(get_name_from_config(config)), inline=False)
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
import discord
from discord.ext import commands
from random import randint
import logging
from sys import stdout
import difflib
import os

from exceptions import *
import db_handler as db


'''
DEPENDENCIES:
    discord.py
    PyNaCl
    ffmpeg be installed to PATH
'''

'''
TODO
* error handling (ie. command syntax reminders)
'''


# logger stuff
logger = logging.getLogger('gaybot')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(filename='gaybot.log', encoding='utf-8', mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:   %(message)s'))
console_handler = logging.StreamHandler(stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:   %(message)s'))
logger.addHandler(file_handler)
logger.addHandler(console_handler)

bot = commands.Bot(command_prefix='gay ', help_command=None, activity=discord.Game(name='gay help'))


# init images
mock_img = discord.File('images/mock.jpg')
yike_img = discord.File('images/yike.png')


quote_channel_id = 178576825511837696



@bot.event
async def on_ready():
    global logger
    logger.info(f'logged in as {bot.user.name}')
    logger.info('initializing user data')
    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                db.init_user(str(member.id), member.name)
    logger.info('finished initializing')
    logger.info('bot ready!')
    logger.info('awaiting commands ...\n\n\n')



@bot.command()
async def help(ctx):
    '''
    shows all the commands and their syntax
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    commands = ('```'
                'BOT COMMANDS\n'
                'note: all commands must be preceeded by "gay ". ex: "gay help"\n'
                'note: all instances of <user> can be pings with @ or name shorthands. ex: "gay mock @GayZach" is the same as "gay mock j-zach"\n'
                'github link: https://github.com/rexosorous/discord-bot\n\n'
                'help                       displays this message.\n'
                'checknicknames             shows all the users who have nicknames for quick referencing\n'
                'mock <user>                randomizes the capitlization in that user\'s last message in this channel.\n'
                'yikes <user>               awards that user with a yikes.\n'
                'checkyikes <user>          checks how many yikes that user has been awarded.\n'
                'bruh                       shows the bruh copy pasta.\n'
                'emoji <emoji name>         uses this server\'s emoji even if it\'s nitro gated. note: don\'t surround the emoji name with colons.\n'
                'quote <user> <num>         posts in the quote channel with the user\'s last num messages in this channel\n'
                'soundboard <clip name>     joins the voice channel and plays the specified clip\n'
                'checksoundboard            shows all the clips names that the soundboard can play\n'
                'scan                       scans the server\'s users to update the bot\'s database. use if new users join.'
                '```')
    await ctx.send(commands)



@bot.command()
async def checknicknames(ctx):
    '''
    gets a list of all users with a nickname
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    nicknames = db.get_nicknames()
    msg = 'all users with nicknames\n```username: nickname'
    for user in nicknames:
        msg += f"\n{user['username']}: {user['nickname']}"
    msg += '```\nif a name is not on here, they either don\'t have a nickname or are not initialized in the database'
    msg += '\nif you would like to change or add a nickname, message j-zach'
    await ctx.send(msg)



@bot.command()
async def mock(ctx, user):
    '''
    gets specified user's last message and mocks it
    ex: hello world -> hELlO woRLd
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    # allows for users to @mention or use real names
    if len(ctx.message.mentions) == 0:
        user_id = int(db.get_id(user))
    else:
        user_id = ctx.message.mentions[0].id

    async for msg in ctx.channel.history(limit=100):
        if msg.author.id == user_id and not msg.content.startswith('gay '): # get user's last message that's not a bot command
            mocked = ''
            for char in msg.content: # randomize what character is uppercase and lowercase
                if randint(0, 1) == 1:
                    mocked += char.upper()
                else:
                    mocked += char.lower()
            logger.info(mocked)
            await ctx.send(mocked)
            await ctx.send(file=mock_img)
            return



@bot.command()
async def yikes(ctx, recipient):
    '''
    awards a yikes to a user
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    try:
        # allows for users to @mention or use real names
        if len(ctx.message.mentions) == 0:
            ping = '<@' + db.get_id(recipient) + '>'
        else:
            ping = ctx.message.mentions[0].mention
        db.add_yikes(ping[ping.find('@')+1:-1]) # a really round about way to get the id
        logger.info(f'{recipient} received one yikes')
        await ctx.send(ping)
        await ctx.send(file=yike_img)
    except UserNotFound:
        logger.error(f'could not find {recipient} in database')
        await ctx.send(f'could not find {recipient}')



@bot.command()
async def checkyikes(ctx, user):
    '''
    checks how many yikes a user has
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    try:
        # allows for users to @mention or use real names
        if len(ctx.message.mentions) == 0:
            yike_qty = db.get_yikes_from_rname(user)
        else:
            user = ctx.message.mentions[0].name
            yike_qty = db.get_yikes_from_uname(user)

        # i need this part cause people are babies
        yike_msg = 'yikes'
        if yike_qty == 1:
            yike_msg = 'yike'

        logger.info(f'{user} has {yike_qty} {yike_msg}')
        await ctx.send(f'{user} has {yike_qty} {yike_msg}')
    except UserNotFound:
        logger.error(f'could not find {user} in database')
        await ctx.send(f'could not find {user}')



@bot.command()
async def bruh(ctx):
    '''
    bruh copy pasta
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    await ctx.send(':warning:BRUH:warning:...:warning:BRUH:warning:...:warning:BRUH:warning:... \n\nThe :police_officer: Department of :house: Homeland :statue_of_liberty: Security :oncoming_police_car: has issued a :b:ruh Moment :warning: warning :construction: for the following districts: Ligma, Sugma, :b:ofa, and Sugondese. \n\nNumerous instances of :b:ruh moments :b:eing triggered by :eyes: cringe:grimacing: normies :toilet: have :alarm_clock: recently :clock2: occurred across the :earth_americas: continental :flag_us:United States:flag_us:. These individuals are :b:elieved to :b:e highly :gun: dangerous :knife: and should :no_entry_sign: not :x: :b:e approached. Citizens are instructed to remain inside and :lock:lock their :door:doors. \n\nUnder :x:no:no_entry: circumstances should any citizen :speak_no_evil: say "bruh" in reaction to an action performed :b:y a cringe:grimacing: normie:toilet: and should store the following items in a secure:lock: location: Jahcoins:euro:, V-bucks:yen:, Gekyume\'s foreskin:eggplant:, poop:poop: socks, juul:thought_balloon: pods, ball :cherries: crushers, and dip. \n\nRemain tuned for further instructions. \n\n:warning:BRUH:warning:...:warning:BRUH:warning:...:warning:BRUH:warning:...')



@bot.command()
async def emoji(ctx, *emoji_names):
    '''
    allows users to use server nitro-gated emojis
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    msg = ''
    for server_emoji in await ctx.guild.fetch_emojis():
        if server_emoji.name in emoji_names:
            msg += str(server_emoji) + ' '

    if msg:
        logger.info(msg)
        await ctx.send(msg)



@bot.command()
async def quote(ctx, user, count=1):
    '''
    quotes user and posts it to multiple quotes of the day channel
    if count is specified, user's last count's worth of messages are combined into one quote
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    count = int(count)

    # allows for users to @mention or use real names
    if len(ctx.message.mentions) == 0:
        user_id = int(db.get_id(user))
    else:
        user_id = ctx.message.mentions[0].id

    # makes sure the bot doesn't ping the user when posting
    username = user
    if username.startswith('@'):
        username = username[1:]

    searched = 0
    quote = ''
    async for msg in ctx.channel.history(limit=100):
        if msg.author.id == user_id and not msg.content.startswith('gay '): # get user's last message that's not a bot command
            # gets rid of hanging '\n'
            if quote:
                quote = msg.content + '\n' + quote
            else:
                quote = msg.content

            searched += 1
            if count:
                if searched >= count:
                    await bot.get_channel(quote_channel_id).send(f'"{quote}" -{username}')
                    return



@bot.command()
async def soundboard(ctx, *search_terms):
    '''
    joins a voice channel and plays the specified soundboard clip
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    search = ' '.join(search_terms)
    all_clips = os.listdir('soundboard/') # finds all the file names
    selected_clip = difflib.get_close_matches(search, all_clips, cutoff=0.1) # finds the file name closest to search params

    if selected_clip: # don't join the VC if we couldn't find the clip
        channel = ctx.message.author.voice.channel # find the voice channel of the person who sent the message
        voice = await channel.connect() # connect to said voice channel
        voice.play(discord.FFmpegPCMAudio(f'soundboard/{selected_clip[0]}')) # play clip
        while voice.is_playing(): # wait until the clip is done playing to disconnect
            pass
        await voice.disconnect()
    else:
        await ctx.send('could not find any clips with that search term')



@bot.command()
async def checksoundboard(ctx):
    '''
    shows all the clips that the soundboard can play
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    clip_names = 'All Playable Soundboard Clips:```'
    all_clips = os.listdir('soundboard/')
    for clip in all_clips:
        clip_names += (clip[:-4] + '\n')
    clip_names += '```'
    await ctx.send(clip_names)



@bot.command()
async def scan(ctx):
    '''
    allows users to rescan the users during runtime if usernames are changed or new users join
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                db.init_user(str(member.id), member.name)



@bot.command()
async def stop(ctx):
    '''
    stops the bot
    can only be used by me
    '''
    global logger
    logger.info(f'{ctx.author.name}: {ctx.message.content}')

    if ctx.author.id == 158371798327492608:
        logger.info('bot shutting down')
        await bot.close()






with open('token.txt', 'r') as file:
    token = file.read()
bot.run(token)
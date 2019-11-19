import discord
from discord.ext import commands
from random import randint
import logging
from sys import stdout

from exceptions import *
import db_handler as db


'''
TODO
* error handling (ie. command syntax reminders)
'''

yikes_link = 'https://cdn.discordapp.com/attachments/244738123802607616/645827013030182932/d70d53df721cea99097dea76ab8eabbf.png'

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
                'note: all commands must be preceeded by "gay ". ex: gay help\n'
                'note: all instances of <user> can be pings with @ or name shorthands. ex: "gaymock @GayZach" is the same as "gaymock j-zach\n"'
                'help                 displays this message.\n'
                'mock <user>          randomizes the capitlization in that user\'s last message in this channel.\n'
                'yikes <user>         awards that user with a yikes.\n'
                'bruh                 shows the bruh copy pasta.\n'
                'emoji <emoji name>   uses this server\'s emoji even if it\'s nitro gated. note: don\'t surround the emoji name with colons.\n'
                'scan                 scans the server\'s users to update the bot\'s database. use if new users join.'
                '```')
    await ctx.send(commands)



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
        if msg.author.id == user_id: # get user's last message
            mocked = ''
            for char in msg.content: # randomize what character is uppercase and lowercase
                if randint(0, 1) == 1:
                    mocked += char.upper()
                else:
                    mocked += char.lower()
            logger.info(mocked)
            await ctx.send(mocked)
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
        await ctx.send(ping + ' ' + yikes_link)
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
        logger.info(f'{user} has {yike_qty} yikes')
        await ctx.send(f'{user} has {yike_qty} yikes')
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
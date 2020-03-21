from discord.ext import commands
import discord
import random

import utilities as util
from exceptions import *
import db_handler as db
import voice


'''
DEPENDENCIES:
    discord.py
    PyNaCl
    ffmpeg be installed to PATH
'''

'''
TODO
* allow the bot to stop soundclips midway through
* figure out a way to delete self.voice[server] when it's done to save on memory
* error handling (ie. command syntax reminders)
'''


class GayBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # images
        self.mock_img = 'images/mock.jpg'
        self.yike_img = 'images/yike.png'

        self.logger = util.get_logger()
        self.quote_channel_id = 178576825511837696
        self.voice = {}
        self.clip_bank,self.clipNameList = util.generate_clip_bank()



    @commands.command()
    async def help(self, ctx):
        '''
        shows all the commands and their syntax
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')
        await ctx.send(util.commands)



    @commands.command()
    async def checknicknames(self, ctx):
        '''
        gets a list of all users with a nickname
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')
        await ctx.send(util.get_nicknames())



    @commands.command()
    async def mock(self, ctx, user, count=1):
        '''
        gets specified user's last count messages and mocks it
        ex: hello world -> hELlO woRLd
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

        # allows for users to @mention or use real names
        if len(ctx.message.mentions) == 0:
            user_id = int(db.get_id(user))
        else:
            user_id = ctx.message.mentions[0].id

        count = int(count)
        quote = ''
        async for msg in ctx.channel.history(limit=100):
            if msg.author.id == user_id and not msg.content.startswith('gay '): # get user's last message that's not a bot command
                quote = util.build_quote(quote, msg.content)
                count -= 1
                if count <= 0:
                    break

        mocked = util.mock_msg(quote)
        self.logger.info(mocked)
        await ctx.send(mocked)
        await ctx.send(file=discord.File(self.mock_img))



    @commands.command()
    async def yikes(self, ctx, recipient):
        '''
        awards a yikes to a user
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

        try:
            # allows for users to @mention or use real names
            if len(ctx.message.mentions) == 0:
                ping = '<@' + db.get_id(recipient) + '>'
            else:
                ping = ctx.message.mentions[0].mention
            db.add_yikes(ping[ping.find('@')+1:-1]) # a really round about way to get the id
            self.logger.info(f'{recipient} received one yikes')
            await ctx.send(ping)
            await ctx.send(file=discord.File(self.yike_img))
        except UserNotFound:
            self.logger.error(f'could not find {recipient} in database')
            await ctx.send(f'could not find {recipient}')



    @commands.command()
    async def checkyikes(self, ctx, user):
        '''
        checks how many yikes a user has
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

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

            self.logger.info(f'{user} has {yike_qty} {yike_msg}')
            await ctx.send(f'{user} has {yike_qty} {yike_msg}')
        except UserNotFound:
            self.logger.error(f'could not find {user} in database')
            await ctx.send(f'could not find {user}')



    @commands.command()
    async def bruh(self, ctx):
        '''
        bruh copy pasta
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')
        await ctx.send(':warning:BRUH:warning:...:warning:BRUH:warning:...:warning:BRUH:warning:... \n\nThe :police_officer: Department of :house: Homeland :statue_of_liberty: Security :oncoming_police_car: has issued a :b:ruh Moment :warning: warning :construction: for the following districts: Ligma, Sugma, :b:ofa, and Sugondese. \n\nNumerous instances of :b:ruh moments :b:eing triggered by :eyes: cringe:grimacing: normies :toilet: have :alarm_clock: recently :clock2: occurred across the :earth_americas: continental :flag_us:United States:flag_us:. These individuals are :b:elieved to :b:e highly :gun: dangerous :knife: and should :no_entry_sign: not :x: :b:e approached. Citizens are instructed to remain inside and :lock:lock their :door:doors. \n\nUnder :x:no:no_entry: circumstances should any citizen :speak_no_evil: say "bruh" in reaction to an action performed :b:y a cringe:grimacing: normie:toilet: and should store the following items in a secure:lock: location: Jahcoins:euro:, V-bucks:yen:, Gekyume\'s foreskin:eggplant:, poop:poop: socks, juul:thought_balloon: pods, ball :cherries: crushers, and dip. \n\nRemain tuned for further instructions. \n\n:warning:BRUH:warning:...:warning:BRUH:warning:...:warning:BRUH:warning:...')



    @commands.command()
    async def emoji(self, ctx, *emoji_names):
        '''
        allows users to use server nitro-gated emojis
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

        msg = ''
        for server_emoji in await ctx.guild.fetch_emojis():
            if server_emoji.name in emoji_names:
                msg += str(server_emoji) + ' '

        if msg:
            self.logger.info(msg)
            await ctx.send(msg)



    @commands.command()
    async def quote(self, ctx, user, count=1):
        '''
        quotes user and posts it to multiple quotes of the day channel
        if count is specified, user's last count's worth of messages are combined into one quote
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

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

        quote = ''
        async for msg in ctx.channel.history(limit=100):
            if msg.author.id == user_id and not msg.content.startswith('gay '): # get user's last message that's not a bot command
                quote = util.build_quote(quote, msg.content)
                count -= 1
                if count <= 0:
                    break

        self.logger.info(f'"{quote}" -{username}')
        await self.bot.get_channel(self.quote_channel_id).send(f'"{quote}" -{username}')



    @commands.command()
    async def soundboard(self, ctx, *search_terms):
        '''
        joins a voice channel and plays the specified soundboard clip
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

        word_count = len(search_terms)
        search = ' '.join(search_terms)
        clip_name = util.get_clipv2(self.clipNameList, search_terms)
        # clip_name = util.get_clip(search, self.clip_bank[word_count])
        db.add_clip_stat(clip_name[:-4], 'soundboard')

        try:
            server = ctx.guild
            channel = ctx.message.author.voice.channel
            if server not in self.voice: # a bot can only be in one voice channel per server
                self.logger.info(f'creating {server} voice bot, connecting to {channel} and playing {clip_name}')
                self.voice[server] = voice.VoiceHandler(clip_name)
                await self.voice[server].connect(channel)
                await self.voice[server].play()
            elif not self.voice[server].active:
                self.logger.info(f'switching {server} voice channels to {channel} and playing {clip_name}')
                await self.voice[server].change_channel(channel, clip_name)
            else:
                self.logger.info(f'adding {clip_name} to {server}\'s audio queue in {channel}')
                self.voice[server].add_queue(clip_name)
        except InvalidAudioChannel:
            self.logger.error('user is not in a valid voice channel')
            await ctx.send('you are not in a voice channel')



    @commands.command()
    async def cliproulette(self, ctx):
        '''
        randomly selects an audio clip for gay soundboard to play
        '''
        all_clips = util.get_filenames('soundboard/')
        selected_clip = random.choice(all_clips)
        db.add_clip_stat(selected_clip[:-4], 'roulette')
        await self.soundboard(ctx, selected_clip[:-4])



    @commands.command()
    async def checksoundboard(self, ctx):
        '''
        shows all the clips that the soundboard can play
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

        clip_names = []
        for clip in util.get_filenames('soundboard/'):
            clip_names.append(f'{clip[:-4]}')
        clip_names.sort()
        clip_names.insert(0, 'All Playable Soundboard Clips:```')
        clip_names.append('```')
        msg = '\n'.join(clip_names)
        await ctx.send(msg)



    @commands.command()
    async def soundboardstats(self, ctx):
        '''
        shows the stats for all the clips
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')
        await ctx.send(db.get_clip_stats())



    @commands.command()
    async def stop(self, ctx):
        '''
        disconnects from voice channel
        functionally the same as leave
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')
        server = ctx.guild
        self.voice[server].disconnect()
        del self.voice[server]



    @commands.command()
    async def leave(self, ctx):
        '''
        disconnects from voice channel
        functionally the same as stop
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')
        server = ctx.guild
        self.voice[server].disconnect()
        del self.voice[server]



    @commands.command()
    async def scan(self, ctx):
        '''
        allows users to rescan the users during runtime if usernames are changed or new users join
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

        for guild in self.bot.guilds:
            for member in guild.members:
                if not member.bot:
                    db.init_user(str(member.id), member.name)



    @commands.command()
    async def kill(self, ctx):
        '''
        stops the bot
        can only be used by me
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

        if ctx.author.id == 158371798327492608:
            self.logger.info('bot shutting down')
            await self.bot.close()




if __name__ == '__main__':
    bot = commands.Bot(command_prefix='gay ', help_command=None, activity=discord.Game(name='gay help'))
    @bot.event
    async def on_ready():
        print(f'logged in as {bot.user.name}')
    bot.add_cog(GayBot(bot))


    with open('token.txt', 'r') as file:
        token = file.read()
        bot.run(token)
from discord.ext import commands
import discord

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
* figure out a way to delete self.voice[server] when it's done to save on memory
* error handling (ie. command syntax reminders)
'''


class GayBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # images
        self.mock_img = discord.File('images/mock.jpg')
        self.yike_img = discord.File('images/yike.png')

        self.logger = util.get_logger()
        self.quote_channel_id = 178576825511837696
        self.voice = {}
        self.clip_bank = util.load_file('clip_bank.json')



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
        util.get_nicknames()
        await ctx.send(msg)



    @commands.command()
    async def mock(self, ctx, user):
        '''
        gets specified user's last message and mocks it
        ex: hello world -> hELlO woRLd
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

        # allows for users to @mention or use real names
        if len(ctx.message.mentions) == 0:
            user_id = int(db.get_id(user))
        else:
            user_id = ctx.message.mentions[0].id

        async for msg in ctx.channel.history(limit=100):
            if msg.author.id == user_id and not msg.content.startswith('gay '): # get user's last message that's not a bot command
                mocked = util.mock_msg(msg.content)
                self.logger.info(mocked)
                await ctx.send(mocked)
                await ctx.send(file=self.mock_img)
                return



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
            await ctx.send(file=self.yike_img)
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
                        await self.bot.get_channel(self.quote_channel_id).send(f'"{quote}" -{username}')
                        return



    @commands.command()
    async def soundboard(self, ctx, *search_terms):
        '''
        joins a voice channel and plays the specified soundboard clip
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

        word_count = len(search_terms)
        search = ' '.join(search_terms)
        clip_name = util.get_clip(search, self.clip_bank[str(word_count)])

        try:
            server = ctx.guild
            channel = ctx.message.author.voice.channel
            if server not in self.voice: # a bot can only be in one voice channel per server
                self.voice[server] = voice.VoiceHandler(clip_name)
                await self.voice[server].connect(channel)
                await self.voice[server].play()
            elif not self.voice[server].active:
                await self.voice[server].change_channel(channel, clip_name)
            else:
                self.voice[server].add_queue(clip_name)
        except InvalidAudioChannel:
            await ctx.send('you are not in a voice channel')



    @commands.command()
    async def checksoundboard(self, ctx):
        '''
        shows all the clips that the soundboard can play
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')

        clip_names = 'All Playable Soundboard Clips:```'
        all_clips = util.get_filenames('soundboard/')
        for clip in all_clips:
            clip_names += (clip[:-4] + '\n')
        clip_names += '```'
        await ctx.send(clip_names)



    @commands.command()
    async def stop(self, ctx):
        '''
        disconnects from voice channel
        functionally the same as leave
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')
        self.voice.stop()
        await voice.disconnect()



    @commands.command()
    async def leave(self, ctx):
        '''
        disconnects from voice channel
        functionally the same as stop
        '''
        self.logger.info(f'{ctx.author.name}: {ctx.message.content}')
        self.stop()
        await voice.disconnect()



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
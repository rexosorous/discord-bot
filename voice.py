from discord import FFmpegPCMAudio
import utilities as util
import asyncio



class VoiceHandler():
    def __init__(self, clip_name=[]):
        self.active = True
        self.queue = clip_name if isinstance(clip_name, list) else [clip_name]
        self.voice = None
        self.playing = False



    async def connect(self, channel):
        try:
            self.voice = await channel.connect()
        except AttributeError:
            raise InvalidAudioChannel



    async def disconnect(self):
        await self.voice.disconnect()
        self.active = False
        self.playing = False



    async def play(self, interval=1):
        if self.playing:
            return

        self.playing = True
        while self.queue:
            if self.queue[0].startswith('phasmophobia'):
                self.voice.play(FFmpegPCMAudio(f'{self.queue.pop(0)}'))
            else:
                self.voice.play(FFmpegPCMAudio(f'soundboard/{self.queue.pop(0)}')) # play clip
            while self.voice.is_playing():
                await asyncio.sleep(0.5)
            await asyncio.sleep(interval)
        self.playing = False



    async def change_channel(self, channel):
        self.active = True
        await self.connect(channel)



    def add_queue(self, clip_name):
        if isinstance(clip_name, list):
            self.queue += clip_name
        else:
            self.queue.append(clip_name)
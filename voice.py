from discord import FFmpegPCMAudio
import utilities as util
import asyncio



class VoiceHandler():
    def __init__(self, clip_name):
        self.active = True
        self.queue = [clip_name]
        self.voice = None



    async def connect(self, channel):
        try:
            self.voice = await channel.connect()
        except AttributeError:
            raise InvalidAudioChannel



    async def disconnect(self):
        await self.voice.disconnect()
        self.active = False



    async def play(self):
        while self.queue:
            self.voice.play(FFmpegPCMAudio(f'soundboard/{self.queue.pop(0)}')) # play clip
            while self.voice.is_playing():
                await asyncio.sleep(0.5)
            await asyncio.sleep(1)
        await self.disconnect()



    async def change_channel(self, channel, clip_name):
        self.active = True
        self.add_queue(clip_name)
        await self.connect(channel)
        await self.play()



    def add_queue(self, clip_name):
        self.queue.append(clip_name)
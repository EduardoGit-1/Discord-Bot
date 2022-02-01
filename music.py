from pickle import GLOBAL
import discord
from discord.ext import commands
import youtube_dl
import time

youtube_dl.utils.bug_reports_message = lambda: ''
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' 
}
FFMPEG_OPTIONS = {'options':'-vn'}

pause_resume_emo = "⏯️"
previews_song_emo = "⏮️"
next_song_emo = "⏭️"
stop_emo = 	"⏹"
class Music(commands.Cog):

    _GLOBAL_QUEUE_INDEX = 0
    _QUEUE = list()
    _MESSAGE = 0
    def __init__(self, client):
        self.client = client
    
    @commands.command()
    async def music(self, ctx):
        await ctx.send("music cog is working")

    @commands.command()
    async def play(self, ctx, url:str):
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

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            music_title = info.get('title', None)
            music_duration = info.get('duration', None)
            ydl_url = info['formats'][0]['url']
            self._QUEUE.append({
                "title" : music_title,
                # "source" : source,
                "duration" : music_duration,
                "ydl_url" : ydl_url
            })
            if len(self._QUEUE) == 1:
                source = await discord.FFmpegOpusAudio.from_probe(ydl_url, **FFMPEG_OPTIONS)
                self._MESSAGE = await ctx.send("Now playing {}".format(music_title))
                ctx.voice_client.play(source)
            else:
                self._MESSAGE = await ctx.send("Song: {} has been added to queue".format(music_title))
                time.sleep(2)
                await self._MESSAGE.edit(content="Now playing {}".format(self._QUEUE[self._GLOBAL_QUEUE_INDEX]['title']))
            await self._MESSAGE.add_reaction(previews_song_emo)
            await self._MESSAGE.add_reaction(pause_resume_emo)
            await self._MESSAGE.add_reaction(next_song_emo)
            await self._MESSAGE.add_reaction(stop_emo)

            

    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()
        await ctx.send("Music paused!")
    
    @commands.command()
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        await ctx.send("Music resumed!")
    
    @commands.command()
    async def stop(self, ctx):
        await ctx.voice_client.stop()
        await ctx.send("Music stoped!")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        async def transform_url(ydl_url):
            source = await discord.FFmpegOpusAudio.from_probe(ydl_url, **FFMPEG_OPTIONS)
            return source

        if payload.user_id != self.client.user.id and payload.message_id == self._MESSAGE.id:
            ctx = await self.client.get_context(self._MESSAGE)
    
            if str(payload.emoji) == pause_resume_emo:
                if ctx.voice_client.is_playing():
                    ctx.voice_client.pause()
                    await ctx.send("Music paused!")
                else:
                    ctx.voice_client.resume()
                    await ctx.send("Music resumed!")
            elif str(payload.emoji) == next_song_emo:
                self._GLOBAL_QUEUE_INDEX += 1
                print(self._GLOBAL_QUEUE_INDEX)
                if len(self._QUEUE) > 1 and (self._GLOBAL_QUEUE_INDEX <= (len(self._QUEUE) - 1)):
                    await self._MESSAGE.edit(content="Now playing {}".format(self._QUEUE[self._GLOBAL_QUEUE_INDEX]['title']))
                    ctx.voice_client.stop()
                    source = await transform_url(self._QUEUE[self._GLOBAL_QUEUE_INDEX]['ydl_url'])
                    # ctx.voice_client.play(self._QUEUE[self._GLOBAL_QUEUE_INDEX]['source'])
                    ctx.voice_client.play(source)
                else:
                    if self._GLOBAL_QUEUE_INDEX > 0 : self._GLOBAL_QUEUE_INDEX -= 1
                    await payload.member.guild.system_channel.send("There are no more songs in queue!")
            elif str(payload.emoji) == previews_song_emo:
                self._GLOBAL_QUEUE_INDEX -= 1
                print(self._GLOBAL_QUEUE_INDEX)
                if len(self._QUEUE) > 0 and (self._GLOBAL_QUEUE_INDEX >= 0):
                    source = await transform_url(self._QUEUE[self._GLOBAL_QUEUE_INDEX]['ydl_url'])
                    ctx.voice_client.stop()
                    # ctx.voice_client.play(self._QUEUE[self._GLOBAL_QUEUE_INDEX]['source'])
                    ctx.voice_client.play(source)
                    await self._MESSAGE.edit(content="Now playing {}".format(self._QUEUE[self._GLOBAL_QUEUE_INDEX]['title']))
                else:
                    self._GLOBAL_QUEUE_INDEX = 0
                    await ctx.send("There are no more songs in queue!")
            elif str(payload.emoji) == stop_emo:
                    ctx.voice_client.stop()
                    self._QUEUE.clear()
                    await ctx.send("Music stoped and queue was cleared!")

            await self._MESSAGE.remove_reaction(payload.emoji, payload.member)
        



def setup(client):
    client.add_cog(Music(client))
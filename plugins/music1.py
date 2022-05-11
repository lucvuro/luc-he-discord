# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Valentin B.
A simple music bot written in discord.py using youtube-dl.
Though it's a simple example, music bots are complex and require much time and knowledge until they work perfectly.
Use this as an example or a base for your own bot and extend it as you want. If there are any bugs, please let me know.
Requirements:
Python 3.5+
pip install -U discord.py pynacl youtube-dl
You also need FFmpeg in your PATH environment variable or the FFmpeg.exe binary in your bot's directory on Windows.
"""

import asyncio
import functools
import itertools
import math
import random
from datetime import datetime
import time
from time import gmtime
from xdrlib import ConversionError
import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Không tìm được bài phù hợp cho từ khóa `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Không tìm được bài phù hợp cho từ khóa `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Không tìm được bài phù hợp cho từ khóa `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        format = ""
        # duration = []
        # if days > 0:
        #     duration.append('{}'.format(days))
        # if hours > 0:
        #     duration.append('{}'.format(hours))
        # if minutes > 0:
        #     duration.append('{}'.format(minutes))
        # if seconds >= 0:
        #     duration.append('{}'.format(seconds))
        if days > 0:
            format = "%d:%H:%M:%S"
        elif hours > 0:
            format = "%H:%M:%S"
        elif minutes > 0:
            format = "%M:%S"
        elif seconds >= 0:
            format = "%M:%S"
        # print(':'.join(duration),format)
        # time =  datetime.strptime(':'.join(duration),format)
        # return time.strftime(format)
        return time.strftime(format,gmtime(duration))


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Đang phát',
                               description='[{0.source.title}]({0.source.url})'.format(self),
                               color=discord.Color.blue())
                #  .add_field(name='** **', value='[{0.source.title}]({0.source.url})'.format(self),inline=False)              
                 .add_field(name='Thời lượng', value=f'`{self.source.duration}`')
                 .add_field(name='Requested by', value=self.requester.mention)
                #  .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                #  .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]

class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx
        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()
        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        # return self.voice and self.current
        return self._ctx.voice_client.is_playing()
    async def audio_player_task(self):
        while True:
            self.next.clear()
            self.now = None
            if self.loop == False:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

                # self.current.source.volume = self._volume
                # self.voice.play(self.current.source, after=self.play_next_song)
            self.now = discord.FFmpegPCMAudio(self.current.source.stream_url)
            self.voice.play(self.now,after=self.play_next_song)
            # await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()
            # self.current = None
    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    async def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()
            # list_song = enumerate(self.songs, 1)
            try:
                embed = (discord.Embed(title=f'{self._ctx.author} vừa skip 1 bài',
                                description = f'[Previous]({self.current.source.url}): {self.current.source.title}\n[Next]({self.songs[0].source.url}): {self.songs[0].source.title}',
                               color=discord.Color.blue()))
                await self._ctx.send(embed=embed)
            except IndexError:
                embed = (discord.Embed(title=f'{self._ctx.author} vừa skip 1 bài',
                                description = f'[Previous]({self.current.source.url}): {self.current.source.title}\nKhông còn nhạc để tui phát, tui đi đây',
                               color=discord.Color.blue()))
                await self._ctx.send(embed=embed)
                await self.stop()
        # if len(self.songs) == 0:
        #     await self.stop()
        
    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None
        # # return self.bot.loop.create_task(self._cog.cleanup(guild))
        return self.bot.loop.create_task(self._ctx.cog.cleanup(self._ctx.guild))


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state
    async def cleanup(self, guild):
        try:
            del self.voice_states[guild.id]
        except KeyError:
            pass
    
    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('Lệnh này không thể sử dụng trong kênh DM')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error,commands.MissingRequiredArgument):
            return
        if isinstance(error,commands.BadArgument):
            return
        if isinstance(error,commands.CheckFailure):
            return await ctx.send("Server của bạn hiện tại không nằm trong whitelist!\nVui lòng liên hệ với chủ bot để được thêm vào whitelist")
        await ctx.send('Có lỗi xảy ra: {}'.format(str(error)))

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()
        await ctx.send("222222")
    @commands.command(name='summon')
    @commands.has_permissions(manage_guild=True)
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel.
        If no channel was specified, it joins your channel.
        """

        if not channel and not ctx.author.voice:
            raise VoiceError('Bạn đang không trong voice hoặc là bạn đang triệu hồi tui tới 1 kênh ẩn mà trong đó không có tui..')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()
        await ctx.send("222222")
    @commands.command(name='stop', aliases=['disconnect'])
    # @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send('Tôi đang ở ngoài, đưa tôi vô voice rồi tính tiếp.')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    # @commands.command(name='volume')
    # async def _volume(self, ctx: commands.Context, *, volume: int):
    #     """Sets the volume of the player."""

    #     if not ctx.voice_state.is_playing:
    #         return await ctx.send('Nothing being played at the moment.')

    #     if 0 > volume > 100:
    #         return await ctx.send('Volume must be between 0 and 100')

    #     ctx.voice_state.volume = volume / 100
    #     await ctx.send('Volume of the player set to {}%'.format(volume))

    @commands.command(name='nowplaying', aliases=['np'])
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song."""
        if not ctx.voice_state.voice:
            return await ctx.send('Tôi đang ở ngoài, đưa tôi vô voice rồi tính tiếp.')
        await ctx.send(embed=ctx.voice_state.current.create_embed())

    # @commands.command(name='pause')
    # # @commands.has_permissions(manage_guild=True)
    # async def _pause(self, ctx: commands.Context):
    #     """Pauses the currently playing song."""

    #     if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
    #         ctx.voice_state.voice.pause()
    #         await ctx.message.add_reaction('⏯')

    # @commands.command(name='resume')
    # # @commands.has_permissions(manage_guild=True)
    # async def _resume(self, ctx: commands.Context):
    #     """Resumes a currently paused song."""

    #     if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
    #         ctx.voice_state.voice.resume()
    #         await ctx.message.add_reaction('⏯')

    # @commands.command(name='clear')
    # # @commands.has_permissions(manage_guild=True)
    # async def _stop(self, ctx: commands.Context):
    #     """Stops playing song and clears the queue."""

    #     ctx.voice_state.songs.clear()

    #     if not ctx.voice_state.is_playing:
    #         ctx.voice_state.voice.stop()
    #         await ctx.message.add_reaction('⏹')

    @commands.command(name='skip',aliases=['s'])
    async def _skip(self, ctx: commands.Context):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """
        if not ctx.voice_state.voice:
            return await ctx.send('Tôi đang ở ngoài, đưa tôi vô voice rồi tính tiếp.')
        if not ctx.voice_state.is_playing:
            return await ctx.send('Có gì đâu mà skip? Có bị đin hok?')
        await ctx.voice_state.skip()
        # voter = ctx.message.author
        # if voter == ctx.voice_state.current.requester:
        #     await ctx.message.add_reaction('⏭')
        #     ctx.voice_state.skip()

        # elif voter.id not in ctx.voice_state.skip_votes:
        #     ctx.voice_state.skip_votes.add(voter.id)
        #     total_votes = len(ctx.voice_state.skip_votes)

        #     if total_votes >= 3:
        #         await ctx.message.add_reaction('⏭')
        #         ctx.voice_state.skip()
        #     else:
        #         await ctx.send('Skip vote added, currently at **{}/3**'.format(total_votes))

        # else:
        #     await ctx.send('You have already voted to skip this song.')

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's queue.
        You can optionally specify the page to show. Each page contains 10 elements.
        """
        if not ctx.voice_state.voice:
            return await ctx.send('Tôi đang ở ngoài, đưa tôi vô voice rồi tính tiếp.')
        if not ctx.voice_client.is_playing():
            return await ctx.send('Danh sách đang không có nhạc giống như bạn đang không có người yêu vậy.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '[#{0}]({1.source.url}) - {1.source.title} `[{1.source.duration}]`\n'.format(i + 1, song)

        embed = (discord.Embed(title="Danh sách phát",description=f'[đang phát]({ctx.voice_state.current.source.url}) - **{ctx.voice_state.current.source.title}** `[{ctx.voice_state.current.source.duration}]`\n{queue}',color=discord.Color.blue())
                 .add_field(name="\u200B",value=f'Số bài: **{len(ctx.voice_state.songs) + 1}**'))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """Shuffles the queue."""
        if not ctx.voice_state.voice:
            return await ctx.send('Tôi đang ở ngoài, đưa tôi vô voice rồi tính tiếp.')
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Có ăn bánh trán trộn bao giờ chưa, không có bánh trán thì lấy gì trộn, danh sách nhạc đang trống thì lấy nhạc đâu mà trộn? Có bị khùm hok?.')

        ctx.voice_state.songs.shuffle()
        await ctx.send("Đã trộn list nhạc xong, mời bạn ăn")

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int):
        """Removes a song from the queue at a given index."""
        if not isinstance(index,int):
            return await ctx.send(f"{index} không phải là 1 số hợp lệ")
        if not ctx.voice_state.voice:
            return await ctx.send('Tôi đang ở ngoài, đưa tôi vô voice rồi tính tiếp.')
        if index <= 0:
            return await ctx.send(f"Có khùm hok? Làm gì có bài nào số thứ tự {index}")
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Danh sách nhạc rỗng thì xóa cái gì, có bị khùm hok?.')

        embed = (discord.Embed(title='',
                                description = f'Đã xóa [#{index}]({ctx.voice_state.songs[index-1].source.url}) **{ctx.voice_state.songs[index-1].source.title}** ra khỏi danh sách',
                            color=discord.Color.blue()))
        await ctx.send(embed=embed)
        ctx.voice_state.songs.remove(index - 1)
    @_remove.error
    async def _remove_error(self,ctx,error):
        if isinstance(error,commands.BadArgument):
            await ctx.send("Lệnh sai cú pháp rồi pa: `~remove number`")
    @commands.command(name='loop')
    async def _loop(self, ctx: commands.Context):
        """Loops the currently playing song.
        Invoke this command again to unloop the song.
        """
        if not ctx.voice_state.voice:
            return await ctx.send('Tôi đang ở ngoài, đưa tôi vô voice rồi tính tiếp.')
        if not ctx.voice_state.is_playing:
            return await ctx.send('Có bài nào đâu mà loop, có bị khùm hok?')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        if ctx.voice_state.loop:
            return await ctx.send('Loop đang **bật**')
        else:
            return await ctx.send('Loop đang **tắt**')
    @commands.command(name='play',aliases=['p'])
    async def _play(self, ctx: commands.Context, *, search: str):
        """Plays a song.
        If there are songs in the queue, this will be queued until the
        other songs finished playing.
        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """
        if not ctx.voice_client:
            await ctx.invoke(self._join)

        try:
            source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
        except YTDLError as e:
            await ctx.send('Có lỗi xảy ra: {}'.format(str(e)))
        else:
            song = Song(source)

            await ctx.voice_state.songs.put(song)
            embed = (discord.Embed(title=f'{ctx.author} vừa thêm một bài mới',
                                description = f'[#{len(ctx.voice_state.songs)}]({source.url}) **{source.title}**\n',
                            color=discord.Color.blue()))
            await ctx.send(embed=embed)
    @_play.error
    async def _play_error(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            await ctx.send('Lệnh sai cú pháp rồi pa: `~play tenbaihat | url`')
    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('Bạn đang không ở trong kênh voice nào cả.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Tôi đang ở trong voice rồi.')
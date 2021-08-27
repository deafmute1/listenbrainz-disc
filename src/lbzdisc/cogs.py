#stdlib
from enum import Enum
from typing import Iterable, Tuple, Union, Optional  
import logging 
import importlib.metadata
from datetime import datetime 

#self
import lbzdisc.utils as utils
from lbzdisc.data import DataManager

#pypi
from discord.ext import commands
import discord
import pylistenbrainz 

import musicbrainzngs 
musicbrainzngs.set_useragent('listenbrainz-disc', importlib.metadata.version('listenbrainz-disc') , contact='https://github.com/deafmute1/listenbrainz-disc')

modes = ['PLAIN', 'PLAINFULL', 'EMBED', 'EMBEDFULL']

plain_view_modes = ('PLAIN', 'PLAINFULL')
embed_view_modes = ('EMBED', 'EMBEDFULL')

class Core(commands.Cog): 
    def __init__(self, bot:commands.Bot, data: DataManager) -> None: 
        self.bot = bot 
        self.data = data
        self.lbz = pylistenbrainz.ListenBrainz()

    async def _format_no_data(self, text: str) -> Union[str, discord.Embed, None]: 
        content, embed = None, None
        mode = self.data.get_global_option('mode') 
        if mode in plain_view_modes: 
            content = text 
        elif mode in embed_view_modes:
            embed = discord.Embed(description = text)
        return content, embed

    async def _get_cover_url(self, listen: pylistenbrainz.Listen) -> Union[str, discord.Embed]: 
        try: 
            if listen.release_group_mbid is not None: 
                images = musicbrainzngs.get_release_group_image_list(listen.release_group_mbid)['images']
            elif listen.release_mbid is not None: 
                images = musicbrainzngs.get_image_list(listen.release_mbid)['images']
            else:
                res = musicbrainzngs.search_releases(listen.release_name, artist=listen.artist_name)['release-list']
                if res is not None and res != []: 
                    images = musicbrainzngs.get_image_list(res[0])['images']
            for image in images:
                if image['front']: 
                    return image['thumbnails']['250']
        except Exception: 
            logging.exception("Failed to retrieve cover url from musicbrainz API")

    async def _format_listens(self, header: str, footer: str, listens: list, ctx: commands.Context) -> Union[str, discord.Embed, None]:
        content = None
        embed = None
        mode = self.data.get_global_option('mode')

        if mode == 'PLAIN':
            content =   header + \
                        ''.join([f'{i+1}: **{e.track_name}** by {e.artist_name} | {e.release_name}\n' for i, e in enumerate(listens)]) + \
                        footer
        elif mode == 'PLAINFULL': 
            content =   header + \
                        ''.join([f'{i+1}: **{e.track_name}** by {e.artist_name} | {e.release_name}\n at {datetime.fromtimestamp(e.listened_at)}' for i, e in enumerate(listens)]) + \
                        footer
        elif mode in embed_view_modes:
            uid = self.data.get_user_by_id(ctx.author.id)
            embed = discord.Embed()
            embed.set_author(   name = header, 
                                url = f'https://listenbrainz.org/user/{uid}/',
                                icon_url = ctx.author.avatar_url
            )
            embed.set_footer(text = footer)
            url = await self._get_cover_url(listens[0])
            if url is not None: 
                logging.debug("Got thumbnail url from musicbrainz: {url}")
                embed.set_thumbnail(url = url)
            for i, e in enumerate(listens): 
                field = f'By {e.artist_name} | {e.release_name}'
                if mode == 'EMBEDFULL':
                    field += f'\n At {datetime.fromtimestamp(e.listened_at)}'
                embed.add_field(name=f'**{i+1}: {e.track_name} **', value=field)

        return (content, embed)

    @commands.command(  
        aliases = ['lbz','lb','r', 'listens'], 
        description = 'Get recent listens for user',
        usage = 'lbz <NUMBER OF LISTENS=2> <LISTENBRAINZ USER=!set_user>'
    )
    async def get_listens(self, ctx: commands.Context, count: Optional[int] = 2, *, user: Optional[str] = None) -> None: 
        if user is None: 
            user = self.data.get_user_by_id(ctx.author.id)
            if user is None: 
                await ctx.send(f'You neither specified a user, nor have a user set using set_user.')
        content, embed = await self._format_listens( 
            f'Recent listens for {utils.nick_or_name(ctx.author)}: \n',
            f'{utils.nick_or_name(ctx.author)} has {self.lbz.get_user_listen_count(user)} listens', 
            self.lbz.get_listens(user, count=count), 
            ctx
        )
        if embed is not None:
            await ctx.send(embed = embed)
        else:  
            await ctx.send(content=content, embed = embed)

    @commands.command(
        alias = ['np', 'playing'],
        description = 'Get current listen for user',
        usage = 'np <LISTENBRAINZ USER=!set_user>'
    )
    async def now_playing(self, ctx: commands.Context, *, user: Optional[str] = None) -> None:
        if user is None: 
            user = self.data.get_user_by_id(ctx.author.id)
            if user is None: 
                await ctx.send(f'You neither specified a user, nor have a user set using set_user.')
                return
        listen = self.lbz.get_playing_now(user)  
        logging.debug(f'Got listens: {listen}')     
        if listen is None: 
            content, embed = await self._format_no_data(f'Nothing currently playing for {utils.nick_or_name(ctx.author)}')
        else: 
            content, embed = await self._format_listens(
                f'Now playing for {utils.nick_or_name(ctx.author)}', 
                f'{utils.nick_or_name(ctx.author)} has {self.lbz.get_user_listen_count(user)} listens', 
                [listen],
                ctx
            )
        if content is None:
            await ctx.send(embed=embed)
        else: 
            await ctx.send(content=content, embed = embed)

    @commands.command(description = 'Set your listenbrainz username')
    async def set_user(self, ctx: commands.Context, *, arg: str): 
        await self.data.set_user_for_id(ctx.author.id, arg)
        await ctx.send(f'Set {utils.nick_or_name(ctx.author)}\'s listenbrainz user to {self.data.get_user_by_id(ctx.author.id)}')

    @commands.command(description = '[ADMIN] Set reply mode (overrides env settings). \
                                    Valid values: ' + ','.join(modes)
    )
    @commands.has_permissions(administrator = True)
    async def set_mode(self, ctx:commands.Context, *, mode: str):
        mode = mode.upper() 
        if mode not in modes: 
            await ctx.send('Invalid mode. Valid values are: ' + ','.join(modes))
            return
        await self.data.set_global_option('mode', mode)
        set_mode = self.data.get_global_option('mode')
        await ctx.send(f'Set mode to {set_mode}')




#stdlib
from enum import Enum
from typing import Tuple  
import logging 
#pypi
from discord.ext import commands
import pylistenbrainz 

#self

from lbzdisc.data import DataManager

class ViewModes(Enum): 
    PLAIN = 'PLAIN'
    PLAINFULL = 'PLAINFULL'

class Configure(commands.Cog): 
    def __init__(self, bot: commands.Bot, data: DataManager) -> None:
        self.bot = bot 
        self.data = data

    @commands.command(brief = 'Set your listenbrainz username')
    async def set_user(self, ctx: commands.Context, *, arg: str): 
        await self.data.set_user_for_id(ctx.author.id, arg)

class FetchUserData(commands.Cog): 
    def __init__(self, bot:commands.Bot, data: DataManager, mode=ViewModes.PLAIN) -> None: 
        self.bot = bot 
        self.mode = mode
        self.data = data
        self.lbz_api = pylistenbrainz.ListenBrainz()

    async def _decompose_user_and_range_args(self, ctx, args, default_count=5) -> Tuple[str, int]:
        try: 
            user = args[0] 
        except IndexError: 
            user = await self.data.get_user_by_id(ctx.author.id)

        try: 
            count = args[1]
        except IndexError: 
            count = default_count

        return (user, count)

    @commands.command(  aliases = ['np', 'lb', 'ns'], 
                        brief = 'Get recent scrobbles for user',
                        usage = 'lbz <LISTENBRAINZ USER> <NUMBER OF SCROBLES>'
    )
    async def lbz(self, ctx: commands.Context, *args) -> None: 
        user, count = await self._decompose_user_and_range_args(ctx, args, 2)

        listens = self.lbz_api.get_listens(user, count=count) 
        content = None
        embed = None
        heading = f'Recent scrobbles for {ctx.author.name}: \n'
        footer = f'{ctx.author.name} has {self.lbz_api.get_user_listen_count(user)} listens'
        
        if self.mode == ViewModes.PLAIN:
            content = heading + ''.join([f'{i}: **{e.track_name}** by {e.artist_name} | {e.release_name}\n' for i, e in enumerate(listens)]) + footer
        elif self.mode == ViewModes.PLAINFULL: 
            content = heading + ''.join([f'{i+1}: **{e.track_name}** by {e.artist_name} | {e.release_name}\n at {e.listened_at}' for i, e in enumerate(listens)]) + footer
        
        await ctx.send(content=content, embed=embed)



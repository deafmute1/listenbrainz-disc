#stdlib 
from typing import Union 

#pypi
import discord

def nick_or_name(user: Union[discord.User, discord.Member]) -> str: 
    if user.nick is not None:
        return user.nick 
    return user.name
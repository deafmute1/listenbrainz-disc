#stdlib
import os 
import logging 
from enum import Enum
from pathlib import Path 

#pypi
from discord.ext import commands

#self
from lbzdisc import cogs, exceptions, data

try: 
    import dotenv
    dotenv.load_dotenv()
except ModuleNotFoundError: 
    print("python-dotenv not installed; your .env (if it exists) was not loaded.")

DEFAULT = {
    'LBZ_LOG_LEVEL': 'WARNING',
    'LBZ_LOG_FORMAT': '%(asctime)s : %(levelname)s : %(message)s',
    'LBZ_LOG_FILE': None,
    'LBZ_BOT_PREFIX': '!',
    'LBZ_DATA_DIR': '.'
}

def startBot() -> None: 
    handlers = [logging.StreamHandler()]
    log_file = os.getenv('LBZ_LOG_FILE', DEFAULT['LBZ_LOG_FILE'])
    if log_file is not None: 
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(level=os.getenv('LBZ_LOG_LEVEL', DEFAULT['LBZ_LOG_LEVEL']), 
                        format=os.getenv('LBZ_LOG_FORMAT', DEFAULT['LBZ_LOG_FORMAT']),
                        handlers=handlers
    )

    data_dir = Path(os.getenv('LBZ_DATA_DIR', DEFAULT['LBZ_DATA_DIR'])).resolve()
    if not data_dir.is_dir(): 
        data_dir.mkdir()
    data_manager = data.DataManager(data_dir.joinpath('lbzdisc.json'))

    bot = commands.Bot(command_prefix=os.getenv('LBZ_BOT_PREFIX', DEFAULT['LBZ_BOT_PREFIX']))
    bot.add_cog(cogs.FetchUserData(bot, data_manager))
    bot.add_cog(cogs.Configure(bot, data_manager))
    token = os.getenv('LBZ_DISCORD_TOKEN')
    if token is None: 
        logging.error("No token set in LBZ_DISCORD_TOKEN")
        raise exceptions.MissingCriticalEnvironmentalVariable("Missing LBZ_DISCORD_TOKEN")
    bot.run(token)

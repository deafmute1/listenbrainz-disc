#stdlib
import os 
import logging 
from pathlib import Path 
import importlib.metadata
import asyncio 

#pypi
from discord.ext import commands

#self
from lbzdisc import cogs, exceptions, data

try: 
    import dotenv
    dotenv.load_dotenv()
except ModuleNotFoundError: 
    print("python-dotenv not installed; your .env (if it exists) was not loaded.")


__version__ = importlib.metadata.version('listenbrainz-disc') 

DEFAULT = {
    'LBZ_LOG_LEVEL': 'WARNING',
    'LBZ_LOG_FORMAT': '%(asctime)s : %(levelname)s : %(message)s',
    'LBZ_LOG_FILE': None,
    'LBZ_BOT_PREFIX': '!',
    'LBZ_MODE': 'EMBED',
    'LBZ_DATA_DIR': '.'
}

def startBot() -> None: 
    handlers = [logging.StreamHandler()]
    log_file = os.getenv('LBZ_LOG_FILE', DEFAULT['LBZ_LOG_FILE'])
    if log_file is not None: 
        handlers.append(logging.FileHandler(log_file))
        logging.info(f'Using log file: {log_file}')
    logging.basicConfig(level=os.getenv('LBZ_LOG_LEVEL', DEFAULT['LBZ_LOG_LEVEL']), 
                        format=os.getenv('LBZ_LOG_FORMAT', DEFAULT['LBZ_LOG_FORMAT']),
                        handlers=handlers
    )

    data_dir = Path(os.getenv('LBZ_DATA_DIR', DEFAULT['LBZ_DATA_DIR'])).resolve()
    logging.info(f'Using data directory: {data_dir}')
    if not data_dir.is_dir(): 
        logging.info(f'Running mkdir on data directory')
        data_dir.mkdir()
    data_manager = data.DataManager(data_dir.joinpath('lbzdisc.json'))

    prefix = os.getenv('LBZ_BOT_PREFIX', DEFAULT['LBZ_BOT_PREFIX'])
    logging.info(f'Using command prefix: {prefix}')
    bot = commands.Bot(command_prefix = prefix)

    if data_manager.get_global_option('mode') is None:
        asyncio.run(data_manager.set_global_option('mode', os.getenv('LBZ_MODE', DEFAULT['LBZ_MODE'])))
    mode = data_manager.get_global_option('mode')
    logging.info(f'Using mode: {mode}')

    bot.add_cog(cogs.Core(bot, data_manager))

    token = os.getenv('LBZ_DISCORD_TOKEN')
    if token is None: 
        logging.error("No token set in LBZ_DISCORD_TOKEN")
        raise exceptions.MissingCriticalEnvironmentalVariable("Missing LBZ_DISCORD_TOKEN")
    bot.run(token)

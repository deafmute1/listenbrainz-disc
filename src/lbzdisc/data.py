import json
import logging 
from pathlib import Path

REQUIRED_KEYS = ('user', 'global')

class DataManager(): 
    def __init__(self, file: Path): 
        self.file = file

        if self.file.exists():
            with open(self.file, 'r') as f: 
                self.data =  json.load(f) 
        else: 
            self.data = {} 
        for key in REQUIRED_KEYS:
            if key not in self.data:
                self.data[key] = {}
        logging.debug(f'Initalised DataManager with self.data: {self.data}')

    async def set_global_option(self, option: str, value) -> None:
        self.data['global'][option] = value
        logging.debug(f'gldata {self.data}')
        await self._dump_json()

    def get_global_option(self, option: str): 
        try:
            return self.data['global'][option]
        except KeyError:
            return None

    async def set_user_for_id(self, disc_id: int, lbz_user: str) -> None: 
        disc_id = str(disc_id) # numbers cant be json keys
        if disc_id not in self.data['user']: 
            self.data['user'][disc_id] = {}
        self.data['user'][disc_id]['lbz_user'] = lbz_user 
        await self._dump_json()

    def get_user_by_id(self, disc_id: int) -> str: 
        try: 
            return self.data['user'][str(disc_id)]['lbz_user']
        except KeyError: 
            return None

    async def _dump_json(self): 
        with open(self.file, 'w') as f: 
            return json.dump(self.data ,f)
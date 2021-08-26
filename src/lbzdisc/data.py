import json 
from pathlib import Path

class DataManager(): 
    def __init__(self, file: Path): 
        self.file = file
        if self.file.exists():
            with open(self.file, 'r') as f: 
                self.data =  json.load(f)
        else: 
            self.data = {} 
        if "user" not in self.data: 
            self.data['user'] = {}

    async def set_user_for_id(self, disc_id: int, lbz_user: str) -> None: 
        disc_id = str(disc_id) # numbers cant be json keys
        if disc_id not in self.data['user']: 
            self.data['user'][disc_id] = {}
        self.data['user'][disc_id]['lbz_user'] = lbz_user 
        await self._dump_json()

    async def get_user_by_id(self, disc_id: int) -> str: 
        return self.data['user'][str(disc_id)]['lbz_user']

    async def _dump_json(self): 
        with open(self.file, 'w') as f: 
            return json.dump(self.data ,f)
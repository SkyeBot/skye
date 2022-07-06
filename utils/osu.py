import datetime
from typing import Any, Dict, Union
import aiohttp
from .default import date

class Osu:
    def __init__(self, *, client_id: int, client_secret: str, session: aiohttp.ClientSession):
        self.id = client_id
        self.secret = client_secret
        self.session: aiohttp.ClientSession = session
        self.API_URL = "https://osu.ppy.sh/api/v2"
        self. TOKEN_URL = "https://osu.ppy.sh/oauth/token"
    
    async def get_token(self):
        data = {
            "client_id": self.id,
            "client_secret":self.secret,
            'grant_type':'client_credentials',
            'scope':"public",
        }


        async with self.session.post(self.TOKEN_URL,data=data) as response:
            return (await response.json()).get("access_token")
    

    async def get_user(self, user: Union[str, int]):
        autorization = await self.get_token()
        headers = {
            "Content-Type": "application/json",
            "Accept":"application/json",
            "Authorization": f'Bearer {autorization}'
        }

        params = {
            "limit":5
        }
        async with self.session.get(self.API_URL+f"/users/{user}",headers=headers,params=params) as response:
            json = await response.json()



        return User(json)

    async def get_user_recent(self, user: Union[str, int]):
        autorization = await self.get_token()
        headers = {
            "Content-Type": "application/json",
            "Accept":"application/json",
            "Authorization": f'Bearer {autorization}'
        }

        params = {
            "limit":5
        }
        async with self.session.get(self.API_URL+f"/users/{user}/scores/recent",headers=headers,params=params) as response:
            json = await response.json()

        return json

    
    
    async def get_beatmap(self, beatmap: Union[str, int]) -> Dict[str, Any]: 
        authorization = await self.get_token()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {authorization}"
        }

        params = {

        }

        async with self.session.get(self.API_URL+f"/beatmaps/{beatmap}", headers=headers, params=params) as resp:
            json = await resp.json()

        return json

class User:
    def __init__(self, data):
        self.data = data
        self.joined_at = date(datetime.datetime.strptime(data['join_date'], '%Y-%m-%dT%H:%M:%S+00:00').timestamp(), ago=True)
        self.username = data['username']
        self._global_rank = str(data['statistics']['global_rank'])
        self._profile_order = data['profile_order']
        self.pp = data['statistics']['pp']
        self._rank = data['statistics']['grade_counts']
        self.accuracy = data['statistics']['hit_accuracy']
        self._country_rank = str(data['statistics']['country_rank'])
        self.country = data['country_code']
        self.avatar_url = data['avatar_url']



    @property
    def global_rank(self) -> Any:
        rank = self._global_rank[:3] + ',' + self._global_rank[3:] if int(self._global_rank) >  10000 else self._global_rank if int(self._global_rank) < 1000 else  self._global_rank[:1] + ',' + self._global_rank[1:]
        return rank
    
    @property
    def country_rank(self):
        rank = self._country_rank[:2] + ',' + self._country_rank[2:] if int(self._country_rank) > 10000 else self._country_rank if int(self._country_rank) < 1000 else  self._country_rank[:1] + ',' + self._country_rank[1:]
        return rank

            
    @property
    def profile_order(self) -> str:
        profile_order ='\n ​ ​ ​ ​ ​ ​ ​ ​  - '.join(x for x in self._profile_order)
        return profile_order

    @property
    def ranks(self) -> str:
        ss_text = self._rank['ss']
        ssh_text = self._rank['ssh']
        s_text = self._rank['s']
        sh_text = self._rank['sh']
        a_text = self._rank['a']
        return f"``SS {ss_text}`` | ``SSH {ssh_text}`` | ``S {s_text}`` | ``SH {sh_text}`` | ``A {a_text}``"


    @property
    def raw(self) -> Dict[str, any]:
        return self.data

class UserRecent:
    def __init__(self) -> None:
        pass

class Beatmap:
    def __init__(self, data):
        pass
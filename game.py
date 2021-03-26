from hashlib import md5, sha1
from json.decoder import JSONDecodeError

from asks import Session
import trio

from states import State, state, init_state, PAYLOAD

class GameSession(Session):
    def __init__(self):
        super().__init__(
                headers = {
                    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 8.0.0; Samsung Galaxy S8 - 8.0 - API 26 - 1440x2960 Build/OPR6.170623.017)',
                    'X-Unity-Version': '5.6.2p4'},
                persist_cookies=True,
                connections=2)

        self.user_id = None
        self.ev = None
        self.mobile_token = None


    def _get_default_payload(self):
        default = {
            'aid': self.user_id,
            'mobile': '1',
            'ev' : self.ev,
            'mobile_token': self.mobile_token
        }

        return {k:v for (k,v) in default.items() if k in PAYLOAD[state()]}

    def _get_base_url(self):
        if state() == State.NOT_LOGGED:
            return 'http://www.margonem.pl/ajax/logon.php?t=login'

        if state() == State.LOGGED_IN:
            return 'http://www.margonem.pl/ajax/getplayerdata.php'

        if state() in {State.INIT, State.ACTIVE}:
            return f'http://{self.game_server}.{self.server_name}/engine?'
        

    async def query_game(self, params={}):
        payload = self._get_default_payload() | params
        response = await self.post(url = self._get_base_url(), data=payload)
  
        try:#response.json() doesnt return None if thats not a json, not cool
            if json := response.json():
                if ev := json.get('ev'):
                    self.ev = ev
                if token := json.get('mobile_token'):
                    self.mobile_token = md5(b'ludzkastonoga-' + token.encode('utf-8')).hexdigest()

                return json
        except JSONDecodeError:
            return response.content


class Game():
    def __init__(self):
        init_state(State.NOT_LOGGED)

        self.session = GameSession()
        self.container = {}

    async def log_in(self, login: str, password: str):
        if state() == State.NOT_LOGGED:
            hashed_password = sha1(b'mleczko'+ password.encode('utf-8')).hexdigest()
            content = await self.session.query_game({
                                        'l': login,
                                        'ph': hashed_password})


            cookies = self.session._cookie_tracker.domain_dict['www.margonem.pl']
            if 'chash' in {cookie.name:cookie.value for cookie in cookies}:
                state(State.LOGGED_IN)

    async def get_player_data(self):
        if state() == State.LOGGED_IN:
            print(await self.session.query_game())


async def main():
    game = Game()
    await game.log_in('', '')
    await game.get_player_data()

trio.run(main)   
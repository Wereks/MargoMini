from hashlib import md5, sha1
from json.decoder import JSONDecodeError
from random import random

from asks import Session
from asks.cookie_utils import Cookie
import trio

from states import State, state, init_state, PAYLOAD

class GameSession(Session):
    def __init__(self):
        super().__init__(
                headers = {
                    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 8.0.0; Samsung Galaxy S8 - 8.0 - API 26 - 1440x2960 Build/OPR6.170623.017)',
                    'X-Unity-Version': '5.6.2p4',
                    'Connection': 'Keep-Alive',},
                connections=2)

        self.cookies = {}

        self.user_id = None
        self.ev = None
        self.mobile_token = None

        self.game_server = None


    def _get_default_payload(self):
        default = {
            'mucka': str(random()),
            'aid': self.user_id,
            'mobile': '1',
            'ev' : self.ev,
            'mobile_token': self.mobile_token,
        }

        return {k:v for (k,v) in default.items() if k in PAYLOAD[state()]}

    def _get_base_url(self):
        if state() == State.NOT_LOGGED:
            return 'http://www.margonem.pl/ajax/logon.php?t=login'

        if state() == State.LOGGED_IN:
            return 'http://www.margonem.pl/ajax/getplayerdata.php'

        if state() in {State.START_INIT, State.INIT}:
            return f'http://{self.game_server}.margonem.pl/engine?t=init'

        if state() == State.ACTIVE:
            return f'http://{self.game_server}.margonem.pl/engine?t=_'
        

    async def _send(self, payload):
        data = {}
        params = {}

        if state() in {State.NOT_LOGGED, State.LOGGED_IN}:
            data = payload
        elif state() in {State.START_INIT, State.INIT, State.ACTIVE}:
            params = payload

        return await self.post(url = self._get_base_url(), cookies=self.cookies, data=data, params=params)

        

    async def query_game(self, params={}):
        payload = params | self._get_default_payload()

        response = await self._send(payload)
        self.cookies.update({c.name:c.value for c in response.cookies})

        try:#response.json() doesnt return None if thats not a json, not cool
            if json := response.json():
                if ev := json.get('ev'):
                    self.ev = ev
                if token := json.get('mobile_token'):
                    self.mobile_token = md5(b'humantorch-' + token.encode('utf-8')).hexdigest()

                return json
        except JSONDecodeError:
            pass

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

            if 'chash' in self.session.cookies:
                state(State.LOGGED_IN)

    async def get_player_data(self):
        if state() == State.LOGGED_IN:
            print(await self.session.query_game())


    async def init(self, server, mchar_id):
        async def _init(lvl):
            return await self.session.query_game({'initlvl': lvl})

        if state() == State.LOGGED_IN:
            self.session.game_server = server
            self.session.cookies.update({'mchar_id': str(mchar_id)})

            state(State.START_INIT)
            await _init(1)

            state(State.INIT)
            for lvl in range(2,5)
                await _init(lvl)

            state(State.ACTIVE)
            self.keep_alive()

    async def keep_alive(self):
        pass



async def main():
    game = Game()
    await game.log_in('', '')
    #await game.get_player_data()
    await game.init('', '')

trio.run(main)   
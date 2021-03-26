from enum import Enum

class State(Enum):
    NOT_LOGGED = 0,
    LOGGED_IN = 1,
    START_INIT, INIT = 2, 3 
    ACTIVE = 4,

PAYLOAD = {
    State.ACTIVE: {'mobile', 'ev', 'mobile_token', 'mucka'},
    State.INIT : {'mobile', 'mobile_token', 'mucka'},
    State.START_INIT : {'mobile', 'mucka'},
    State.LOGGED_IN: {},
    State.NOT_LOGGED: {},
}


def init_state(new_state : State = None):
    global _state
    _state = State.NOT_LOGGED

    if new_state:
        _state = new_state
        

def state(new_state : State = None):  
    global _state
    
    if not new_state:
        return _state

    _state = new_state
from enum import Enum

class State(Enum):
    NOT_LOGGED = 0,
    LOGGED_IN = 1,
    INIT = 2, 
    ACTIVE = 3,

PAYLOAD = {
    State.ACTIVE: {'aid', 'mobile', 'ev', 'mobile_token'},
    State.INIT : {'aid', 'mobile', 'mobile_token'},
    State.LOGGED_IN: {'aid', 'mobile'},
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
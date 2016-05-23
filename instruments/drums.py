from . import Instrument

class Drums(Instrument):
    _parameters = [
        Parameter("fullness", set_fullness)
    ]
    
    def set_fullness(self):
        pass
    

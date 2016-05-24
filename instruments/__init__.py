from collections import namedtuple

class Instrument(object):
    def __init__(self, live_set):
        self.live_set = live_set
    
    @classmethod    
    def get_parameters(cls):
        return cls._parameters

    def set_parameter(self, parameter, value):
        cls._parameters[parameter].set_value_func(self, value)
        
        
Parameter = namedtuple("Parameter", ("name", "set_value_func",))

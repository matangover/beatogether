from collections import namedtuple

class Instrument(object):
    # Override this
    TRACK_NAME_BASE = None
    
    def __init__(self, live_set, role):
        self.live_set = live_set
        self.role = role
        self.player = None
    
    @classmethod    
    def get_parameters(cls):
        return cls._parameters

    def set_parameter(self, parameter, value):
        cls._parameters[parameter].set_value_func(self, value)
        
    def get_track_named(self, name):
    	""" Returns the Track with the specified name, or None if not found. """
    	for track in self.live_set.tracks:
    		if track.name == name:
    			return track
    	return None
        
    def get_track_name(self, base_name=None):
        base_name = base_name or self.TRACK_NAME_BASE
        return "%s %s" % (base_name, self.role)
        
    def get_track(self, base_name=None):
        return self.get_track_named(self.get_track_name(base_name))
        
    def tick(self, tick_count):
        pass

        
Parameter = namedtuple("Parameter", ("name", "set_value_func",))

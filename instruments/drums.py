from . import Instrument, Parameter

class Drums(Instrument):
    #CLIP_COUNT = 5
    
    def __init__(self, live_set):
        super(Drums, self).__init__(live_set)
        
    def set_clip_based_parameter(self, track_name, value):
        track = get_track_named(self.live_set, track_name)
        max_clip_index = len(track.clips)
        clip_index = int(round(value * max_clip_index))
        if clip_index > 0:
            track.clips[clip_index - 1].play()
        else:
            track.stop()
            
    def set_parameter1(self, value):
        self.set_clip_based_parameter("Kick", value)
        self.set_clip_based_parameter("Clap", value)
        
    def set_parameter2(self, value):
        self.set_clip_based_parameter("Hihat", value)
        self.set_clip_based_parameter("Bongos", value)
        self.set_clip_based_parameter("Tambourine", value)

    _parameters = [
        #Parameter("base", set_base)
    ]

def get_track_named(live_set, name):
	""" Returns the Track with the specified name, or None if not found. """
	for track in live_set.tracks:
		if track.name == name:
			return track
	return None

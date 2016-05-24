from . import Instrument, Parameter

class SynthHarmony(Instrument):
    def __init__(self, live_set):
        super(SynthHarmony, self).__init__(live_set)

    def set_volume(self, value):
        track = get_track_named(self.live_set, "Stab Synth")
        track.volume = value

def get_track_named(live_set, name):
	""" Returns the Track with the specified name, or None if not found. """
	for track in live_set.tracks:
		if track.name == name:
			return track
	return None

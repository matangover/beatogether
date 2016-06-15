from . import Instrument, Parameter

class SynthHarmony(Instrument):
    TRACK_NAME_BASE = "Stab Synth"
    
    def __init__(self, live_set, role):
        super(SynthHarmony, self).__init__(live_set, role)

    def tick(self, tick_count):
        if tick_count % 24 != 0 or not self.player:
            # Update only every beat
            return
        
        self.set_volume(self.player.param_values[3]) # Body z position
        # Set device parameters of "Beat Repeat": grid, pitch decay, (interval, variation)
        
    def set_volume(self, value):
        self.get_track().volume = value

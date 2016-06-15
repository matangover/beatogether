from . import Instrument, Parameter

class SynthHarmony(Instrument):
    TRACK_NAME_BASE = "Stab Synth"
    
    def tick(self, tick_count):
        super(SynthHarmony, self).tick(tick_count)
        # if self.role == 1 and tick_count % 24*4 == 0:
        #     print "Role 1. Player:", self.player
        #print "SYNTH HARMONY TICK"
        if not self.player:
            return
        # print "SYNTH HARMONY SET VOLUME"
        self.set_volume(self.player.param_values[3]) # Body z position
        # Set device parameters of "Beat Repeat": grid, pitch decay, (interval, variation)
        
    def set_volume(self, value):
        self.get_track().volume = value

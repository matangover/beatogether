import sys
import live
from instruments.drums import Drums
from instruments.synth_lead import SynthLead
from instruments.synth_harmony import SynthHarmony
from threading import Thread
import time
import mido
from primesense import nite2
from kinect import KinectInterface
import signal

class KinectLooper(object):
    def __init__(self):
        # TODO: add callback for user lost, to remove 'player' from instruments.
        self.kinect = KinectInterface(self.gesture_received, self.pose_detected)
        
    def start(self):
        self.start_ableton_thread()
        self.kinect.start()
        
    def start_ableton_thread(self):
        self.ableton_thread = Thread(target=self.ableton_thread_func)
        self.ableton_thread.daemon = True
        self.ableton_thread.start()

    def ableton_thread_func(self):
        self.live_set = live.Set()
        self.live_set.scan(scan_clip_names=True, scan_devices=True)
        self.beat_length = 60 / self.live_set.tempo 
        
        self.drums = Drums(self.live_set)
        self.melody = SynthLead(self.live_set)
        self.harmony = SynthHarmony(self.live_set)
        
        self.midi_clock_loop()
        
    def midi_clock_loop(self):
        clock_input = mido.open_input("IAC Driver IAC Bus 2")
        
        tick_count = 0
        # MIDI clock loop - 24 times in each beats
        # For 130 BPM, beat_length=6/13sec, so MIDI clock tick is every 1/52sec =~ 19.23ms.
        # One 1/16 note = 4 clock ticks =~ 80ms.
        for message in clock_input:
            if message.type == "start":
                tick_count = 0
            elif message.type == "clock":
                tick_count += 1
                if tick_count % 6 == 0:
                    #print "1/16 tick"
                    # We only update every sixteenth note (~80ms).
                    self.midi_tick(tick_count)
            
    def midi_tick(self, tick_count):
        self.melody.tick(tick_count)
        
        #print "Params: (%.3f, %.3f, %.3f, %.3f)" % self.kinect.param_values
        #self.drums.set_parameter1(right_hand)
        #self.drums.set_parameter2(left_hand)
        #self.melody.set_volume(1 - head_height)
        #self.harmony.set_volume(1 - body_depth)
        
    def gesture_received(self, user_id, hand, gesture):
        if gesture.type == nite2.c_api.NiteGestureType.NITE_GESTURE_CLICK:
            # TODO: check which player, use their own track. 
            # TODO: check other hand position to determine which track to activate.
            print "Setting melody player to user:", user_id
            self.melody.player = self.kinect.user_listener.tracked_users[user_id]
    
    def pose_detected(self, user_id, pose):
        pass

def main():
    looper = KinectLooper()
    looper.start()
    signal.pause()
    
if __name__ == "__main__":
    main()

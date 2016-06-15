import sys
import live
from instruments.drums import Drums
from instruments.synth_lead import SynthLead, scale_to_range
from instruments.synth_harmony import SynthHarmony
from threading import Thread
import time
import mido
from primesense import nite2
from kinect import KinectInterface, UserRole
import signal
import graphics

class KinectLooper(object):
    def __init__(self):
        # TODO: add callback for user lost, to remove 'player' from instruments.
        self.kinect = KinectInterface(self.gesture_received, self.pose_detected, self.user_added, self.user_removed, self.user_roles_changed)
        
    def start(self):
        self.start_ableton_thread()
        self.kinect.start()
        
    def start_ableton_thread(self):
        # Initialization is done on the main thread.
        self.live_set = live.Set()
        # Patch pylive's console dumping.
        self.live_set.dump = lambda *args: None
        self.live_set.scan(scan_clip_names=True, scan_devices=True)
        self.beat_length = 60 / self.live_set.tempo 
        
        self.user_tracks = {}
        self.active_tracks = {}
        for role in (UserRole.RIGHT_USER, UserRole.LEFT_USER):
            self.user_tracks[role] = {
                Track.MELODY: SynthLead(self.live_set, role, self.recording_ended),
                Track.HARMONY: SynthHarmony(self.live_set, role, self.recording_ended),
                Track.DRUMS: Drums(self.live_set, role, self.recording_ended)
            }
            self.active_tracks[role] = None

        self.ableton_thread = Thread(target=self.ableton_thread_func)
        self.ableton_thread.daemon = True
        self.ableton_thread.start()

    def ableton_thread_func(self):        
        self.midi_clock_loop()
        
    def midi_clock_loop(self):
        clock_input = mido.open_input("IAC Driver Clock")
        
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
                    
                if tick_count % (24 * 8) == 0:
                    self.log_status()
            
    def midi_tick(self, tick_count):
        for user_tracks in self.user_tracks.values():
            for track in user_tracks.values():
                track.tick(tick_count)
    
    def log_status(self):
        try:
            print "Tracked users:", [
                "id: %s, role: %s" % (user_id, user.role) \
                for user_id, user in self.kinect.user_listener.tracked_users.items()
            ]
            print "Active tracks:", self.active_tracks
        except:
            pass
        
    def gesture_received(self, user_id, hand, gesture):
        if gesture.type == nite2.c_api.NiteGestureType.NITE_GESTURE_CLICK:
            user = self.kinect.user_listener.tracked_users[user_id]
            if hand == nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_HAND:
                other_hand_angle = user.lh_angle
            else:
                other_hand_angle = user.rh_angle
                
            if other_hand_angle < 70:
                track = Track.MELODY
            elif other_hand_angle < 110:
                track = Track.HARMONY
            else:
                track = Track.DRUMS
            print "Other hand angle is:", other_hand_angle
            # TODO: Disabled for now - use for "effects" mode
            #self.activate_track(user_id, track)
    
    def activate_track(self, user_id, track):
        user = self.kinect.user_listener.tracked_users[user_id]
        role = user.role
        previous_track = self.active_tracks[role]
        if previous_track == track:
            print "Tried to activate track %s for user %s but it's already active" % (track, user_id)
            return
        
        print "Activating track %s for user %s (previous track: %s)" % (track, user_id, previous_track)
        self.active_tracks[role] = track
        if previous_track is not None:
            self.user_tracks[user.role][previous_track].deactivate()
            self.user_tracks[user.role][previous_track].player = None
        if track is not None:
            track = self.user_tracks[user.role][track]
            print "Set track! track=%s, user=%s" % (track, user)
            track.player = user
            track.activate()
            
    def pose_detected(self, user_id, pose):
        if pose == nite2.c_api.NitePoseType.NITE_POSE_PSI:
            user = self.kinect.user_listener.tracked_users.get(user_id)
            if not user:
                print "user_id %s doesn't exist yet in tracked_users, ignoring" % user_id
                return
                
            active_track = self.active_tracks[user.role]
            if active_track is None:
                print "Detected PSI for %s but no track is active" % user_id
                return
            print "Starting to record for role %s track %s" % (user.role, active_track)
            instrument = self.user_tracks[user.role][active_track]
            instrument.start_recording()
        
    def user_roles_changed(self):
        print "User roles changed! New roles:", [
            (user_id, user.role) for user_id, user
            in self.kinect.user_listener.tracked_users.items()
        ]
        # Activate drums track for all users.
        # TODO: Keep active tracks for existing user?
        for user_id in self.kinect.user_listener.tracked_users:
            self.activate_track(user_id, Track.DRUMS)
        
    def user_added(self, user_id):
        print "User added:", user_id
        
    def user_removed(self, user_id):
        print "User removed:", user_id
        self.activate_track(user_id, None)

    def recording_ended(self, role):
        print "Activating next track for role: %s" % role
        # Activate next track
        active_track = self.active_tracks[role]
        user_id = self.get_user_id_by_role(role)
        self.activate_track(user_id, (active_track + 1) % 3)
        
    def get_user_id_by_role(self, role):
        for user_id, user in self.kinect.user_listener.tracked_users.items():
            if user.role == role:
                return user_id


def main():
    looper = KinectLooper()
    looper.start()
    graphics.start(looper)
    #signal.pause()
    
class Track(object):
    DRUMS = 0
    HARMONY = 1
    MELODY = 2


    
if __name__ == "__main__":
    main()

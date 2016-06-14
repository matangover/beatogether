import math
from Person import Person
from primesense import openni2, nite2
import time

class KinectInterface(object):
    def __init__(self):
        self.visible_users = set()
        self.skeleton_state = {}
        self.tracked_users = {}
        self.last_ts = None
        
    def start(self):
        openni2.initialize()
        nite2.initialize()
        self.user_tracker = nite2.UserTracker(None)
        self.hand_tracker = nite2.HandTracker(None)
        self.hand_tracker.start_gesture_detection(nite2.c_api.NiteGestureType.NITE_GESTURE_CLICK)
        #self.hand_tracker.start_gesture_detection(nite2.c_api.NiteGestureType.NITE_GESTURE_WAVE)
        self.hand_listener = HandListener(self.hand_tracker)
        self.user_listener = UserListener(self.user_tracker)
        
    def stop(self):
        self.hand_listener.close()
        self.user_listener.close()
        nite2.unload()

    def get_joint_positions(self):
        positionList = []
        for i in range(15):
            position = self.skeleton.get_joint(i).position
            x, y = self.user_tracker.convert_joint_coordinates_to_depth(position.x, position.y, position.z)
            positionList.append((x,y))
        return positionList

class HandListener(nite2.HandTrackerListener):
    last_ts = None
    def on_ready_for_next_frame(self):
        if not self.hand_tracker:
            # Can happen while NiTE2 is being shut down.
            return
            
        frame = self.hand_tracker.read_frame()
        #self.log_frame_frequency()
        self.handle_frame(frame)
        
    def log_frame_frequency(self):
        frame_timestamp = time.time()
        if self.last_ts is not None:
            print "Time delta (HAND): %6d ms" % (1000 * (frame_timestamp - self.last_ts))
        self.last_ts = frame_timestamp
        
    def handle_frame(self, frame):
        for gesture in frame.gestures:
            gesture = nite2.GestureData(gesture)
            if gesture.is_complete():
                print "Gesture! Type:", gesture.type, " Position:", gesture.currentPosition
                

class UserListener(nite2.UserTrackerListener):
    def __init__(self, user_tracker):
        super(UserListener, self).__init__(user_tracker)
        self.last_ts = None
        self.visible_users = set()
        self.skeleton_state = {}
        self.tracked_users = {}

    def on_ready_for_next_frame(self):
        if not self.user_tracker:
            # Can happen while NiTE2 is being shut down.
            return
            
        frame = self.user_tracker.read_frame()
        frame_timestamp = time.time()
        #self.log_frame_frequency()
        self.handle_frame(frame, frame_timestamp)
        
    def log_frame_frequency(self):
        frame_timestamp = time.time()
        if self.last_ts is not None:
            print "Time delta (USER): %6d ms" % (1000 * (frame_timestamp - self.last_ts))
        self.last_ts = frame_timestamp
        
    def handle_frame(self, frame, frame_timestamp):
        for user in frame.users:
            self.start_tracking_if_needed(user)
            self.track_user_visibility(user)
            self.track_skeleton_state(user)
            self.update_skeleton(user, frame_timestamp)

    def start_tracking_if_needed(self, user):
        if user.is_new():
            print "Found new user, starting to track:", user.id
            self.user_tracker.start_skeleton_tracking(user.id)
            
    def track_user_visibility(self, user):
        if user.is_visible() and not user.id in self.visible_users:
            print "User #%s: Visible" % user.id
            self.visible_users.add(user.id)
        if not user.is_visible() and user.id in self.visible_users:
            print "User #%s: Out of scene" % user.id
            self.visible_users.remove(user.id)
        
    def track_skeleton_state(self, user):
        if user.id in self.skeleton_state and self.skeleton_state[user.id] != user.skeleton.state:
            if user.skeleton.state == nite2.c_api.NiteSkeletonState.NITE_SKELETON_NONE:
                print "User #%s: Stopped tracking" % user.id
            elif user.skeleton.state == nite2.c_api.NiteSkeletonState.NITE_SKELETON_CALIBRATING:
                print "User #%s: Calibrating..." % user.id
            elif user.skeleton.state == nite2.c_api.NiteSkeletonState.NITE_SKELETON_TRACKED:
                print "User #%s: Tracking!" % user.id
            else:
                print "User #%s: Calibration Failed... :-|"
            
        self.skeleton_state[user.id] = user.skeleton.state
        
    def update_skeleton(self, user, frame_timestamp):
        if user.skeleton.state == nite2.c_api.NiteSkeletonState.NITE_SKELETON_TRACKED:
            person = self.tracked_users.setdefault(user.id, Person(None, None))
            person.update_skeleton(user.skeleton, frame_timestamp)
        elif user.id in self.tracked_users:
            del self.tracked_users[user.id]

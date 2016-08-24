import math
from Person import Person, calcDist
from primesense import openni2, nite2
import time
import traceback

class KinectInterface(object):
    MAX_GESTURE_DISTANCE_FROM_JOINT = 500

    def __init__(self, gesture_callback, pose_callback, user_added_callback, user_removed_callback, user_roles_changed):
        self.gesture_callback = gesture_callback
        self.pose_callback = pose_callback
        self.user_added_callback = user_added_callback
        self.user_removed_callback = user_removed_callback
        self.user_roles_changed = user_roles_changed
        
    def start(self):
        openni2.initialize()
        nite2.initialize()
        self.user_tracker = nite2.UserTracker(None)
        self.hand_tracker = nite2.HandTracker(None)
        self.hand_tracker.start_gesture_detection(nite2.c_api.NiteGestureType.NITE_GESTURE_CLICK)
        #self.hand_tracker.start_gesture_detection(nite2.c_api.NiteGestureType.NITE_GESTURE_WAVE)
        self.hand_listener = HandListener(self.hand_tracker, self.gesture_received)
        self.user_listener = UserListener(self.user_tracker, self.pose_detected, self.user_added_callback, self.user_removed_callback, self.user_roles_changed)
        
    def stop(self):
        print "Closing Kinect interfaces"
        #self.hand_listener.close()
        #self.user_listener.close()
        #nite2.c_api.niteShutdown()
        #openni2.c_api.oniShutdown()
        nite2.unload()
        openni2.unload()
        print "Kinect interfaces closed"

    def get_joint_positions(self):
        positionList = []
        for user_id, user in self.user_listener.tracked_users.items():
            positions = []
            try:
                for i in range(15):
                    position = user.skeleton.get_joint(i).position
                    x, y = self.user_listener.user_tracker.convert_joint_coordinates_to_depth(position.x, position.y, position.z)
                    positions.append((x,y))
                positionList.append(positions)
            except:
                traceback.print_exc("Failed saving user position")
        return positionList
        
    def gesture_received(self, gesture):
        print "Gesture! Type:", gesture.type, " Position:", gesture.currentPosition
        hand_data = self.get_hand(gesture.currentPosition)
        if hand_data:
            user_id, hand = hand_data
            print "Gesture generated by", user_id, hand
            self.gesture_callback(user_id, hand, gesture)

    def get_hand(self, position):
        all_hands = []
        for user_id, user in self.user_listener.tracked_users.iteritems():
            for hand in (
                nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_HAND,
                nite2.c_api.NiteJointType.NITE_JOINT_LEFT_HAND
            ):
                hand_position = user.last_joint_positions[hand]
                hand_distance_from_gesture = calcDist(position, hand_position)
                all_hands.append((user_id, hand, hand_distance_from_gesture))
        
        if not all_hands:
            print "No hands tracked!"
            return None
        closest_hand = min(all_hands, key=lambda hand: hand[2])
        if closest_hand[2] > self.MAX_GESTURE_DISTANCE_FROM_JOINT:
            print "Can't find hand that generated gesture! Closest is %s mm away." % closest_hand[2]
            return None
            
        return closest_hand[:2]
    
    def pose_detected(self, user_id, pose_type):
        print "Pose detected! Type:", pose_type, " User:", user_id
        self.pose_callback(user_id, pose_type)

class HandListener(nite2.HandTrackerListener):
    def __init__(self, hand_tracker, gesture_callback):
        super(HandListener, self).__init__(hand_tracker)
        self.last_ts = None
        self.gesture_callback = gesture_callback
        
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
                self.gesture_callback(gesture)
                

class UserListener(nite2.UserTrackerListener):
    POSE_HOLD_MINIMUM_TIME = 1
    MAX_USERS = 2
    
    def __init__(self, user_tracker, pose_callback, user_added_callback, user_removed_callback, user_roles_changed):
        super(UserListener, self).__init__(user_tracker)
        self.last_ts = None
        self.visible_users = set()
        self.skeleton_state = {}
        self.tracked_users = {}
        self.users_poses = {}
        self.pose_callback = pose_callback
        self.user_added = user_added_callback
        self.user_removed = user_removed_callback
        self.user_roles_changed = user_roles_changed

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
            self.track_poses(user, frame_timestamp)
            
        self.update_roles()

    def start_tracking_if_needed(self, user):
        if not user.is_new():
            return
            
        if len(self.tracked_users) >= self.MAX_USERS:
            print "Found new user %s, but already tracking %s users - skipping" % (user.id, self.MAX_USERS)
            return
            
        print "Found new user, starting to track:", user.id
        self.user_tracker.start_skeleton_tracking(user.id)
        self.user_tracker.start_pose_detection(user.id, nite2.c_api.NitePoseType.NITE_POSE_PSI)
        self.user_tracker.start_pose_detection(user.id, nite2.c_api.NitePoseType.NITE_POSE_CROSSED_HANDS)
            
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
            person = self.tracked_users.get(user.id)
            if not person:
                person = Person()
                self.tracked_users[user.id] = person
                self.user_added(user.id)
            person.update_skeleton(user.skeleton, frame_timestamp)
        elif user.id in self.tracked_users:
            self.user_removed(user.id)
            del self.tracked_users[user.id]

    def track_poses(self, user, frame_timestamp):
        user_poses = self.users_poses.setdefault(user.id, {})
        for pose_type in (
            nite2.c_api.NitePoseType.NITE_POSE_PSI,
            nite2.c_api.NitePoseType.NITE_POSE_CROSSED_HANDS
        ):
            pose = user.get_pose(pose_type)
            if pose.is_entered():
                user_poses[pose_type] = frame_timestamp
            elif pose.is_held() or pose.is_exited():
                pose_start_time = user_poses.get(pose_type)
                if pose_start_time and frame_timestamp - pose_start_time >= self.POSE_HOLD_MINIMUM_TIME:
                    # Remove the pose so that it's not triggered again.
                    del user_poses[pose_type]
                    self.pose_callback(user.id, pose_type)
            
    def update_roles(self):
        users = self.tracked_users.items()
        changed = False
        
        if len(users) == 1:
            user_id, user = users[0]
            # If there's only one user, determine the role based on the X position.
            x_position = self.get_user_horizontal_position(users[0])
            new_role = UserRole.RIGHT_USER if x_position > 0 else UserRole.LEFT_USER
            if user.role != new_role:
                user.role = new_role
                changed = True
        elif len(users) == 2:
            rightmost_user_id, _ = max(users, key=self.get_user_horizontal_position)
            for user_id, user in users:
                if user_id == rightmost_user_id:
                    new_role = UserRole.RIGHT_USER
                else:
                    new_role = UserRole.LEFT_USER
                    
                if user.role != new_role:
                    user.role = new_role
                    changed = True
        else:
            #assert len(users) == 0
            if len(users) != 0:
                print "More than 2 users"
            
        if changed:
            self.user_roles_changed()
    
    @staticmethod
    def get_user_horizontal_position(user_item):
        # TODO: Use center of mass instead of torso
        user_id, user = user_item
        return user.skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_TORSO).position.x

class UserRole(object):
    LEFT_USER = 1
    RIGHT_USER = 2

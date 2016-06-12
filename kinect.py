####    https://github.com/leezl/OpenNi-Python/blob/master/primesense/nite2.py  ###


import math
from Person import Person
from primesense import openni2, nite2


class KinectInterface(object):
    def __init__(self):
        self.visible_users = set()
        self.skeleton_state = {}
        self.tracked_users = {}

    def start(self):
        openni2.initialize()
        nite2.initialize()
        self.user_tracker = nite2.UserTracker(None)
        self.user_tracker_loop()

    def get_joint_positions(self):
        positionList = []
        for i in range(15):
            position = self.skeleton.get_joint(i).position
            x, y = self.user_tracker.convert_joint_coordinates_to_depth(position.x, position.y, position.z)
            positionList.append((x,y))
        return positionList


    def user_tracker_loop(self):
        while True:
            frame = self.user_tracker.read_frame()
            for user in frame.users:
                if user.is_new():
                    print "Found new user, starting to track:", user.id
                    self.user_tracker.start_skeleton_tracking(user.id)

                if user.is_visible() and not user.id in self.visible_users:
                    print "User #%s: Visible" % user.id
                    self.visible_users.add(user.id)
                if not user.is_visible() and user.id in self.visible_users:
                    print "User #%s: Out of scene" % user.id
                    self.visible_users.remove(user.id)
                
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
                
                if user.skeleton.state == nite2.c_api.NiteSkeletonState.NITE_SKELETON_TRACKED:
                    #head = user.skeleton.joints[nite2.c_api.NiteJointType.NITE_JOINT_HEAD]
                    #if head.positionConfidence > 0.5:
                    #    print "User #%s: Head position (%5.2f, %5.2f, %5.2f)" % (user.id, head.position.x, head.position.y, head.position.z)
                    self.tracked_users[user.id] = Person(None, user)
                elif user.id in self.tracked_users:
                    del self.tracked_users[user.id]

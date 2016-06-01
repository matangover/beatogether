####    https://github.com/leezl/OpenNi-Python/blob/master/primesense/nite2.py  ###


import math
from Person import Person
from primesense import openni2, nite2


class KinectInterface(object):
    def __init__(self):
        self.tracked_people = []
        self.param_values = (0, 0, 0, 0, 0)
        self.skeleton = None

    def start(self):
        openni2.initialize("/usr/local/Cellar/openni2/2.2.0.33/lib/ni2")
        nite2.initialize("/Users/omerrom/Desktop/NiTE-2.0.0/Redist")
        dev = openni2.Device.open_any()
        self.user_tracker = nite2.UserTracker(dev)
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
            if len(frame.users) > 0:

                for i in range(0, len(frame.users)):
                    user = frame.users[i]
                    if user.state & 2 != 0:  # user.is_new() doesn't work
                        print "Found new user, starting to track:", user.id
                        roll = "Player"  # check where is the user and give him a roll
                        person = Person(roll, user)
                        self.tracked_people.append(user)
                        self.user_tracker.start_skeleton_tracking(user.id)
                    self.param_values = person.get_params()
                    print self.param_values

            #     #print "Found %s users" % len(frame.users)
            #     user = frame.users[0]
            #     i = 0
            #     #for i, user in enumerate(frame.users):
            #     if user.state & 2 != 0: # user.is_new() doesn't work
            #         print "Found new user, starting to track:", user.id
            #         self.user_tracker.start_skeleton_tracking(user.id)
            #     # if user.skeleton.state != nite2.c_api.NiteSkeletonState.NITE_SKELETON_TRACKED:
            #     #     print "User", i
            #     #     print "Skeleton state:", user.skeleton.state
            #     #     continue
            # #
            #
            #
            # ## vars:
            #     skeleton = nite2.Skeleton(user.skeleton)
            #     self.skeleton = skeleton
            #     head = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_HEAD)
            #     nack = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_NECK)
            #     torso = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_TORSO)
            #     right_hip = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_HIP)
            #     right_knee = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_KNEE)
            #     right_foot = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_FOOT)
            #     left_hand = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_LEFT_HAND)
            #     right_hand = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_HAND)
            #
            # ## get head position
            #     # head_pos = head.position.y
            #     # estimated_height = calcDist(head.position, nack.position) + \
            #     #       calcDist(nack.position, torso.position) + \
            #     #       calcDist(torso.position, right_hip.position) + \
            #     #       calcDist(right_hip.position, right_knee.position) + \
            #     #       calcDist(right_knee.position, right_foot.position)
            #     # head_pos = float(head_pos / estimated_height)
            #     # print "Height: ", estimated_height
            #     # print "Head: ", head_pos
            #     # print "Relative head position: ", head_pos / estimated_height * 100
            #
            #
            # ## get head position
            #     # to change before presentation!!
            #     max_head = 400
            #     min_head = -200
            #     relitive_head = min(1, max(0, float(head.position.y - min_head) / float(max_head - min_head)))
            #     # print "Raw head position: ", head.position.y
            #     #print "~~~~~~~~~~~~~~~~~~~~ Relative head position: ", relitive_head, "   ~~~~~~~~~~~~~~~~~~~~~~~"
            #
            #
            #
            # ## get hands distance
            #     hands_distance = calcDist(right_hand.position,left_hand.position)
            #     hands_distance_pos = min(float(hands_distance) / float(1000), 1)
            #     # print "~~~~~~~~~~~~~~~~~~~~ Hands Position: ", hands_distance, "   ~~~~~~~~~~~~~~~~~~~~~~~"
            #     #print "~~~~~~~~~~~~~~~~~~~~ Relative hand distance: ", hands_distance_pos
            #
            #
            # ## get body position (front-back)
            #     body_pos = torso.position.z
            #     min_dist = 1000
            #     max_dist = 3000
            #     relative_body_distance = float(body_pos - min_dist) / (max_dist - min_dist)
            #     relative_body_distance = min(1, max(0, relative_body_distance))
            #     # print "~~~~~~~~~~~~~~~~~~~~ Torso position: ", body_pos, "   ~~~~~~~~~~~~~~~~~~~~~~~"
            #
            #     #print "~~~~~~~~~~~~~~~~~~~~ Relative torso position: ", relative_body_distance
            #
            #
            # ## get hands y height
            #     min_hands = -150
            #     max_hands = 750
            #     left_hand_pos = float(left_hand.position.y - min_hands) / (max_hands - min_hands)
            #     left_hand_pos = min(1, max(0, left_hand_pos))
            #     #print "~~~~~~~~~~~~~~~~~~~~ Left Hand Y cord: ", left_hand_pos, "   ~~~~~~~~~~~~~~~~~~~~~~~"
            #     right_hand_pos = float(right_hand.position.y - min_hands) / (max_hands - min_hands)
            #     right_hand_pos = min(1, max(0, right_hand_pos))
            #     #print "~~~~~~~~~~~~~~~~~~~~ Right Hand Y cord: ", right_hand_pos, "   ~~~~~~~~~~~~~~~~~~~~~~~"
            #
            #     self.param_values = (right_hand_pos, left_hand_pos, relitive_head, relative_body_distance)
            #


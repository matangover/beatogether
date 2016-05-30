import math

from primesense import openni2, nite2

class Person(object):

    def __init__(self, role, user):
        self.role = role
        self.user = user
        self.param_values = [0, 0, 0, 0, 0]


    def get_params(self):
        skeleton = nite2.Skeleton(self.user.skeleton)
        head = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_HEAD)
        nack = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_NECK)
        torso = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_TORSO)
        right_hip = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_HIP)
        right_knee = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_KNEE)
        right_foot = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_FOOT)
        left_hand = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_LEFT_HAND)
        right_hand = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_HAND)


        #################       get hands y height       #################
        min_hands = -300
        max_hands = 820
        if left_hand.positionConfidence >= 0.5:
            left_hand_pos = float(left_hand.position.y - min_hands) / (max_hands - min_hands)
            left_hand_pos = min(1, max(0, left_hand_pos))
            self.param_values[0] = left_hand_pos
            # print "~~~~~~~~~~~~~~~~~~~~ Left Hand Y cord: ", left_hand.position.y, "   ~~~~~~~~~~~~~~~~~~~~~~~"

        if right_hand.positionConfidence >= 0.5:
            right_hand_pos = float(right_hand.position.y - min_hands) / (max_hands - min_hands)
            right_hand_pos = min(1, max(0, right_hand_pos))
            self.param_values[1] = right_hand_pos
            # print "~~~~~~~~~~~~~~~~~~~~ Right Hand Y cord: ", right_hand.position.y, "   ~~~~~~~~~~~~~~~~~~~~~~~"


        #################       get head position       #################
        max_head = 450
        min_head = -140
        if head.positionConfidence >= 0.5:
            relitive_head = min(1, max(0, float(head.position.y - min_head) / float(max_head - min_head)))
            # print "~~~~~~~~~~~~~~~~~~~~ Raw head position: ", head.position.y
            # print "~~~~~~~~~~~~~~~~~~~~ Relative head position: ", relitive_head, "   ~~~~~~~~~~~~~~~~~~~~~~~"
            self.param_values[2] = relitive_head


        #################       get body position (front-back)       #################
        if torso.positionConfidence >= 0.5:
            body_pos = torso.position.z
            min_dist = 1200
            max_dist = 2750
            relative_body_distance = float(body_pos - min_dist) / (max_dist - min_dist)
            relative_body_distance = min(1, max(0, relative_body_distance))
            self.param_values[3] = relative_body_distance
            # print "~~~~~~~~~~~~~~~~~~~~ Torso position: ", body_pos, "   ~~~~~~~~~~~~~~~~~~~~~~~"
            # print "~~~~~~~~~~~~~~~~~~~~ Relative torso position: ", relative_body_distance



        #################       get hands distance       #################
        if right_hand.positionConfidence >= 0.5 and left_hand.positionConfidence >= 0.5:
            hands_distance = calcDist(right_hand.position, left_hand.position)
            hands_distance_pos = min(float(hands_distance) / float(1000), 1)
            # print "~~~~~~~~~~~~~~~~~~~~ Hands Position: ", hands_distance, "   ~~~~~~~~~~~~~~~~~~~~~~~"
            # print "~~~~~~~~~~~~~~~~~~~~ Relative hand distance: ", hands_distance_pos
            self.param_values[4] = hands_distance_pos

        return self.param_values


# func to calc euclidean distance
def calcDist(right_position, left_position):
    return math.sqrt(pow(abs(right_position.x - left_position.x), 2) + \
                     pow(abs(right_position.y - left_position.y), 2) + \
                     pow(abs(right_position.z - left_position.z), 2))

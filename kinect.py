####    https://github.com/leezl/OpenNi-Python/blob/master/primesense/nite2.py  ###


import math

from primesense import openni2, nite2



def start(ut):

    while True:
        frame = ut.read_frame()
        if len(frame.users) > 0:
            print "Found %s users" % len(frame.users)
            for i, user in enumerate(frame.users):
                if user.state & 2 != 0: # user.is_new() doesn't work
                    print "Found new user, starting to track:", user.id
                    ut.start_skeleton_tracking(user.id)
                if user.skeleton.state != nite2.c_api.NiteSkeletonState.NITE_SKELETON_TRACKED:
                    print "User", i
                    print "Skeleton state:", user.skeleton.state
                    continue

                # for joint_type, joint_type_name in nite2.c_api.NiteJointType._values_.items():
                #     joint = user.skeleton.joints[joint_type]
                #     print joint_type_name, joint_type
                #     print joint

                    #print joint.jointType, joint.position.....


                ##  vars:
                skeleton = nite2.Skeleton(user.skeleton)
                #x, y = ut.convert_joint_coordinates_to_depth(head.position.x, head.position.y, head.position.z)

                head = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_HEAD)
                nack = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_NECK)
                torso = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_TORSO)
                right_hip = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_HIP)
                right_knee = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_KNEE)
                right_foot = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_FOOT)
                left_hand = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_LEFT_HAND)
                right_hand = skeleton.get_joint(nite2.c_api.NiteJointType.NITE_JOINT_RIGHT_HAND)

                # func to calc euclidean distance
                def calcDist(right_position, left_position):
                    return math.sqrt(pow(abs(right_position.x - left_position.x), 2) + \
                              pow(abs(right_position.y - left_position.y), 2) + \
                              pow(abs(right_position.z - left_position.z), 2))


            ## get head position
                # head_pos = head.position.y
                # estimated_height = calcDist(head.position, nack.position) + \
                #       calcDist(nack.position, torso.position) + \
                #       calcDist(torso.position, right_hip.position) + \
                #       calcDist(right_hip.position, right_knee.position) + \
                #       calcDist(right_knee.position, right_foot.position)
                # head_pos = float(head_pos / estimated_height)
                # print "Height: ", estimated_height
                # print "Head: ", head_pos
                # print "Relative head position: ", head_pos / estimated_height * 100


            ## get head position
                # to change before presentation!!
                max_head = 400;
                min_head = -200;
                relitive_head = float(head.position.y - min_head) / float(max_head - min_head)
                # print "Raw head position: ", head.position.y
                print "~~~~~~~~~~~~~~~~~~~~ Relative head position: ", relitive_head, "   ~~~~~~~~~~~~~~~~~~~~~~~"



            ## get hands distance
                hands_distance = calcDist(right_hand.position,left_hand.position)
                hands_distance_pos = min(float(hands_distance) / float(1000), 1)
                # print "~~~~~~~~~~~~~~~~~~~~ Hands Position: ", hands_distance, "   ~~~~~~~~~~~~~~~~~~~~~~~"
                print "~~~~~~~~~~~~~~~~~~~~ Relative hand distance: ", hands_distance_pos


            ## get body position (front-back)
                body_pos = torso.position.z
                min_dist = 1000
                max_dist = 3000
                relative_body_distance = float(body_pos - min_dist) / (max_dist - min_dist)
                relative_body_distance = min(1, max(0, relative_body_distance))
                # print "~~~~~~~~~~~~~~~~~~~~ Torso position: ", body_pos, "   ~~~~~~~~~~~~~~~~~~~~~~~"
                print "~~~~~~~~~~~~~~~~~~~~ Relative torso position: ", relative_body_distance


            ## get hands y height
                min_hands = -200
                max_hands = 750
                left_hand_pos = float(left_hand.position.y - min_hands) / (max_hands - min_hands);
                left_hand_pos = min(1, max(0, left_hand_pos))
                print "~~~~~~~~~~~~~~~~~~~~ Left Hand Y cord: ", left_hand_pos, "   ~~~~~~~~~~~~~~~~~~~~~~~"
                right_hand_pos = float(right_hand.position.y - min_hands) / (max_hands - min_hands);
                right_hand_pos = min(1, max(0, right_hand_pos))
                print "~~~~~~~~~~~~~~~~~~~~ Right Hand Y cord: ", right_hand_pos, "   ~~~~~~~~~~~~~~~~~~~~~~~"




if __name__ == "__main__":
    openni2.initialize("/usr/local/Cellar/openni2/2.2.0.33/lib/ni2")
    nite2.initialize("/Users/omerrom/Desktop/NiTE-2.0.0/Redist")
    dev = openni2.Device.open_any()
    ut = nite2.UserTracker(dev)
    start(ut)
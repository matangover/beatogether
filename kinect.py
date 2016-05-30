####    https://github.com/leezl/OpenNi-Python/blob/master/primesense/nite2.py  ###


import math
from Person import Person
from primesense import openni2, nite2


class KinectInterface(object):
    def __init__(self):
        self.tracked_people = []


    def start(self):
        openni2.initialize("/usr/local/Cellar/openni2/2.2.0.33/lib/ni2")
        nite2.initialize("/Users/omerrom/Desktop/NiTE-2.0.0/Redist")
        dev = openni2.Device.open_any()
        self.user_tracker = nite2.UserTracker(dev)
        self.user_tracker_loop()

    def user_tracker_loop(self):
        while True:
            frame = self.user_tracker.read_frame()
            if len(frame.users) > 0:

                for i in range(0, len(frame.users)):
                    user = frame.users[i]
                    if user.state & 2 != 0: # user.is_new() doesn't work
                        print "Found new user, starting to track:", user.id
                        roll = "Player"  # check where is the user and give him a roll
                        if user.id not in self.tracked_people:
                            person = Person(roll, user)
                            self.tracked_people.append(user.id)
                            self.user_tracker.start_skeleton_tracking(user.id)
                        params = person.get_params()
                        print params
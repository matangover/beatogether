from threading import Thread
from kinect import KinectInterface
import time

def start_kinect_tracking():
    global kinect
    kinect = KinectInterface()
    try:
        kinect.start()
    except KeyboardInterrupt:
        return

def start_monitor_thread():
    t = Thread(target=monitor_thread)
    t.daemon = True
    t.start()

def monitor_thread():
    while True:
        time.sleep(0.5)
        for user_id, user in kinect.tracked_users.iteritems():
            formatted_params = ", ".join("%.2f" % p for p in user.get_params())
            print "User %s: (%s)" % (user_id, formatted_params)
        
def main():
    start_monitor_thread()
    # This runs the kinect loop until Ctrl+C
    start_kinect_tracking()
    return



if __name__ == "__main__":
    main()

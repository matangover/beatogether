from threading import Thread, Event
from kinect import KinectInterface
import time
import signal

exit_event = Event()

def signal_handler(signal, frame):
        print "User pressed Ctrl+C!"
        exit_event.set()
signal.signal(signal.SIGINT, signal_handler)


def start_kinect_tracking():
    global kinect
    kinect = KinectInterface()
    kinect.start()
    
def start_monitor_thread():
    t = Thread(target=monitor_thread)
    t.daemon = True
    t.start()

def monitor_thread():
    while not exit_event.wait(1):
        for user_id, user in kinect.user_listener.tracked_users.iteritems():
            formatted_params = ", ".join("%.2f" % p for p in user.param_values)
            print "User %s: (%s)" % (user_id, formatted_params)
        
def main():
    start_kinect_tracking()
    start_monitor_thread()
    # This runs the kinect loop until Ctrl+C
    signal.pause()
    kinect.stop()

if __name__ == "__main__":
    main()

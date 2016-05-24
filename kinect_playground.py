import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
import live
from instruments.drums import Drums
from kinect import KinectInterface
from threading import Thread
import time

def start_kinect_tracking():
    global kinect
    kinect = KinectInterface()
    kinect.start()

def start_ableton_thread():
    t = Thread(target=ableton_thread)
    t.start()

def ableton_thread():
    live_set = live.Set()
    live_set.scan(scan_clip_names=True, scan_devices=True)
    drums = Drums(live_set)
    while True:
        time.sleep(0.1)
        param1, param2 = kinect.param_values
        print "Params: %s, %s" % kinect.param_values
        drums.set_parameter1(param1)
        drums.set_parameter2(param2)


def main():
    start_ableton_thread()
    start_kinect_tracking()


if __name__ == "__main__":
    main()
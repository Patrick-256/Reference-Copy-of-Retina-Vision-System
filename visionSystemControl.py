import time
import signal
import sys
import time
from visionSystem import VisionSystem
import os

DEBUG = False


os.chdir('/home/ubuntu/Retina2023') # can remove

vis = VisionSystem()
if DEBUG: print("DEBUG: vision system initialized!")

def process_stop_handler(signal, frame):
    print("CTRL-C pressed!\n Stopping program", file=sys.stderr)
    vis.stopPipeline()
    time.sleep(1)
    sys.exit(0)


signal.signal(signal.SIGINT, process_stop_handler)


def control_sig_handler(signal, frame):
    if DEBUG: print("DEBUG: Received Control signal")


signal.signal(signal.SIGUSR1, control_sig_handler)


def main():
    print("r", flush=True)
    while True:
        if DEBUG: print("DEBUG: waiting for signal...")
        signal.pause()  # Integrated version (comment for cmd line testing)
        if DEBUG: print("DEBUG: signal recieved!")

        # vis.showOneFrame() # Demo version

        if DEBUG: print("DEBUG: calling processOneFrame() ...")
        realx, realy, realz, orientation, confidence, tubeGrasped = vis.processOneFrame()  # Integrated version
        if DEBUG: print(f"DEBUG: done frame processing frame - real x,y,z, orientation, confidence, tubeGrasped: {realx}, {realy},{realz},{orientation},{confidence},{tubeGrasped}")
        # send coordinates to ARM TEAM
        # if no tube found, print "0"
        if(realx == -1 or realy == -1 or realz == -1 or orientation == -1):
            print("0", flush=True)
        else:
            print(f"x={int(realx * 10)},y={int(realy * 10)},z={int(realz * 10)},a={orientation},c={0.9},g={tubeGrasped}", flush=True)  # Integrated version

if __name__ == '__main__':
    sys.exit(main())

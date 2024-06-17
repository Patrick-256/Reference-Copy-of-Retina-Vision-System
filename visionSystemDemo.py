import pyrealsense2 as rs
import numpy as np
import cv2
import time
import torch
import math
import edge2
import signal
import sys
import time
from visionSystem import VisionSystem

DEBUG = True

vis = VisionSystem()
if DEBUG: print("DEBUG: vision system initialized!")

def process_stop_handler(signal, frame):
    print("CTRL-C pressed!\n Stopping program")
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
        # if DEBUG: print("DEBUG: waiting for signal...")
        # signal.pause()  # Integrated version
        # if DEBUG: print("DEBUG: signal recieved!")

        vis.showOneFrame() # Demo version

        # if DEBUG: print("DEBUG: calling processOneFrame() ...")
        # realx, realy, realz, orientation, confidence = vis.processOneFrame()  # Integrated version
        # if DEBUG: print(f"DEBUG: done frame processing frame - real x,y,z, orientation, confidence: {realx}, {realy},{realz},{orientation},{confidence}")
        # # send coordinates to ARM TEAM
        # # if no tube found, print "0" instead of -1,-1,-1,-1 etc.
        # if(realx == -1 or realy == -1 or realz == -1 or orientation == -1):
        #     print("0", flush=True)
        # else:
        #     print(f"x={realx},y={realy},z={realz},a={orientation},c={confidence}", flush=True)  # Integrated version

if __name__ == '__main__':
    sys.exit(main())

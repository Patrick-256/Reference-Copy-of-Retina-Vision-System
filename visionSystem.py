# boot pathing
import sys

sys.path.append("/home/ubuntu/Retina2023")
sys.path.append("/usr/local/lib")
sys.path.append("/usr/local/lib/python3.8/pyrealsense2")
sys.path.append("/us/local/lib/python3.10/pyrealsense2")
sys.path.append("/home/ubuntu/librealsense/build/Release")

import pyrealsense2 as rs
import numpy as np
import cv2
import time
import torch
import math
import edge2
import coordinateSystem

DEBUG = False

class VisionSystem:
    def __init__(
        self,
        directoryOfNNWeights="/home/ubuntu/Retina2023/",
        nameOfWeights="weights/sampleTubeWeights_May6.pt",
    ):
        self.model = torch.hub.load(
            directoryOfNNWeights, "custom", path=nameOfWeights, source="local"
        )
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.pipeline_running = True
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(self.config)
        self.color_frame = None
        self.depth_frame = None

        if DEBUG: print("DEBUG: vision system pipeline started!")
        if DEBUG: print("pyrealsense2 version:", rs.__version__)
        

    def stopPipeline(self):
        if self.pipeline_running: 
            if DEBUG: print("DEBUG: stopping vision system pipeline...")
            try:
                self.color_frame = None
                self.depth_frame = None
                cv2.destroyAllWindows()
                self.pipeline.stop()
            except Exception as e:
                print(f"Error stopping pipeline: {e}")
            
            if DEBUG: print("DEBUG: vision system pipeline stopped!")
            self.pipeline_running = False
        else:
            if DEBUG: print("DEBUG: attempted to stop vision system pipeline but pipeline not currently running")

    def processOneFrame(self):
        """
        Processes a frame and returns the x, y, z, orientation
        3 possible outputs
            int, int, int, int -> found a tube and all relevant info
            int, int, 0, int -> found a tube but couldnt get depth info
            -1, -1, -1, -1 -> no tube found
        """
        self.captureImage()
        results, confidence = self.checkForTube()
        realx, realy, realz, orientation, = self.getTubeData(results)
        # Release frames
        self.depth_frame = None
        self.color_frame = None

        tubeGrasped = 0
        if results is not None:
            if(results[5] == 0): # 1= MST, 0 = GT
                tubeGrasped = 1

        return realx, realy, realz, orientation, confidence, tubeGrasped

    def captureImage(self):
        frames = self.pipeline.wait_for_frames()
        self.depth_frame = frames.get_depth_frame()
        self.color_frame = frames.get_color_frame()

    def checkForTube(self):
        color_image = np.asanyarray(self.color_frame.get_data())
        results = self.model(color_image)
        results.render()
        highestConf = -1
        bestResults = None
        cv2.imwrite("VSView.jpg", results.ims[0])
        if not results.xyxy:
            return None

        for i in results.xyxy[0]: #  i[0]: xmin i[1]: ymin, i[2]: xmax, i[3]: ymax, i[4]: confidence, i[5]: class, i[6]: name
            if i[4] > highestConf:
                highestConf = i[4]
                bestResults = i
        return bestResults, round(float(highestConf), 2)

    def getTubeData(self, tubeResults):
        if tubeResults is not None:
            centerx, centery = self.getTubePixelCoordinates(tubeResults)
            depth = self.depth_frame.get_distance(centerx, centery) * 100
            # X (forward) = tubeCoordinates[0], Y (height) = tubeCoordinates[1], Z (right/left) = tubeCoordinates[2]
            tubeCoordinates = coordinateSystem.determineCoords(centery,centerx,depth)
            orientation = self.getTubeOrientation(tubeResults, centerx, centery)
            return round(tubeCoordinates[0],2), round(tubeCoordinates[1],2), round(tubeCoordinates[2],2), round(orientation,2)
        return -1, -1, -1, -1

    def getTubePixelCoordinates(self, tubeResults):
        centerx = int((tubeResults[0] + tubeResults[2]) / 2)
        centery = int((tubeResults[1] + tubeResults[3]) / 2)
        return centerx, centery

    def getTubeOrientation(self, tubeResults, centerx, centery):
        xdist = tubeResults[0] - tubeResults[2]
        ydist = tubeResults[1] - tubeResults[3]
        ratio = xdist / ydist

        if ratio > 4.75:
            return 90
        elif ratio < 0.55:
            return 0

        color_image = np.asanyarray(self.color_frame.get_data())
        return int(
            edge2.get_degrees(
                (int(tubeResults[0]), int(tubeResults[1])),
                (int(tubeResults[2]), int(tubeResults[3])),
                (centerx, centery),
                color_image,
            )
        )

    def showOneFrame(self):
        """
        Processes a frame and outputs image annotated with coordinates
            int, int, int, int -> found a tube and all relevant info
            int, int, 0, int -> found a tube but couldnt get depth info
            -1, -1, -1, -1 -> no tube found
        Does not write any images to disk
        """
        self.captureImage()
        results, confidence, image = self.checkForTubeWithImage()
        real_x, real_y, real_z, orientation = self.getTubeData(results)
        grasped = 0
        if results is not None:
            if results[5] == 0: # 1= MST, 0 = GT
                grasped = "true"
            cv2.putText(
                image,
                "Tube Grasped: " + grasped, 
                (10, 390),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
            )
        cv2.putText(
            image,
            "X-Coord: " + str(round(real_x, 2)),
            (10, 410),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
        )
        cv2.putText(
            image,
            "Y-Coord: " + str(round(real_y, 2)),
            (10, 430),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
        )
        cv2.putText(
            image,
            " Z-Coord: "+ str(round(real_z, 2)),
            (10, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
        )
        cv2.putText(
            image,
            "Orientation: " + str(round(orientation, 2)),
            (10, 470),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
        )
        # print("\nreal coords:", real_x, real_y, depth, "\n\n")
        print(f"Confidence: {confidence}")
        print(f"integrated version output: x={int(real_x * 10)},y={int(real_y * 10)},z={int(real_z * 10)},a={orientation},c={0.9},g={grasped}")
        # cv2.circle(results.ims[0], (centerx, centery), 5, (0,0,255), 2) # Circle center of tube
        # Show image
        cv2.namedWindow("RealSense", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("RealSense", image)

        # Release frames
        self.depth_frame = None
        self.color_frame = None
        cv2.waitKey(1)  # show window for 1 millisecond or until a key is pressed

    def checkForTubeWithImage(self):
        """
        Check for tube witht he model but do not save image to disk and instead
        return the image along with the best results.
        """
        color_image = np.asanyarray(self.color_frame.get_data())
        results = self.model(color_image)
        results.render()
        highestConf = -1
        bestResults = None
        if not results.xyxy:
            return None

        for i in results.xyxy[0]:
            if i[4] > highestConf:
                highestConf = i[4]
                bestResults = i
        return bestResults, round(float(highestConf), 2), results.ims[0]


# vs = VisionSystem()
# while(True):
# print(vs.processOneFrame())
# time.sleep(1)

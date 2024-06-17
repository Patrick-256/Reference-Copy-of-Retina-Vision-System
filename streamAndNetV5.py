import pyrealsense2 as rs
import numpy as np
import cv2
import time
import torch
import math
import edge
import coordinateSystem

# MAIN

import signal
import sys

# program status
RUNNING = True


# Handle sigint
def signal_handler(signal, frame):
    global RUNNING
    print("Received sigint")
    RUNNING = False


signal.signal(signal.SIGINT, signal_handler)

# Build Neural Net
model = torch.hub.load(
    "/home/ubuntu/Retina2023/",
    "custom",
    path="weights/best_Retina2023.pt",
    source="local",
)

# Set up pipeline
pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)
i = 0
try:
    while RUNNING:
        print(RUNNING)

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET
        )

        image = color_image.copy()
        results = model(image)
        results.render()
        print(image.shape)
        print(color_image.shape)
        if len(results.xyxy) > 0 and len(results.xyxy[0]) > 0:
            centery = int((results.xyxy[0][0][1] + results.xyxy[0][0][3]) / 2)
            centerx = int((results.xyxy[0][0][0] + results.xyxy[0][0][2]) / 2)
            depth = depth_frame.get_distance(centerx, centery) * 100

            if depth > 0:
                # Determine coordinates of the tube
                coordinates = coordinateSystem.determineCoords(centery,centerx,depth)

                xdist = results.xyxy[0][0][0] - results.xyxy[0][0][2]
                ydist = results.xyxy[0][0][1] - results.xyxy[0][0][3]
                ratio = xdist / ydist
                if ratio > 3:
                    orient = "Orientation: 90.00"
                elif ratio < 0.55:
                    orient = "Orientation: 0.00"
                else:
                    print("EDGE!! \n")
                    print(results.xyxy[0][0])
                    orient = "Orientation: " + str(
                        round(
                            edge.get_degrees(
                                (
                                    int(results.xyxy[0][0][0]),
                                    int(results.xyxy[0][0][1]),
                                ),
                                (
                                    int(results.xyxy[0][0][2]),
                                    int(results.xyxy[0][0][3]),
                                ),
                                (centerx, centery),
                                color_image,
                            ),
                            2,
                        )
                    )

                print("Ratio: " + str(ratio) + "\n")
                i += 1
                cv2.imwrite(
                    time.strftime("%Y%m%d-%H%M%S") + " no coord.jpg", results.ims[0]
                )
                cv2.putText(
                    results.ims[0],
                    "X-Coord (forward): " + str(round(coordinates[0], 2)),
                    (10, 390),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                )
                cv2.putText(
                    results.ims[0],
                    "Y-Coord (height): " + str(round(coordinates[1], 2)),
                    (10, 410),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                )
                cv2.putText(
                    results.ims[0],
                    "Z-Coord (right): " + str(round(coordinates[2], 2)),
                    (10, 430),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                )
                cv2.putText(
                    results.ims[0],
                    "   Depth: " + str(round(depth, 2)),
                    (10, 450),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                )
                cv2.putText(
                    results.ims[0],
                    orient,
                    (10, 470),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                )
                # print("\nreal coords:", real_x, real_y, depth, "\n\n")
                cv2.circle(results.ims[0], (centerx, centery), 5, (0, 0, 255), 2)

                # print("x coordinate: " + str((centerx - 320) * depth_frame.get_distance(centerx, centery) /386))
                # print("y coordinate: " + str((centery - 240) * depth_frame.get_distance(centerx, centery) /386))
                # print("Tube is " + str(depth_frame.get_distance(centerx, centery)) + " m away")
                # print("Rotate " + str(real_xy_angle * 180 / math.pi) + " degrees in the xy plane and " + str(real_depth_angle * 180 / math.pi) + "degrees in the z plane")

        images = np.hstack((image, depth_colormap))
        # Display image on the screen
        cv2.namedWindow("RealSense", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("RealSense", results.ims[0])

        # Save the image to disk
        #cv2.imwrite(str(i + 9) + "cords.jpg", results.ims[0])
        #cv2.waitKey(1)
finally:
    print("finally")
    print(RUNNING)
    # Stop streaming
    cv2.destroyAllWindows()
    print("CLOSE ALL WINDOWS")
    pipeline.stop()
    print("PIPILINE STOP")
    exit()

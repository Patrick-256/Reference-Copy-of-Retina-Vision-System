# Patrick Whitlock  2024-01-18
#
# Calculates the coordinates of a point in space that is in view of a depth-perception camera
# Requires the pixel location of the point:
#       camPxHeight: amount of pixels from the base of the view up to the point
#       camPxFromCenter: amount of pixels (to the left or right) from the vertical centerline
#                        of the view. The left side is negative.
#       depth: the actual measured depth reading for the given pixel.

# CALIBRATION INSTRUCTIONS
# 1. Ensure that camera is fixed and the area ahead is flat. A table works well. The camera must not 
#    move during the calibration process.
# 2. Using a square or any right-angle, draw a dot on the table directly below the camera lenses.
# 3. Measure the height of the camera, record it in the cameraHeight value in the code below.
# 4. Connect a monitor to Kria Board, run visionSystemDemo.py
# 5. On the bottom of the window that shows what the camera sees, the coordinates of the mouse
#    cursor is shown. Hover the mouse over bottom center of the window, on coordinates x= 320, y= 480
# 6. Draw a dot on the surface ahead of the camera so that the dot is directly under the mouse cursor
#    on the monitor.
# 7. Measure the distance between this dot and the base of the camera. Record the value as blindspotDist
#    in the code below.
# 8. Move the mouse cursor 40 pixels to the left to 280,480 and draw the corrisponding dot on the table.
# 9. Move the mouse cursor to the right to 360,480 and draw the corrisponding dot.
# 10. There should now be 3 dots in a line at the bottom of the camera's view. Measure the distances
#     between each one, and take the average. (Ideally, they should already be the same). Record this 
#     value as KDzAA in the code below.
# 11. Move the mouse cursor up 40px, to 360,440. Draw the dot. repeat for 320,440 and 280,440
# 12. Measure the distance between the two center dots (the dots at 320,480 and 320, 440). Record this 
#     value as KDxA in the code below.
# 13. Measure the distance between the side dots and the center dot, take the average, and record value
#     as KDzA1
# 14. Move the mouse cursor to 280,400 , 320,400 and 360,400 and draw dots for each point
# 15. measure the distance between that center dot and the base center dot (the dots at 320,400 and 320,480)
#     and record that value as KDxB in the code below
# 16. Measure the average distances of each side dot to the center dot and record as KDzB1 in the code below
# 17. Keep following the pattern of moving the cursor to the pixel coordinates, all in 40px increments, and
#     drawing the dots on the surface ahead of the camera. You may find it more effient to draw all the dots
#     first, then measure everything at the end. Below are all the values and corrisponding pixel coordinates.
#     If the camera is angled high so that the top of the view shows stuff that is more than 2 meters away, you
#     can extrapolate instead of trying to measure.


# Define constants - all values in cm
cameraHeight = 28.4
blindspotDist = 11 #amount of centiemeters between the base of the camera and the base of the camera's view

#Measured 2024-02-29 with camera glued to rover
#Known Distances (in the X direction)
KDxA = 2.6 # Measured between dots (320,480) to (320,440)
KDxB = 6.1 # Measured between dots (320,480) to (320,400)
KDxC = 9.7 # Measured between dots (320,480) to (320,360)
KDxD = 14.4 # Measured between dots (320,480) to (320,320)
KDxE = 20 # Measured between dots (320,480) to (320,280)
KDxF = 27.1 # Measured between dots (320,480) to (320,240)
KDxG = 36.6 # Measured between dots (320,480) to (320,200)
KDxH = 49.5 # Measured between dots (320,480) to (320,160)
KDxI = 68.7 # Measured between dots (320,480) to (320,120)
KDxJ = 96.5 # Measured between dots (320,480) to (320,80)
KDxK = 120 # Measured between dots (320,480) to (320,40)
KDxL = 160 # Measured between dots (320,480) to (320,0)

# Known Distances (in the z direction) measured at each Known Distance checkpoint, incrementing every 40 pixels
KDzAA = 2.7 #Average distance between dots [(280,480) and (320,480)] and [(320,480) and (360,480)]
KDzA1 = 2.9 #Average distance between dots [(280,440) and (320,440)] and [(320,440) and (360,440)]
KDzB1 = 3.1 #Average distance between dots [(280,400) and (320,400)] and [(320,400) and (360,400)]
KDzC1 = 3.4 #Average distance between dots [(280,360) and (320,360)] and [(320,360) and (360,360)]
KDzD1 = 3.7 #Average distance between dots [(280,320) and (320,320)] and [(320,320) and (360,320)]
KDzE1 = 4.3 #Average distance between dots [(280,280) and (320,280)] and [(320,280) and (360,280)]
KDzF1 = 4.9 #Average distance between dots [(280,240) and (320,240)] and [(320,240) and (360,240)]
KDzG1 = 5.5 #Average distance between dots [(280,200) and (320,200)] and [(320,200) and (360,200)]
KDzH1 = 6.3 #Average distance between dots [(280,160) and (320,160)] and [(320,160) and (360,160)]
KDzI1 = 8.2 #Average distance between dots [(280,120) and (320,120)] and [(320,120) and (360,120)]
KDzJ1 = 11 #Average distance between dots [(280,80) and (320,80)] and [(320,80) and (360,80)]
KDzK1 = 14 #Average distance between dots [(280,40) and (320,40)] and [(320,40) and (360,40)]
KDzL1 = 18 #Average distance between dots [(280,0) and (320,0)] and [(320,0) and (360,0)]

import math

debug = False

def determineCoords(camPxFromTop,camPxFromLeft,depth):
    camPxHeight = 480-camPxFromTop
    camPxFromCenter = camPxFromLeft - 320

    baseCoordinates = calcBaseCoords(camPxHeight,camPxFromCenter)

    if(debug): print(f"Base Coords: X:{round(baseCoordinates[0],2)} Y:0 Z:{round(baseCoordinates[1],2)}")

    calculatedDepth = round(calcBaseDepth(baseCoordinates),2)
    if(debug): print(f"Base depth calculation: {calculatedDepth}")
    deltaDepth = calculatedDepth - depth

    # apply plane offset based on the difference of measured and calculated depth
    a1 = math.asin(cameraHeight / calculatedDepth)
    if(baseCoordinates[1] == 0): baseCoordinates[1] = 0.01
    a2 = math.atan(baseCoordinates[0] / baseCoordinates[1])
    c = math.cos(a1)*deltaDepth
  
    offset_x = round(abs(math.sin(a2) * c),2)
    offset_z = round(math.cos(a2) * c,2)
    if(deltaDepth > 0):
        offset_x = -round(abs(math.sin(a2) * c),2)
    if(camPxFromCenter > 0):
        offset_z = -round(math.cos(a2) * c,2)

    offset_y = round(math.sin(a1) * deltaDepth,2)
    if(debug): print(f"OFFSET Coords: X:{offset_x} Y:{offset_y} Z:{offset_z}")
    if(debug): print(f"Final Coords: X:{baseCoordinates[0]+offset_x} Y:{offset_y} Z:{baseCoordinates[1]+offset_z}")
    return [round(baseCoordinates[0]+offset_x,2), round(offset_y,2), round(baseCoordinates[1]+offset_z,2)]

def calcBaseDepth(baseCoordinates):
    return math.sqrt(pow(cameraHeight,2) +
                     pow(baseCoordinates[0],2) +
                     pow(baseCoordinates[1],2))

def calcBaseCoords(camPxHeight,camPxFromCenter):
    if(debug): print(f"camPxHeight: {camPxHeight} camPxFromCenter: {camPxFromCenter}")
    KDx = 0
    KDxNext = KDxA
    KDxPast = 0
    KDPx = 0

    KDz = KDzAA
    KDzNext = KDzA1

    if(camPxHeight >= 40):
        KDxPast = 0
        KDx = KDxA
        KDxNext = KDxB
        KDPx = 40

        KDz = KDzA1
        KDzNext = KDzB1
    if(camPxHeight >= 80):
        KDxPast = KDxA
        KDx = KDxB
        KDxNext = KDxC
        KDPx = 80

        KDz = KDzB1
        KDzNext = KDzC1
    if(camPxHeight >= 120):
        KDxPast = KDxB
        KDx = KDxC
        KDxNext = KDxD
        KDPx = 120

        KDz = KDzC1
        KDzNext = KDzD1
    if(camPxHeight >= 160):
        KDxPast = KDxC
        KDx = KDxD
        KDxNext = KDxE
        KDPx = 160

        KDz = KDzD1
        KDzNext = KDzE1
    if(camPxHeight >= 200):
        KDxPast = KDxD
        KDx = KDxE
        KDxNext = KDxF
        KDPx = 200

        KDz = KDzE1
        KDzNext = KDzF1
    if(camPxHeight >= 240):
        KDxPast = KDxE
        KDx = KDxF
        KDxNext = KDxG
        KDPx = 240

        KDz = KDzF1
        KDzNext = KDzG1
    if(camPxHeight >= 280):
        KDxPast = KDxF
        KDx = KDxG
        KDxNext = KDxH
        KDPx = 280

        KDz = KDzG1
        KDzNext = KDzH1
    if(camPxHeight >= 320):
        KDxPast = KDxG
        KDx = KDxH
        KDxNext = KDxI
        KDPx = 320

        KDz = KDzH1
        KDzNext = KDzI1
    if(camPxHeight >= 360):
        KDxPast = KDxH
        KDx = KDxI
        KDxNext = KDxJ
        KDPx = 360

        KDz = KDzI1
        KDzNext = KDzJ1
    if(camPxHeight >= 400):
        KDxPast = KDxI
        KDx = KDxJ
        KDxNext = KDxK
        KDPx = 400

        KDz = KDzJ1
        KDzNext = KDzK1
    if(camPxHeight >= 440):
        KDxPast = KDxJ
        KDx = KDxK
        KDxNext = KDxL
        KDPx = 440

        KDz = KDzK1
        KDzNext = KDzL1

    baseXcoord = 0
    # Original before height ratio implementation
    # baseXcoord = (blindspotDist + KDx +((camPxHeight - KDPx) / 40)*(KDxNext - KDx))
    
    blockHalfRatio = calcRatio(KDxNext,KDx,KDxPast)
    heightRatio = ((camPxHeight - KDPx) / 40)
    if( heightRatio <= 0.5):
        baseXcoord = (blindspotDist + KDx + (KDxNext - KDx)*(1-blockHalfRatio)*(2*heightRatio))
    else:
        baseXcoord = (blindspotDist + KDx + (KDxNext - KDx)*(blockHalfRatio)*(heightRatio-0.5) + (KDxNext - KDx)*(1-blockHalfRatio))

    
    numZblocks = math.floor(abs(camPxFromCenter) / 40)

    KDPz = numZblocks * 40

    blockHeightRatio = (camPxHeight - KDPx) / 40
    blockWidthRatio = (abs(camPxFromCenter) - KDPz) / 40

    baseZcoord = ((numZblocks*KDz)+(blockWidthRatio*KDz))*(1-blockHeightRatio) + ((numZblocks*KDzNext)+(blockWidthRatio*KDzNext))*blockHeightRatio
    if(camPxFromCenter < 0):
        baseZcoord = baseZcoord*(-1)

    return [round(baseXcoord,2), round(baseZcoord,2)]

def calcRatio(KDx2,KDx1,KDx0):
    return (KDx2 - KDx1) / ((KDx2 - KDx1) + (KDx1 - KDx0))
    

# =========================================================================================
# Test values here
pxFromLeft = 340
pxFromTop = 220
depth = 80 #depth as measured by the camera at the pixel defined by the past two values

testCoords = determineCoords(pxFromTop,pxFromLeft,depth)

#print(f"BlockHalf Ratio test: {calcRatio(KDxB,KDxA,0)}")
#=========================================================================================
import cv2
from math import atan, degrees
#top left (x,y) representing top left corner of tube box
#bottom right (x,y) same as above
#center (x,y) same as above
def get_degrees(top_left, bottom_right, center, img):
	# Find top left pixel of sample tube
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img_out = cv2.Canny(gray, 100, 150)
	first_white_col, first_white_row = top_left[1], top_left[0]
	done = 0
	for row in range(top_left[0], bottom_right[0] - 1):
	    for col in range(top_left[1], bottom_right[1] - 1):
	        if img_out[col][row] > 0 and col >= top_left[1] and row >= top_left[0] and col <= bottom_right[1] and row <= bottom_right[0]:
	            first_white_col, first_white_row = col, row
	            done = 1
	            break
	    if done:
	        break
	
    # Use bounding box corners to determine orientation
	# tan_triangle = abs(bottom_right[1] - top_left[1]) / abs(bottom_right[0] - top_left[0])
	# degrees_off_axis =  90 - degrees(atan(tan_triangle))
	# # If the top left pixel of the tube is to the right of center
	# if(first_white_col > center[1]):
	# 	degrees_off_axis = 180 - degrees_off_axis
	#print(f"First white pixel: {first_white_col} {first_white_row}")
	#print(f"Center: {center[0]}, {center[1]}")
	#print(f"Degrees from y-axis = {degrees_off_axis} and {done}")
	tan_triangle = abs(bottom_right[1] - top_left[1]) / abs(bottom_right[0] - top_left[0])
	degrees_off_axis = 90 - degrees(atan(tan_triangle))
	# If the top left pixel of the tube is to the right of center
	if(first_white_col < center[1]):
		degrees_off_axis = -1 * degrees_off_axis
	return(degrees_off_axis)

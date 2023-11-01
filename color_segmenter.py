#!/usr/bin/env python3

import cv2
import numpy as np
from functools import partial
import json

#....Program initialization....
vid = cv2.VideoCapture(0)
alpha_slider_max = 255	#Maximum value of the trackbars
title_window = 'frame'

#....Function to generate a thresholded image....
def on_trackbar(val, channel, image_data):
	
	#Translating values
	min_blue_thr = cv2.getTrackbarPos(b_min_trackbar, title_window)
	min_green_thr = cv2.getTrackbarPos(g_min_trackbar, title_window)
	min_red_thr = cv2.getTrackbarPos(r_min_trackbar, title_window)
	max_blue_thr = cv2.getTrackbarPos(b_max_trackbar, title_window)
	max_green_thr = cv2.getTrackbarPos(g_max_trackbar, title_window)
	max_red_thr = cv2.getTrackbarPos(r_max_trackbar, title_window)

	#Appling the threshold
	_,image_blue = cv2.threshold(image_data['b'], min_blue_thr, max_blue_thr, cv2.THRESH_BINARY)
	_,image_green = cv2.threshold(image_data['g'], min_green_thr, max_green_thr, cv2.THRESH_BINARY)
	_,image_red = cv2.threshold(image_data['r'], min_red_thr, max_red_thr, cv2.THRESH_BINARY)

	image_thresholded_2 = cv2.merge((image_blue,image_green,image_red))
#....Camera initialization....
ret, frame = vid.read()
cv2.imshow(title_window, frame)

#....Creating first frame to initialize window and trackbars....
b ,g ,r = cv2.split(frame)
image_data={'b':b, 'g':g, 'r':r}
r_min_trackbar = 'R Min'
r_max_trackbar = 'R Max'
g_min_trackbar = 'G Min'
g_max_trackbar = 'G Max'
b_min_trackbar = 'B Min'
b_max_trackbar = 'B Max'

cv2.createTrackbar(r_min_trackbar, title_window, 100, alpha_slider_max, partial(on_trackbar, channel='Rmin',image_data=image_data))
cv2.createTrackbar(r_max_trackbar, title_window, 255, alpha_slider_max, partial(on_trackbar, channel='Rmax',image_data=image_data))
cv2.createTrackbar(g_min_trackbar, title_window, 100, alpha_slider_max, partial(on_trackbar, channel='Gmin',image_data=image_data))
cv2.createTrackbar(g_max_trackbar, title_window, 255, alpha_slider_max, partial(on_trackbar, channel='Gmax',image_data=image_data))
cv2.createTrackbar(b_min_trackbar, title_window, 100, alpha_slider_max, partial(on_trackbar, channel='Bmin',image_data=image_data))
cv2.createTrackbar(b_max_trackbar, title_window, 255, alpha_slider_max, partial(on_trackbar, channel='Bmax',image_data=image_data))

while (True):
	#....Updating Camera....
	ret, frame = vid.read()
	
	b ,g ,r = cv2.split(frame)
	image_data={'b':b, 'g':g, 'r':r}

	#....Fetching the trackbar values....
	min_blue_thr = cv2.getTrackbarPos(b_min_trackbar, title_window)
	min_green_thr = cv2.getTrackbarPos(g_min_trackbar, title_window)
	min_red_thr = cv2.getTrackbarPos(r_min_trackbar, title_window)
	max_blue_thr = cv2.getTrackbarPos(b_max_trackbar, title_window)
	max_green_thr = cv2.getTrackbarPos(g_max_trackbar, title_window)
	max_red_thr = cv2.getTrackbarPos(r_max_trackbar, title_window)

	#....Creating the mask....
	lower_bound = np.array([min_blue_thr, min_green_thr, min_red_thr], dtype=np.uint8)
	upper_bound = np.array([max_blue_thr, max_green_thr, max_red_thr], dtype=np.uint8)

	mask = cv2.inRange(frame, lower_bound, upper_bound)

	#....Showing the mask and the camera feedback....
	cv2.imshow('Thresholded Image', mask)
	cv2.imshow(title_window, frame)
	
	#.... Awaiting key to save or quit the program....
	k = cv2.waitKey(1)
	if k == ord('w'):
		#Writing the dictionary
		limits = {
            'limits': {
                'B': {'min': cv2.getTrackbarPos(b_min_trackbar, title_window),
                      'max': cv2.getTrackbarPos(b_max_trackbar, title_window)},
                'G': {'min': cv2.getTrackbarPos(g_min_trackbar, title_window),
                      'max': cv2.getTrackbarPos(g_max_trackbar, title_window)},
                'R': {'min': cv2.getTrackbarPos(r_min_trackbar, title_window),
                      'max': cv2.getTrackbarPos(r_max_trackbar, title_window)}}
            }
		#Saving the values in json type
		with open('limits.json', 'w') as file:
			json.dump(limits, file)

		print('Values Saved') #Feedback

	elif k == ord('q'):
		print('Quitting program') #Feedback
		break	#Quitting


vid.release()
cv2.destroyAllWindows()

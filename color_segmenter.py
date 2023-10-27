#!/usr/bin/env python3

import cv2
import numpy as np
from functools import partial

vid = cv2.VideoCapture(0)

alpha_slider_max = 255
title_window = 'frame'

def on_trackbar(val, channel, image_data):
	print(channel + ': ' + str(val))
	min_blue_thr = cv2.getTrackbarPos(b_min_trackbar, title_window)
	min_green_thr = cv2.getTrackbarPos(g_min_trackbar, title_window)
	min_red_thr = cv2.getTrackbarPos(r_min_trackbar, title_window)
	max_blue_thr = cv2.getTrackbarPos(b_max_trackbar, title_window)
	max_green_thr = cv2.getTrackbarPos(g_max_trackbar, title_window)
	max_red_thr = cv2.getTrackbarPos(r_max_trackbar, title_window)

	_,image_blue = cv2.threshold(image_data['b'], min_blue_thr, max_blue_thr, cv2.THRESH_BINARY)
	_,image_green = cv2.threshold(image_data['g'], min_green_thr, max_green_thr, cv2.THRESH_BINARY)
	_,image_red = cv2.threshold(image_data['r'], min_red_thr, max_red_thr, cv2.THRESH_BINARY)

	image_thresholded_2 = cv2.merge((image_blue,image_green,image_red))

ret, frame = vid.read()
cv2.imshow(title_window, frame)

b ,g ,r = cv2.split(frame)
image_data={'b':b, 'g':g, 'r':r}
r_min_trackbar = 'R Min'
r_max_trackbar = 'R Max'
g_min_trackbar = 'G Min'
g_max_trackbar = 'G Max'
b_min_trackbar = 'B Min'
b_max_trackbar = 'B Max'

cv2.createTrackbar(r_min_trackbar, title_window, 0, alpha_slider_max, partial(on_trackbar, channel='Rmin',image_data=image_data))
cv2.createTrackbar(r_max_trackbar, title_window, 255, alpha_slider_max, partial(on_trackbar, channel='Rmax',image_data=image_data))
cv2.createTrackbar(g_min_trackbar, title_window, 0, alpha_slider_max, partial(on_trackbar, channel='Gmin',image_data=image_data))
cv2.createTrackbar(g_max_trackbar, title_window, 255, alpha_slider_max, partial(on_trackbar, channel='Gmax',image_data=image_data))
cv2.createTrackbar(b_min_trackbar, title_window, 0, alpha_slider_max, partial(on_trackbar, channel='Bmin',image_data=image_data))
cv2.createTrackbar(b_max_trackbar, title_window, 255, alpha_slider_max, partial(on_trackbar, channel='Bmax',image_data=image_data))

while (True):
	ret, frame = vid.read()

	b ,g ,r = cv2.split(frame)
	image_data={'b':b, 'g':g, 'r':r}

	min_blue_thr = cv2.getTrackbarPos(b_min_trackbar, title_window)
	min_green_thr = cv2.getTrackbarPos(g_min_trackbar, title_window)
	min_red_thr = cv2.getTrackbarPos(r_min_trackbar, title_window)
	max_blue_thr = cv2.getTrackbarPos(b_max_trackbar, title_window)
	max_green_thr = cv2.getTrackbarPos(g_max_trackbar, title_window)
	max_red_thr = cv2.getTrackbarPos(r_max_trackbar, title_window)

	lower_bound = np.array([min_blue_thr, min_green_thr, min_red_thr], dtype=np.uint8)
	upper_bound = np.array([max_blue_thr, max_green_thr, max_red_thr], dtype=np.uint8)

	mask = cv2.inRange(frame, lower_bound, upper_bound)

	cv2.imshow('Window 2'+' Merge', mask)

	#(_, b) = cv2.threshold(frame[:, :, 0], 50, 180, cv2.THRESH_BINARY)
	#(_, g) = cv2.threshold(frame[:, :, 1], 50, 180, cv2.THRESH_BINARY)
	#(_, r) = cv2.threshold(frame[:, :, 2], 50, 180, cv2.THRESH_BINARY)
	#i = cv2.merge([b, g, r])
	#cv2.imshow(title_window, i)
	cv2.imshow(title_window, frame)
	k = cv2.waitKey(1)
	if k == ord('w'):
		pass
	elif k == ord('q'):
		break


vid.release()
cv2.destroyAllWindows()

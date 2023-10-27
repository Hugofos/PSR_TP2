import cv2

from functools import partial

vid = cv2.VideoCapture(0)

alpha_slider_max = 255
title_window = 'frame'
def on_trackbar(val, channel):
  print(channel + ': ' + str(val))
  r_value = val
	#alpha = val / alpha_slider_max
	#beta = ( 1.0 - alpha )
	#dst = cv2.addWeighted(src1, alpha, src2, beta, 0.0)
	#cv2.imshow(title_window, dst)

ret, frame = vid.read()
cv2.imshow(title_window, frame)

r_trackbar = 'R'
g_trackbar = 'G'
b_trackbar = 'B'

cv2.createTrackbar(r_trackbar, title_window, 0, alpha_slider_max, partial(on_trackbar, channel='R'))
cv2.createTrackbar(g_trackbar, title_window, 0, alpha_slider_max, partial(on_trackbar, channel='G'))
cv2.createTrackbar(b_trackbar, title_window, 0, alpha_slider_max, partial(on_trackbar, channel='B'))

while (True):
	ret, frame = vid.read()
	(_, b) = cv2.threshold(frame[:, :, 0], 50, 128, cv2.THRESH_BINARY)
	(_, g) = cv2.threshold(frame[:, :, 1], 50, 128, cv2.THRESH_BINARY)
	(_, r) = cv2.threshold(frame[:, :, 2], 50, 128, cv2.THRESH_BINARY)
	i = cv2.merge([b, g, r])
	cv2.imshow(title_window, i)
	k = cv2.waitKey(1)
	if k == ord('w'):
		pass
	elif k == ord('q'):
		break


vid.release()
cv2.destroyAllWindows()

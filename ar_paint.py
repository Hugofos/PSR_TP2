#!/usr/bin/env python3
import argparse
import copy
from functools import partial

import cv2
import numpy as np
from colorama import Fore, Style

def mouseCallback(event, x, y, flags, *userdata, drawing_data):
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing_data['pencil_down'] = True
        print(Fore.BLUE + 'pencil_down set to True' + Style.RESET_ALL)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing_data['pencil_down'] = False
        print(Fore.RED + 'pencil_down released' + Style.RESET_ALL)

    if drawing_data['pencil_down'] == True:
        cv2.line(drawing_data['img'], (drawing_data['previous_x'], drawing_data['previous_y']), (x, y), drawing_data['color'], drawing_data['thickness'])

    drawing_data['previous_x'] = x
    drawing_data['previous_y'] = y

def main():
    # -----------------------------------------------
    # Initialization
    # -----------------------------------------------
    parser = argparse.ArgumentParser()
    parser.add_argument('-if', '--image_filename', type=str, help='', required=False)

    args = vars(parser.parse_args())

    image_filename = args['image_filename']
    if image_filename == None:
        print('NADA')
    else:
        print(image_filename)

    image_rgb = np.ones((400, 600, 3), dtype=np.uint8) * 255
    default_img = copy.deepcopy(image_rgb)

    h, w, nc = image_rgb.shape

    drawing_data = {'img': image_rgb, 'pencil_down': False, 'previous_x': 0, 'previous_y': 0, 'color': (255, 255, 255), 'thickness': 1}

    cv2.namedWindow("image_rgb")
    cv2.setMouseCallback("image_rgb", partial(mouseCallback, drawing_data=drawing_data))

    # -----------------------------------------------
    # Execution
    # -----------------------------------------------

    # -----------------------------------------------
    # Visualization
    # -----------------------------------------------
    while True:
        cv2.imshow('image_rgb', drawing_data['img'])
        key = cv2.waitKey(50)

        if key == ord('q'):
            print('Quitting program')
            break

        elif key == ord('r'):
            print('Setting pencil to red color')
            drawing_data['color'] = (0, 0, 255)

        elif key == ord('g'):
            print('Setting pencil to green color')
            drawing_data['color'] = (0, 255, 0)

        elif key == ord('b'):
            print('Setting pencil to blue color')
            drawing_data['color'] = (255, 0, 0)

        elif key == ord('+'):
            if drawing_data['thickness'] < 10:
                drawing_data['thickness'] += 1
                print('Increased pencil thickness to: ' + str(drawing_data['thickness']))
            else:
                print('Maximum value is 10')

        elif key == ord('-'):
            if drawing_data['thickness'] > 1:
                drawing_data['thickness'] -= 1
                print('Decreased pencil thickness to: ' + str(drawing_data['thickness']))
            else:
                print('Minimum value is 1')

        elif key == ord('c'):
            print('Pressed C button')
            drawing_data['img'] = copy.deepcopy(default_img)

        elif key == ord('w'):
            print('Pressed W button')

    # -----------------------------------------------
    # Termination
    # -----------------------------------------------
    cv2.destroyWindow('image_rgb')

if __name__ == '__main__':
    main()

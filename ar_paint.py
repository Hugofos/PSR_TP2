#!/usr/bin/env python3
import argparse
import copy
from functools import partial
import json

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

def load_color_limits(json_file):
    with open(json_file, 'r') as file:
        limits = json.load(file)
    return limits

def main():
    # -----------------------------------------------
    # Initialization
    # -----------------------------------------------
    
    #....Programm arguments creation....
    parser = argparse.ArgumentParser(description='PSR AR Paint Aplication')
    parser.add_argument('-j', '--JSON', type=str, help='Full path to the JSON file', required=True)

    args = vars(parser.parse_args())

    #.... Setting the color limits....
    color_limits = load_color_limits(args['JSON'])

    #....Camera Initialization....
    vid = cv2.VideoCapture(0)
    ret, frame = vid.read()
    h, w, nc = frame.shape

    #....Canvas Creation....
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 255 #White board
    default_img = copy.deepcopy(canvas)

    #....Image data storing...
    drawing_data = {'img': canvas, 'pencil_down': False, 'previous_x': 0, 'previous_y': 0, 'color': (255, 255, 255), 'thickness': 1}

    cv2.namedWindow("canvas")
    cv2.setMouseCallback("canvas", partial(mouseCallback, drawing_data=drawing_data))

    # -----------------------------------------------
    # Execution
    # -----------------------------------------------

    # -----------------------------------------------
    # Visualization
    # -----------------------------------------------
    while True:
        ret, frame = vid.read()
        cv2.imshow('Camera feedback',frame)

        cv2.imshow('canvas', drawing_data['img'])
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

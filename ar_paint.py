#!/usr/bin/env python3
import argparse
import copy
from functools import partial
import json

import cv2
import numpy as np
import datetime
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
        color_limits=limits['limits']
    return color_limits

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
    print(color_limits)

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
        #....Camera capturing continuously....
        ret, frame = vid.read()
        cv2.imshow('Camera feedback',frame)

        #...Image processing....
        lower_bound = np.array([color_limits['B']['min'], color_limits['G']['min'], color_limits['R']['min']], dtype=np.uint8)
        upper_bound = np.array([color_limits['B']['max'], color_limits['G']['max'], color_limits['R']['max']], dtype=np.uint8)

        mask = cv2.inRange(frame, lower_bound, upper_bound)

        cv2.imshow('Mask Feedback', mask)

        #....Biggest area Selection....
        connectivity = 4  
        output = cv2.connectedComponentsWithStats(mask, connectivity, cv2.CV_32S)
        num_labels = output[0]  #Number of different group of pixels
        labels = output[1]      #Matrices with the different group of pixels
        stats = output[2]       #Saves some important stats (in this example, the important one its the area)
        centroids = output[3]   #Calculates the different centroids of the groups

        if num_labels > 1:
            largest_object_idx = 1 + stats[1:, cv2.CC_STAT_AREA].argmax()   #Stores the biggest area

            largest_object_mask = (labels == largest_object_idx).astype(np.uint8)*255
            contours, _ = cv2.findContours(largest_object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            largest_object_mask = cv2.cvtColor(largest_object_mask, cv2.COLOR_GRAY2BGR)

            cv2.imshow('Highlight Test', largest_object_mask)

            frame_with_highlight = cv2.addWeighted(frame, 1, largest_object_mask, 0.5, 0)
						
            if len(contours) > 0:
                largest_contour = max(contours, key = cv2.contourArea)
                M = cv2.moments(largest_contour)
                if M['m00'] != 0:
                    center_x = int(M['m10'] / M['m00'])
                    center_y = int(M['m01'] / M['m00'])
                    center = (center_x, center_y)

                    cv2.circle(frame_with_highlight, center, 5, (0, 0, 255), -1)
                    
                    cv2.line(drawing_data['img'], (drawing_data['previous_x'], drawing_data['previous_y']), center, drawing_data['color'], drawing_data['thickness'])
                    drawing_data['previous_x'] = center_x
                    drawing_data['previous_y'] = center_y
            
            cv2.imshow('Biggest Area Highlight', frame_with_highlight)
        else:
            cv2.imshow('Biggest Area Highlight', frame)
        
        #....Canvas updating....
        cv2.imshow('canvas', drawing_data['img'])
        
        #....Key awaiting....
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
            date = datetime.datetime.now().strftime('%a_%b_%d_%H:%M:%S_%Y')
            cv2.imwrite(f'./drawing_{date}.png', drawing_data['img'])

    # -----------------------------------------------
    # Termination
    # -----------------------------------------------
    cv2.destroyWindow('image_rgb')

if __name__ == '__main__':
    main()

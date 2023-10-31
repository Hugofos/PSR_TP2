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

def draw_circle(drawing_data):
    if drawing_data['drawing']:
        drawing_data['temp_img'] = drawing_data['img'].copy()
        if (drawing_data['start_pos'] == (0, 0)): return
        circle_radius = int(np.sqrt((drawing_data['start_pos'][0] - drawing_data['previous_x']) ** 2 + (drawing_data['start_pos'][1] - drawing_data['previous_y']) ** 2))
        cv2.circle(drawing_data['temp_img'], (drawing_data['start_pos'][0], drawing_data['start_pos'][1]), circle_radius, drawing_data['color'], drawing_data['thickness'])

def draw_square(drawing_data):
    if drawing_data['drawing']:
        drawing_data['temp_img'] = drawing_data['img'].copy()
        if (drawing_data['start_pos'] == (0, 0)): return
        cv2.rectangle(drawing_data['temp_img'], (drawing_data['start_pos'][0], drawing_data['start_pos'][1]), (drawing_data['previous_x'], drawing_data['previous_y']), drawing_data['color'], drawing_data['thickness'])

def draw_ellipse(drawing_data):
    if drawing_data['drawing']:
        drawing_data['temp_img'] = drawing_data['img'].copy()
        if (drawing_data['start_pos'] == (0, 0)): return
        ellipse_axis = (int(np.sqrt((drawing_data['start_pos'][0] - drawing_data['previous_x']) ** 2 + (drawing_data['start_pos'][1] - drawing_data['previous_y']) ** 2)), 50)
        cv2.ellipse(drawing_data['temp_img'], (drawing_data['start_pos'][0], drawing_data['start_pos'][1]), ellipse_axis, 0, 0, 360, drawing_data['color'], drawing_data['thickness'])

def main():
    # -----------------------------------------------
    # Initialization
    # -----------------------------------------------
    
    #....Programm arguments creation....
    parser = argparse.ArgumentParser(description='PSR AR Paint Aplication')
    parser.add_argument('-j', '--JSON', type=str, help='Full path to the JSON file', required=True)
    parser.add_argument('-usp', '--use_shake_prevention', type=int, help='Set the value for the shakedown - recomended: 50', required=False)
    parser.add_argument('-ucs','--use_camera_stream', action='store_true',help='Use the camera stream as a canvas instead of a white board')

    args = vars(parser.parse_args())

    #.... Setting the color limits and drawing mode....
    color_limits = load_color_limits(args['JSON'])
    drawing_mode = 'Line'

    #....Camera Initialization....
    vid = cv2.VideoCapture(0)
    ret, frame = vid.read()
    h, w, nc = frame.shape

    #....Canvas Creation....
    if args['use_camera_stream']:
        canvas = np.ones((h, w, 3), dtype=np.uint8) #"Transparent" board
    else: 
        canvas = np.ones((h, w, 3), dtype=np.uint8) * 255 #White board
    default_img = copy.deepcopy(canvas)

    #....Image data storing...
    drawing_data = {'img': canvas, 'pencil_down': False, 'previous_x': 0, 'previous_y': 0, 'color': (255, 255, 255), 'thickness': 5, 'drawing': False, 'start_pos': (0, 0), 'temp_img': canvas.copy()}

    cv2.namedWindow("canvas")

    #....Shakedown initialization....
    prev_center = None
    if args['use_shake_prevention'] == None:
        use_shake  = False
    else:
        use_shake = True
        shake_threshold = args['use_shake_prevention']   

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
            largest_object_mask = cv2.cvtColor(largest_object_mask, cv2.COLOR_GRAY2BGR)

            frame_with_highlight = cv2.addWeighted(frame, 1, largest_object_mask, 0.5, 0)
						
            if len(centroids) > 0:
                current_center = centroids[largest_object_idx]
                center_x = int(current_center[0])
                center_y = int(current_center[1])
                cv2.line(frame_with_highlight, (center_x-5,center_y-5), (center_x+5,center_y+5), (0, 0, 255), 2)
                cv2.line(frame_with_highlight, (center_x+5,center_y-5), (center_x-5,center_y+5), (0, 0, 255), 2)
                if use_shake == False:
                    if drawing_mode == 'Line':
                        cv2.line(drawing_data['img'], (drawing_data['previous_x'], drawing_data['previous_y']), (center_x, center_y), drawing_data['color'], drawing_data['thickness'])

                    if drawing_mode == 'Circle':
                        if drawing_data['drawing'] == False:
                            drawing_data['start_pos'] = (center_x, center_y)
                        draw_circle(drawing_data)
                        
                    if drawing_mode == 'Square':
                        if drawing_data['drawing'] == False:
                            drawing_data['start_pos'] = (center_x, center_y)
                        draw_square(drawing_data)
                        
                    if drawing_mode == 'Ellipse':
                        if drawing_data['drawing'] == False:
                            drawing_data['start_pos'] = (center_x, center_y)
                        draw_ellipse(drawing_data)
                else:
                    current_center = None
                
                if use_shake:
                    if prev_center is not None and current_center is not None:
                        dx, dy = abs(current_center[0] - prev_center[0]), abs(current_center[1] - prev_center[1])
                        max_difference = max(np.abs(dx), np.abs(dy))
                        if max_difference <= shake_threshold:
                            if drawing_mode == 'Line':
                                cv2.line(drawing_data['img'], prev_center, current_center, drawing_data['color'], drawing_data['thickness'])
                        else:
                            cv2.circle(drawing_data['img'], current_center, 2, drawing_data['color'], -1)
                    
                    prev_center = current_center
            
                drawing_data['previous_x'] = center_x
                drawing_data['previous_y'] = center_y
            cv2.imshow('Biggest Area Highlight', frame_with_highlight)
        else:
            cv2.imshow('Biggest Area Highlight', frame)
        
        
        #....Canvas updating....
        if args['use_camera_stream']:
            camera_and_canvas = cv2.addWeighted(frame, 1, drawing_data['img'], 1, 0)
            cv2.imshow('canvas', camera_and_canvas)
        else:
            if drawing_data['drawing']:
                cv2.imshow('canvas', drawing_data['temp_img'])
            else:
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
        
        elif key == ord('s'):
            print('Changed mode to square')
            drawing_mode = 'Square'
            drawing_data['drawing'] = True

        elif key == ord('e'):
            print('Changed to ellipse mode')
            drawing_mode = 'Ellipse'
            drawing_data['drawing'] = True

        elif key == ord('o'):
            print('Changed to circle mode')
            drawing_mode = 'Circle'
            drawing_data['drawing'] = True

        elif key == ord('l'):
            print('Changed to line mode')
            drawing_mode = 'Line'

        elif key == ord('c'):
            print('Pressed C button')
            drawing_data['img'] = copy.deepcopy(default_img)

        elif key == ord('w'):
            print('Pressed W button')
            date = datetime.datetime.now().strftime('%a_%b_%d_%H:%M:%S_%Y')
            cv2.imwrite(f'./drawing_{date}.png', drawing_data['img'])
        
        else:
            if drawing_data['drawing']:
                drawing_data['img'] = drawing_data['temp_img'].copy()
            drawing_data['drawing'] = False
            drawing_data['start_pos'] = (0, 0)

    # -----------------------------------------------
    # Termination
    # -----------------------------------------------
    cv2.destroyWindow('image_rgb')

if __name__ == '__main__':
    main()

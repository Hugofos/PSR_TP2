#!/usr/bin/env python3
import argparse

import cv2
import numpy as np

from functions import *

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

    #....Camera Initialization....
    vid = cv2.VideoCapture(0)
    ret, frame = vid.read()
    h, w, nc = frame.shape

    #....Canvas Creation....
    if args['use_camera_stream']:
        canvas = np.ones((h, w, 3), dtype=np.uint8) #"Transparent" board
    else: 
        canvas = np.ones((h, w, 3), dtype=np.uint8) * 255 #White board
    default_img = canvas.copy()

    #....Image data storing...
    drawing_data = {'img': canvas, 'pencil_down': False, 'previous_x': 0, 'previous_y': 0, 'color': (255, 255, 255), 'thickness': 5, 'drawing': False, 'drawing_mode': 'Line', 'start_pos': (0, 0), 'temp_img': canvas.copy()}

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
                    if drawing_data['drawing_mode'] == 'Line':
                        cv2.line(drawing_data['img'], (drawing_data['previous_x'], drawing_data['previous_y']), (center_x, center_y), drawing_data['color'], drawing_data['thickness'])

                    if drawing_data['drawing'] == False:
                        drawing_data['start_pos'] = (center_x, center_y)
                    
                    draw_shape(drawing_data)
                else:
                    current_center = None
                
                if use_shake:
                    if prev_center is not None and current_center is not None:
                        dx, dy = abs(current_center[0] - prev_center[0]), abs(current_center[1] - prev_center[1])
                        max_difference = max(np.abs(dx), np.abs(dy))
                        if max_difference <= shake_threshold:
                            if drawing_data['drawing_mode'] == 'Line':
                                cv2.line(drawing_data['img'], prev_center, current_center, drawing_data['color'], drawing_data['thickness'])
                        else:
                            if drawing_data['drawing'] == False:
                                drawing_data['start_pos'] = (center_x, center_y)
                            
                            draw_shape(drawing_data)
                    
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

        # Changes program behavier according to key pressed
        if key == ord('q'):
            print('Quitting program')
            break
        else: pressed_key(key, drawing_data, default_img)

    # -----------------------------------------------
    # Termination
    # -----------------------------------------------
    cv2.destroyWindow('image_rgb')

if __name__ == '__main__':
    main()

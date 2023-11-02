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
    parser.add_argument('-ucs','--use_camera_stream', action='store_true', help='Use the camera stream as a canvas instead of a white board')
    parser.add_argument('-pbn','--paint_by_number', action='store_true', help='Use to paint in paint-by-number mode. Use_camara_stream overrides this argument\nWhen finished, press A to evaluate')

    args = vars(parser.parse_args())

    #.... Setting the color limits....
    color_limits = load_color_limits(args['JSON'])

    #....Camera Initialization....
    vid = cv2.VideoCapture(0)
    ret, frame = vid.read()
    h, w, nc = frame.shape

    #....Canvas Creation....
    areas = None

    if args['use_camera_stream']:
        canvas = np.ones((h, w, 3), dtype=np.uint8) #"Transparent" board
    else: 
        canvas = np.ones((h, w, 3), dtype=np.uint8) * 255 #White board
    default_img = canvas.copy()

    #....Image data storing...
    drawing_data = {'img': canvas, 'pencil_down': False, 'previous_x': 0, 'previous_y': 0, 'color': (255, 255, 255), 'thickness': 5, 'drawing': False, 'drawing_mode': None, 'start_pos': (0, 0), 'temp_img': canvas.copy(),'score_board':None}

    if not args['use_camera_stream'] and args['paint_by_number']:
        areas = segment_image(drawing_data,h, w)
        drawing_data['score_board'] =  np.ones((100, 300, 3), dtype=np.uint8)
        cv2.imshow('Score', drawing_data['score_board'])

    cv2.namedWindow("canvas")
    cv2.moveWindow("canvas", 40,30)

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
            largest_object_idx = 1 + stats[1:, cv2.CC_STAT_AREA].argmax()   #Stores the index of the biggest area

            largest_object_mask = (labels == largest_object_idx).astype(np.uint8)*255   #Creates a mask
            largest_object_mask = cv2.cvtColor(largest_object_mask, cv2.COLOR_GRAY2BGR) #Convert to color to merge

            frame_with_highlight = cv2.addWeighted(frame, 1, largest_object_mask, 0.5, 0)   #Merging the camera image with the mask
			
            #....Centroid calcultion and drawing....
            if len(centroids) > 0:
                current_center = centroids[largest_object_idx] #Saves the centroid coordinates
                center_x = int(current_center[0])
                center_y = int(current_center[1])
                current_center = (center_x, center_y) #this is needed because centroids came in float type
                cv2.line(frame_with_highlight, (center_x-5,center_y-5), (center_x+5,center_y+5), (0, 0, 255), 2) #Draws a cross in the centroid position
                cv2.line(frame_with_highlight, (center_x+5,center_y-5), (center_x-5,center_y+5), (0, 0, 255), 2)
                
                if use_shake == False:
                    #Line Drawing
                    if drawing_data['drawing_mode'] == 'Line':
                        cv2.line(drawing_data['img'], (drawing_data['previous_x'], drawing_data['previous_y']), (center_x, center_y), drawing_data['color'], drawing_data['thickness'])
                    #Keeps changing the starting postition until the figure drawing starts
                    if drawing_data['drawing'] == False:
                        drawing_data['start_pos'] = (center_x, center_y)
                    #If the drawing mode has changed, it will draw the respective figure
                    draw_shape(drawing_data)
                #Updates the position
                drawing_data['previous_x'] = center_x
                drawing_data['previous_y'] = center_y

            else:
                current_center = None #Just in case it doesn't find any centroid
                
            if use_shake:
                if prev_center is not None and current_center is not None: #To calculate a diference is needed to have two different positions
                    dx, dy = abs(current_center[0] - prev_center[0]), abs(current_center[1] - prev_center[1])   #Difference calculation
                    max_difference = max(np.abs(dx), np.abs(dy))
                    
                    #Only draws if there hasn't been a jump
                    if max_difference <= shake_threshold:
                        if drawing_data['drawing_mode'] == 'Line':
                            cv2.line(drawing_data['img'], prev_center, current_center, drawing_data['color'], drawing_data['thickness'])
                        if drawing_data['drawing'] == False:
                            drawing_data['start_pos'] = (center_x, center_y)
                
                        draw_shape(drawing_data)
                
                prev_center = current_center #updates the postion
            
            #....Showing the highlight and centroid result....
            cv2.imshow('Biggest Area Highlight', frame_with_highlight)
        else:
            cv2.imshow('Biggest Area Highlight', frame)
        
        
        #....Canvas updating....
        if args['use_camera_stream']:
            #We need to merge the transparent board with the camera image
            if drawing_data['drawing']:
                #The temp image represents the drawing of a shape that is not yet finished
                camera_and_canvas = cv2.addWeighted(frame, 1, drawing_data['temp_img'], 1, 0)
                cv2.imshow('canvas', camera_and_canvas)
            else:
                #Here the image update its final
                camera_and_canvas = cv2.addWeighted(frame, 1, drawing_data['img'], 1, 0)
                cv2.imshow('canvas', camera_and_canvas)
        else:
            if drawing_data['drawing']:
                cv2.imshow('canvas', drawing_data['temp_img'])
            else:
                cv2.imshow('canvas', drawing_data['img'])
        
        #....Periodically updates score....
        calculate_score(drawing_data, default_img, areas)
        if not args['use_camera_stream'] and args['paint_by_number']:
            cv2.imshow('Score', drawing_data['score_board'])

        #....Key awaiting....
        key = cv2.waitKey(50)

        # Changes program behavior according to key pressed
        if key == ord('q'):
            print('Quitting program')
            break
        else: pressed_key(key, drawing_data, default_img, areas)

    # -----------------------------------------------
    # Termination
    # -----------------------------------------------
    cv2.destroyWindow('image_rgb')

if __name__ == '__main__':
    main()

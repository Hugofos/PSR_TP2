import json
import cv2
import numpy as np
import datetime
import random

# Mouse callback function to draw
def mouseCallback(event, x, y, flags, *userdata, drawing_data):
    if drawing_data['drawing_mode'] == 'Line':
        cv2.line(drawing_data['img'], (drawing_data['previous_x'], drawing_data['previous_y']), (x, y), drawing_data['color'], drawing_data['thickness'])
    
    #Keeps changing the starting postition until the figure drawing starts
    if drawing_data['drawing'] == False:
        drawing_data['start_pos'] = (x, y)
    
    #If the drawing mode has changed, it will draw the respective figure
    draw_shape(drawing_data)
    
    #Updates the position
    drawing_data['previous_x'] = x
    drawing_data['previous_y'] = y 


# Load values from file
def load_color_limits(json_file):
    with open(json_file, 'r') as file:
        limits = json.load(file)
        color_limits=limits['limits']
    return color_limits

# Draws the shape selected by the user
def draw_shape(drawing_data):
    if drawing_data['drawing']:
        drawing_data['temp_img'] = drawing_data['img'].copy() #creates temp image
        if (drawing_data['start_pos'] == (0, 0)): return

        if drawing_data['drawing_mode'] == 'Circle':
            #Calculates the radius and draws a circle
            circle_radius = int(np.sqrt((drawing_data['start_pos'][0] - drawing_data['previous_x']) ** 2 + (drawing_data['start_pos'][1] - drawing_data['previous_y']) ** 2))
            cv2.circle(drawing_data['temp_img'], (drawing_data['start_pos'][0], drawing_data['start_pos'][1]), circle_radius, drawing_data['color'], drawing_data['thickness'])
        
        elif drawing_data['drawing_mode'] == 'Square':
            #Draws a rectangle
            cv2.rectangle(drawing_data['temp_img'], (drawing_data['start_pos'][0], drawing_data['start_pos'][1]), (drawing_data['previous_x'], drawing_data['previous_y']), drawing_data['color'], drawing_data['thickness'])

        elif drawing_data['drawing_mode'] == 'Ellipse':
            #Draws an elipse
            ellipse_axis = (int(abs(drawing_data['previous_x']-drawing_data['start_pos'][0])),int(abs(drawing_data['previous_y']-drawing_data['start_pos'][1])))
            cv2.ellipse(drawing_data['temp_img'], (drawing_data['start_pos'][0], drawing_data['start_pos'][1]), ellipse_axis, 0, 0, 360, drawing_data['color'], drawing_data['thickness'])

# Changes program behavier according to key pressed
def pressed_key(key, drawing_data, default_img, areas):
    if key == ord('r'):
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
        drawing_data['drawing_mode'] = 'Square'
        drawing_data['drawing'] = True

    elif key == ord('e'):
        drawing_data['drawing_mode'] = 'Ellipse'
        drawing_data['drawing'] = True

    elif key == ord('o'):
        drawing_data['drawing_mode'] = 'Circle'
        drawing_data['drawing'] = True

    elif key == ord('l'):
        print('Changed to line mode')
        drawing_data['drawing_mode'] = 'Line'

    elif key == ord('c'):
        print('Cleared Image')
        drawing_data['img'] = default_img.copy()

    elif key == ord('w'):
        print('Saved Image')
        date = datetime.datetime.now().strftime('%a_%b_%d_%H:%M:%S_%Y')
        cv2.imwrite(f'./drawing_{date}.png', drawing_data['img'])

    else: #Used to know when a pressed key was released
        if drawing_data['drawing']:
            drawing_data['img'] = drawing_data['temp_img'].copy()
        drawing_data['drawing'] = False
        drawing_data['start_pos'] = (0, 0)


def segment_image(drawing_data, h, w):
    # Create a blank white canvas   
    num_lines = 3
    img = np.ones((h, w, 3), np.uint8) * 255

    # Draw 3 vertical polylines
    for i in range(num_lines):
        points = []

        # First point: y = 0
        x1 = (i + 1) * (w // (num_lines + 1))
        y = 0
        points.append((x1, y))

        # Second point: limited by 10 pixels on x, y at the bottom
        x2 = x1 + random.randint(-50, 50)
        y = h / 2
        points.append((x2, y))

        # Third point: limited by 10 pixels on x, y at the bottom
        x = x2 + random.randint(-50, 50)
        y = h
        points.append((x, y))

        points = np.array(points, np.int32)
        points = points.reshape((-1, 1, 2))

        color = (0, 0, 0)

        cv2.polylines(img, [points], isClosed=False, color=color, thickness=2)

    # Draw 3 horizontal polylines
    for j in range(num_lines):
        points = []

        # First point: x = 0
        x = 0
        y1 = (j + 1) * (h // (num_lines + 1))
        points.append((x, y1))

        # Second point: limited by 10 pixels on y, x at the right end
        x = w / 2
        y2 = y1 + random.randint(-50, 50)
        points.append((x, y2))

        # Third point: limited by 10 pixels on y, x at the right end
        x = w
        y = y2 + random.randint(-50, 50)
        points.append((x, y))

        points = np.array(points, np.int32)
        points = points.reshape((-1, 1, 2))

        color = (0, 0, 0)

        cv2.polylines(img, [points], isClosed=False, color=color, thickness=2)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to separate regions
    ret, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Find contours of connected components
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    areas=[]
    # Assign random numbers to sections and label them at the center
    for i, contour in enumerate(contours):
        section_number = random.randint(1, 3)
        if section_number == 1:
            col=(0,0,255)
        elif section_number == 2:
            col=(0,255,0)
        else: 
            col=(255,0,0)
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(img, (cX,cY), 15, col, -1)
            cv2.putText(img, str(section_number), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        areas.append((contour,section_number))

    # Draw contours on the image for visualization
    cv2.drawContours(img, contours, -1, (0, 0, 0), 2)

    # Display the image
    drawing_data['img'] = img.copy()
    return areas

def calculate_score(drawing_data, dificulty, areas):
    color_map = {
    1: (0, 0, 255),  
    2: (0, 255, 0), 
    3: (255, 0, 0)
}

    # Initialize user's score
    user_score = 0

    # Iterate through the contours you have
    for contour, area_number in areas:
        # Calculate the average color within the contour
        x, y, w, h = cv2.boundingRect(contour)
        roi = drawing_data['img'][y:y+h, x:x+w]
        average_color = np.mean(roi, axis=(0, 1))

        # Get the expected color from the color map
        expected_color = color_map.get(area_number, (0, 0, 0))

        # Define a color similarity threshold
        color_similarity_threshold = int(200/dificulty)  # Tweak as needed

        # Compare the color of the area with the expected color
        color_diff = np.linalg.norm(average_color - expected_color)
        if color_diff < color_similarity_threshold:
            user_score += 1  # Increment the score for a correct color

    # Display the user's score on the AR interface
    drawing_data['score_board'] = np.ones((100, 300, 3), dtype=np.uint8) #clear the text
    cv2.putText(drawing_data['score_board'], f"Score: {user_score} / 12", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

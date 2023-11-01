import json
import cv2
import numpy as np
import datetime
import random

# Load values from file
def load_color_limits(json_file):
    with open(json_file, 'r') as file:
        limits = json.load(file)
        color_limits=limits['limits']
    return color_limits

# Draws the shape selected by the user
def draw_shape(drawing_data):
    if drawing_data['drawing']:
        drawing_data['temp_img'] = drawing_data['img'].copy()
        if (drawing_data['start_pos'] == (0, 0)): return

        if drawing_data['drawing_mode'] == 'Circle':
            circle_radius = int(np.sqrt((drawing_data['start_pos'][0] - drawing_data['previous_x']) ** 2 + (drawing_data['start_pos'][1] - drawing_data['previous_y']) ** 2))
            cv2.circle(drawing_data['temp_img'], (drawing_data['start_pos'][0], drawing_data['start_pos'][1]), circle_radius, drawing_data['color'], drawing_data['thickness'])

        elif drawing_data['drawing_mode'] == 'Square':
            cv2.rectangle(drawing_data['temp_img'], (drawing_data['start_pos'][0], drawing_data['start_pos'][1]), (drawing_data['previous_x'], drawing_data['previous_y']), drawing_data['color'], drawing_data['thickness'])

        elif drawing_data['drawing_mode'] == 'Ellipse':
            ellipse_axis = (int(np.sqrt((drawing_data['start_pos'][0] - drawing_data['previous_x']) ** 2 + (drawing_data['start_pos'][1] - drawing_data['previous_y']) ** 2)), 50)
            cv2.ellipse(drawing_data['temp_img'], (drawing_data['start_pos'][0], drawing_data['start_pos'][1]), ellipse_axis, 0, 0, 360, drawing_data['color'], drawing_data['thickness'])

# Changes program behavier according to key pressed
def pressed_key(key, drawing_data, default_img):
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
        drawing_data['img'] = default_img.copy()

    elif key == ord('w'):
        print('Pressed W button')
        date = datetime.datetime.now().strftime('%a_%b_%d_%H:%M:%S_%Y')
        cv2.imwrite(f'./drawing_{date}.png', drawing_data['img'])

    elif key == ord('m'):
        numbered_painting()
    
    else:
        if drawing_data['drawing']:
            drawing_data['img'] = drawing_data['temp_img'].copy()
        drawing_data['drawing'] = False
        drawing_data['start_pos'] = (0, 0)

def numbered_painting():
    num_sections = 8
    width = 512
    height = 512

    img = np.zeros((height, width, 3), np.uint8)

    # Define the center of the image
    center_x, center_y = width // 2, height // 2

    # List to store the vertices of each section
    section_vertices = []

    for _ in range(num_sections):
        num_vertices = random.randint(3, 8) # Randomly select the number of vertices for each section
        section = []
        for _ in range(num_vertices):
            x = random.randint(0, width)
            y = random.randint(0, height)
            section.append((x, y))
        section_vertices.append(section)

    # Draw sections and labels
    for i, vertices in enumerate(section_vertices):
        vertices = np.array(vertices)
        cv2.fillPoly(img, [vertices], (255, 255, 255))
        for j in range(vertices.shape[0]):
            cv2.line(img, tuple(vertices[j]), tuple(vertices[(j + 1) % vertices.shape[0]]), (0, 0, 0), 2) # Draw black lines
        label_x, label_y = np.mean(vertices, axis = 0).astype(int)
        cv2.putText(img, str(i), (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    cv2.imshow('Random shapes', img)
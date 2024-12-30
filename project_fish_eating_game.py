from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
from OpenGL.GLUT import GLUT_BITMAP_TIMES_ROMAN_24
GLUT_BITMAP_HELVETICA_18 = ctypes.c_void_p(5) 
import math

# Window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

BUTTON_WIDTH = 50
BUTTON_HEIGHT = 30

# Button positions
BUTTON_LEFT = (50, WINDOW_HEIGHT - 50)
BUTTON_PAUSE = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)
BUTTON_EXIT = (WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50)

# Fish and point properties
fish1 = {'x': 200, 'y': 300, 'size': 24, 'direction': (1, 0), 'speed': 2.0, 'score': 5}
fish2 = {'x': 600, 'y': 300, 'size': 24, 'direction': (-1, 0), 'speed': 2.0, 'score': 5}
points = []
bubbles = [{'x': random.randint(10, WINDOW_WIDTH - 10), 'y': random.randint(10, WINDOW_HEIGHT - 10), 'radius': random.randint(10, 20)} for _ in range(20)]
level = 1
max_size = 39

time_counter = 0
expanding_radius = 10
expanding_shrink_rate = 0.2
expanding_direction = 1

# Game states
game_over = False
winner = None
show_end_message = False
paused = False

def reset_game():
    global fish1, fish2, points, game_over, paused, winner, show_end_message
    fish1 = {'x': 200, 'y': 300, 'size': 24, 'direction': (1, 0), 'speed': 2.0, 'score': 5}
    fish2 = {'x': 600, 'y': 300, 'size': 24, 'direction': (-1, 0), 'speed': 2.0, 'score': 5}
    points = []
    game_over = False
    paused = False
    winner = None
    show_end_message = False
    print("Starting Over")

def exit_game():
    print(f"Goodbye. Final Scores: Player 1: {fish1['score']}, Player 2: {fish2['score']}")
    glutLeaveMainLoop()

def draw_buttons():
    global BUTTON_LEFT, BUTTON_PAUSE, BUTTON_EXIT

    BUTTON_LEFT = (WINDOW_WIDTH // 2 - 120, WINDOW_HEIGHT - 50)
    BUTTON_PAUSE = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)
    BUTTON_EXIT = (WINDOW_WIDTH // 2 + 120, WINDOW_HEIGHT - 50)

    # Restart button
    glColor3f(0.0, 0.5, 1.0)  # Cyan color
    glBegin(GL_POINTS)
    for x in range(BUTTON_LEFT[0] - BUTTON_WIDTH // 2, BUTTON_LEFT[0] + BUTTON_WIDTH // 2 + 1):
        for y in range(BUTTON_LEFT[1] - BUTTON_HEIGHT // 2, BUTTON_LEFT[1] + BUTTON_HEIGHT // 2 + 1):
            glVertex2f(x, y)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(BUTTON_LEFT[0] - 10, BUTTON_LEFT[1] - 5)
    for c in "<-":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Pause button
    glColor3f(0.9, 1.0, 0.0)  # Yellow color
    glBegin(GL_POINTS)
    for x in range(BUTTON_PAUSE[0] - BUTTON_WIDTH // 2, BUTTON_PAUSE[0] + BUTTON_WIDTH // 2 + 1):
        for y in range(BUTTON_PAUSE[1] - BUTTON_HEIGHT // 2, BUTTON_PAUSE[1] + BUTTON_HEIGHT // 2 + 1):
            glVertex2f(x, y)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(BUTTON_PAUSE[0] - 10, BUTTON_PAUSE[1] - 5)
    icon = "||" if not paused else "|>"
    for c in icon:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

    # Exit button
    glColor3f(1.0, 0.0, 0.0)  # Red color
    glBegin(GL_POINTS)
    for x in range(BUTTON_EXIT[0] - BUTTON_WIDTH // 2, BUTTON_EXIT[0] + BUTTON_WIDTH // 2 + 1):
        for y in range(BUTTON_EXIT[1] - BUTTON_HEIGHT // 2, BUTTON_EXIT[1] + BUTTON_HEIGHT // 2 + 1):
            glVertex2f(x, y)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(BUTTON_EXIT[0] - 5, BUTTON_EXIT[1] - 5)
    for c in "X":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))


def is_inside_button(x, y, button_pos, size=20):
    return (button_pos[0] - size <= x <= button_pos[0] + size and
            button_pos[1] - size <= y <= button_pos[1] + size)

# Midpoint circle algorithm
def midpoint_circle(xc, yc, radius, color):
    x = 0
    y = radius
    d = 1 - radius

    glColor3f(*color)
    glBegin(GL_POINTS)

    def plot_circle_points(xc, yc, x, y):
        glVertex2f(xc + x, yc + y)
        glVertex2f(xc - x, yc + y)
        glVertex2f(xc + x, yc - y)
        glVertex2f(xc - x, yc - y)
        glVertex2f(xc + y, yc + x)
        glVertex2f(xc - y, yc + x)
        glVertex2f(xc + y, yc - x)
        glVertex2f(xc - y, yc - x)

    plot_circle_points(xc, yc, x, y)

    while x < y:
        x += 1
        if d < 0:
            d += 2 * x + 1
        else:
            y -= 1
            d += 2 * (x - y) + 1
        plot_circle_points(xc, yc, x, y)

    glEnd()

def midpoint_line(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    err = dx - dy

    glBegin(GL_POINTS)
    while True:
        glVertex2f(x1, y1)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    glEnd()


# Draw green triangles at the bottom to simulate an aquarium floor
 # For sine wave patterns

def draw_aquarium_floor():
    glColor3f(0.3, 0.6, 0.3)  # Darker green color for leaves
    leaf_width = 10  # Maximum width of each leaf
    leaf_height = 20  # Height of each leaf (shorter length)
    stem_height = 100  # Height of the plant's stem (shortened)

    for x in range(50, WINDOW_WIDTH, 100):  # Spacing between plants
        base_y = 0  # Start from the bottom of the screen

        # Draw the stem using midpoint_line
        midpoint_line(x, base_y, x, base_y + stem_height)

        # Add leaves to the stem
        for i in range(20, stem_height, 40):  # Vertical spacing between leaves
            # Left leaf (curve using midpoint_circle and line)
            for j in range(leaf_height):
                offset = int(math.sin(j * math.pi / leaf_height) * leaf_width)
                midpoint_line(x, base_y + i + j, x - offset, base_y + i + j)

            # Right leaf (curve using midpoint_circle and line)
            for j in range(leaf_height):
                offset = int(math.sin(j * math.pi / leaf_height) * leaf_width)
                midpoint_line(x, base_y + i + j, x + offset, base_y + i + j)

        # Add leaf tips using midpoint_circle for rounded edges
        for i in range(20, stem_height, 40):  # Vertical spacing between leaves
            midpoint_circle(x - leaf_width, base_y + i + leaf_height, leaf_width // 2, (0.3, 0.6, 0.3))
            midpoint_circle(x + leaf_width, base_y + i + leaf_height, leaf_width // 2, (0.3, 0.6, 0.3))

    # Add additional smaller leaves near the bottom
    for x in range(30, WINDOW_WIDTH, 50):  # Denser spacing at the bottom
        base_y = 0

        # Draw shorter stems with leaves
        for i in range(10, 50, 20):  # Shorter vertical spacing
            # Left leaf
            for j in range(leaf_height // 2):
                offset = int(math.sin(j * math.pi / (leaf_height // 2)) * (leaf_width // 2))
                midpoint_line(x, base_y + i + j, x - offset, base_y + i + j)

            # Right leaf
            for j in range(leaf_height // 2):
                offset = int(math.sin(j * math.pi / (leaf_height // 2)) * (leaf_width // 2))
                midpoint_line(x, base_y + i + j, x + offset, base_y + i + j)

            # Leaf tips
            midpoint_circle(x - (leaf_width // 2), base_y + i + (leaf_height // 2), leaf_width // 4, (0.3, 0.6, 0.3))
            midpoint_circle(x + (leaf_width // 2), base_y + i + (leaf_height // 2), leaf_width // 4, (0.3, 0.6, 0.3))

def draw_random_wavy_points():
    glColor3f(0.0, 0.9, 1)  # Light blue color for the points
    line_count = 5  # Number of wavy lines

    for _ in range(line_count):
        # Predefined starting position and wave properties for consistency
        start_x = random.randint(0, WINDOW_WIDTH - 170)
        start_y = random.randint(0, WINDOW_HEIGHT - 25)
        wave_length = random.randint(300, 300)  # Increased wavelength for slower waves
        amplitude = random.randint(10, 15)     # Amplitude of the wave
        frequency = random.uniform(0.001, 0.01)  # Lower frequency for slower movement

        # Draw wave-shaped line using midpoint_line
        previous_x, previous_y = start_x, start_y
        for i in range(0, wave_length):
            x = start_x + i
            y = start_y + int(amplitude * math.sin(2 * math.pi * frequency * i))
            midpoint_line(previous_x, previous_y, x, y)
            previous_x, previous_y = x, y
def draw_bubbles():
    for bubble in bubbles:
        midpoint_circle(bubble['x'], bubble['y'], bubble['radius'], (1, 1, 1))  # White bubbles
def draw_fish(fish, body_color, tail_color, fin_color):
    """
    Draw a fish with body, tail, fins, and an eye.
    Args:
        fish (dict): A dictionary containing fish attributes (x, y, size, direction).
        body_color (tuple): RGB color for the body.
        tail_color (tuple): RGB color for the tail.
        fin_color (tuple): RGB color for the fins.
    """
    # Adjust the body and tail positions based on direction
    body_offset_x = fish['direction'][0] * fish['size'] // 2
    body_offset_y = fish['direction'][1] * fish['size'] // 2

    # Draw the body of the fish (main circle)
    midpoint_circle(fish['x'] + body_offset_x, fish['y'] + body_offset_y, fish['size'], body_color)

    # Draw the tail of the fish
    tail_offset_x = -fish['direction'][0] * fish['size'] // 2
    tail_offset_y = -fish['direction'][1] * fish['size'] // 2
    midpoint_circle(fish['x'] + tail_offset_x, fish['y'] + tail_offset_y, fish['size'] // 2, tail_color)

    # Calculate fin positions relative to direction
    fin_base_x = fish['x'] + body_offset_x
    fin_base_y = fish['y'] + body_offset_y

    # Adjust fin directions based on fish movement
    if fish['direction'][0] != 0:  # Moving left or right
        fin_upper_tip_x = fin_base_x - fish['direction'][0] * fish['size']
        fin_upper_tip_y = fin_base_y + fish['size']
        fin_lower_tip_x = fin_base_x - fish['direction'][0] * fish['size']
        fin_lower_tip_y = fin_base_y - fish['size']
    else:  # Moving up or down
        fin_upper_tip_x = fin_base_x
        fin_upper_tip_y = fin_base_y + fish['size']
        fin_lower_tip_x = fin_base_x
        fin_lower_tip_y = fin_base_y - fish['size']

    # Draw the upper fin
    midpoint_line(
        fin_base_x, fin_base_y + fish['size'] // 2,
        fin_upper_tip_x, fin_upper_tip_y
    )

    # Draw the lower fin
    midpoint_line(
        fin_base_x, fin_base_y - fish['size'] // 2,
        fin_lower_tip_x, fin_lower_tip_y
    )

    # Draw the eye based on direction
    eye_offset_x = fish['size'] // 3 if fish['direction'][0] >= 0 else -fish['size'] // 3
    eye_offset_y = fish['size'] // 4 if fish['direction'][1] <= 0 else fish['size'] // 2
    midpoint_circle(
        fish['x'] + body_offset_x + eye_offset_x,
        fish['y'] + body_offset_y + eye_offset_y,
        fish['size'] // 5,
        (1, 1, 1)
    )
def draw_points():
    global expanding_radius, expanding_direction
    for point in points:
        if point['type'] == 'green':
            # Draw concentric circles for green points
            midpoint_circle(point['x'], point['y'], expanding_radius, (0.0, 0.5, 0.0))  # Dark green outer
            midpoint_circle(point['x'], point['y'], expanding_radius - 2, (0.0, 0.5, 0.0))  # Second dark green outer
            midpoint_circle(point['x'], point['y'], expanding_radius - 4, (0.6, 1.0, 0.6))  # Light green middle
            midpoint_circle(point['x'], point['y'], expanding_radius - 6, (0.6, 1.0, 0.6))  # Second light green middle
            midpoint_circle(point['x'], point['y'], expanding_radius - 8, (0.0, 0.5, 0.0))  # Dark green inner

        elif point['type'] == 'red':
            # Draw concentric circles for red points
            midpoint_circle(point['x'], point['y'], expanding_radius, (1.0, 0.0, 0.0))  # Red outer
            midpoint_circle(point['x'], point['y'], expanding_radius - 2, (1.0, 0.0, 0.0))  # Second red outer
            midpoint_circle(point['x'], point['y'], expanding_radius - 4, (1.0, 0.5, 0.0))  # Orange middle
            midpoint_circle(point['x'], point['y'], expanding_radius - 6, (1.0, 0.5, 0.0))  # Second orange middle
            midpoint_circle(point['x'], point['y'], expanding_radius - 8, (1.0, 0.0, 0.0))  # Red inner

    expanding_radius += expanding_direction * expanding_shrink_rate
    if expanding_radius >= 15 or expanding_radius <= 10:
        expanding_direction *= -1

# Draw scores
def draw_scores():
    glColor3f(0, 0, 1)
    glRasterPos2i(50, WINDOW_HEIGHT - 30)
    score1 = f"Player 1 Score: {fish1['score']}"
    for char in score1:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    glColor3f(0.8, 0, 0.8)
    glRasterPos2i(WINDOW_WIDTH - 250, WINDOW_HEIGHT - 30)
    score2 = f"Player 2 Score: {fish2['score']}"
    for char in score2:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

# Update game state
def update_points():
    global points
    new_points = []
    for point in points:
        point['time'] -= 1
        if point['time'] > 0:
            new_points.append(point)
    if len(new_points) < 7:
        for _ in range(7 - len(new_points)):
            x = random.randint(10, WINDOW_WIDTH - 10)
            y = random.randint(10, WINDOW_HEIGHT - 10)
            point_type = 'green' if random.random() > 0.3 else 'red'
            new_points.append({'x': x, 'y': y, 'type': point_type, 'time': 300})
    points = new_points

def move_fish(fish):
    fish['x'] += int(fish['direction'][0] * fish['speed'])
    fish['y'] += int(fish['direction'][1] * fish['speed'])
    if fish['x'] < 0 or fish['x'] > WINDOW_WIDTH:
        fish['direction'] = (-fish['direction'][0], fish['direction'][1])
    if fish['y'] < 0 or fish['y'] > WINDOW_HEIGHT:
        fish['direction'] = (fish['direction'][0], -fish['direction'][1])

def check_collision(fish):
    global game_over, winner, show_end_message
    opponent = fish2 if fish is fish1 else fish1
    for point in points:
        if math.dist((fish['x'], fish['y']), (point['x'], point['y'])) < fish['size'] + 10:
            if point['type'] == 'green':
                fish['size'] += 3
                fish['score'] += 1
            elif point['type'] == 'red':
                opponent['size']-= 3
                opponent['score'] -= 1
            if fish['score'] >= 10:
                game_over = True
                winner = 'Player 1' if fish is fish1 else 'Player 2'
                glutTimerFunc(1000, show_message, 0)  # Pause for 1 second before showing the message
                return
            elif opponent['score'] < 0:
                game_over = True
                winner = 'Player 1' if fish is fish1 else 'Player 2'
                glutTimerFunc(1000, show_message, 0)  # Pause for 1 second before showing the message
                return
            points.remove(point)
            break

def show_message(value):
    global show_end_message
    show_end_message = True

# Display callback
def display():
    global game_over, winner, show_end_message, paused
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(0.7, 0.9, 1.0, 1)  # Lightened sky blue background
    

    if game_over and show_end_message:
        # Display "The Game End" in red
        glColor3f(1, 0, 0)  # Red
        glRasterPos2i(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 40)
        message1 = "The Game End!!!"
        for char in message1:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        
        # Display winner message in blue
        glColor3f(0, 0, 1)  # Blue
        glRasterPos2i(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2)
        if winner == 'Player 1':
            message2 = "Congratulations to Player 1"
            message3 = "Better luck next time to Player 2"
            message4 = "Press R to play again"
        else:
            message2 = "Congratulations to Player 2"
            message3 = "Better luck next time to Player 1"
            message4 = "Press R to play again"
        
        for char in message2:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        
        # Display consolation message in blue
        glRasterPos2i(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 40)
        for char in message3:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
    else:
        # Draw the main game scene
        draw_bubbles()
        draw_aquarium_floor()
        draw_fish(fish1, (0, 0, 1), (0.0, 0.0, 0.502),(0.0, 0.0, 0.502))  # Blue fish
        draw_fish(fish2, (0.8, 0, 0.8), (0.502, 0.0, 0.0),(0.502, 0.0, 0.0))  # Purple fish
        draw_points()
        draw_scores()
        draw_buttons()
        draw_random_wavy_points()
    
    # Swap the buffers to display the updated frame
    glutSwapBuffers()

# Timer callback
def timer(value):
    global paused
    if not game_over and not paused:
        move_fish(fish1)
        move_fish(fish2)
        check_collision(fish1)
        check_collision(fish2)
        update_points()
    glutPostRedisplay()
    glutTimerFunc(30, timer, 0)

def mouse(button, state, x, y):
    global paused
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        y_adjusted = WINDOW_HEIGHT - y  # Adjust for OpenGL's coordinate system
        if is_inside_button(x, y_adjusted, BUTTON_LEFT):
            reset_game()
        elif is_inside_button(x, y_adjusted, BUTTON_PAUSE):
            paused = not paused
            print("Paused" if paused else "Playing")
        elif is_inside_button(x, y_adjusted, BUTTON_EXIT):
            exit_game()
# Keyboard callback
def keyboard(key, x, y):
    global paused
    if key == b'w':
        fish1['direction'] = (0, 1)
    elif key == b's':
        fish1['direction'] = (0, -1)
    elif key == b'a':
        fish1['direction'] = (-1, 0)
    elif key == b'd':
        fish1['direction'] = (1, 0)
    elif key==b' ':
        paused = not paused
        print("Paused" if paused else "Playing")
    elif key == b'r' and game_over:
        reset_game()


# Special keys callback
# Special keys callback
def special(key, x, y):
    if key == GLUT_KEY_UP:
        fish2['direction'] = (0, 1)
    elif key == GLUT_KEY_DOWN:
        fish2['direction'] = (0, -1)
    elif key == GLUT_KEY_LEFT:
        fish2['direction'] = (-1, 0)
    elif key == GLUT_KEY_RIGHT:
        fish2['direction'] = (1, 0)

# Initialize OpenGL
def init():
    glClearColor(0, 0, 0, 1)
    glMatrixMode(GL_PROJECTION)
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

# Initialize and start the game
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
glutCreateWindow(b"Fish Game")
init()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutSpecialFunc(special)
glutMouseFunc(mouse)
glutTimerFunc(30, timer, 0)
glutMainLoop()
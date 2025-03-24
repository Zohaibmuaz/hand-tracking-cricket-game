import cv2
import mediapipe as mp
import pygame
import random
import threading
import time

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize Video Capture
cap = cv2.VideoCapture(0)

# Pygame Initialization (Game Window)
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Cricket Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Game Variables
ball_x = random.randint(50, WIDTH - 50)
ball_y = 50
ball_radius = 15
ball_speed = 5

bat_width = 100
bat_height = 15
bat_x = WIDTH // 2 - bat_width // 2  # Start in the center
bat_y = HEIGHT - 50

score = 0
swing_detected = False
cooldown = 0.5
last_swing_time = 0
prev_wrist_y = None

# Function to detect hand movement
def detect_hand():
    global bat_x, swing_detected, last_swing_time, prev_wrist_y

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Mirror effect
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(frame_rgb)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark
            
            # Get wrist positions
            wrist_x = int(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x * WIDTH)
            wrist_y = int(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y * HEIGHT)

            # Move bat with hand
            bat_x = max(0, min(WIDTH - bat_width, wrist_x - bat_width // 2))

            # Detect fast upward motion as swing
            if prev_wrist_y is not None:
                movement = prev_wrist_y - wrist_y
                if movement > 30 and (time.time() - last_swing_time > cooldown):
                    swing_detected = True
                    last_swing_time = time.time()

            prev_wrist_y = wrist_y

        # Show webcam feed
        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to update game logic
def game_logic():
    global ball_y, ball_x, score, swing_detected

    ball_y += ball_speed  # Ball falls down

    # Reset ball if it falls out
    if ball_y > HEIGHT:
        ball_x = random.randint(50, WIDTH - 50)
        ball_y = 50

    # Check if bat hits ball
    if swing_detected:
        if bat_y - 10 <= ball_y <= bat_y + 10 and bat_x <= ball_x <= bat_x + bat_width:
            score += random.randint(1, 6)  # Random cricket scoring
            ball_x = random.randint(50, WIDTH - 50)
            ball_y = 50
            swing_detected = False  # Reset swing detection

# Function to draw game objects
def draw_game():
    screen.fill(WHITE)
    pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)  # Ball
    pygame.draw.rect(screen, BLUE, (bat_x, bat_y, bat_width, bat_height))  # Bat
    
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, GREEN)
    screen.blit(score_text, (10, 10))  # Display score
    pygame.display.flip()

# Game loop
def game_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        game_logic()
        draw_game()
        pygame.time.delay(30)

# Start webcam tracking in a separate thread
webcam_thread = threading.Thread(target=detect_hand)
webcam_thread.daemon = True
webcam_thread.start()

# Start the game loop
game_loop()

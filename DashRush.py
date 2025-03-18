import pygame
import random
import time
import os

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
PLAYER_SIZE = 50
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 50, 50
LANES = [150, 300, 450]  # Y positions for the three lanes, further apart
SPEED = 5
FONT = pygame.font.Font(None, 36)
SAVE_FILE = "highscore.txt"

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DashRun")

# Load assets
player_img = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
player_img.fill((255, 0, 0))  # Red square for player

# Create blue box obstacle
obstacle_img = pygame.Surface((OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
obstacle_img.fill((0, 0, 255))  # Blue square for obstacles

# Load saved high score
def load_high_score():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            return int(file.read().strip())
    return 0

def save_high_score(score):
    with open(SAVE_FILE, "w") as file:
        file.write(str(score))

# Player setup
player_x = 100
player_y = LANES[1]
player_lane = 1
jumping = False
jump_height = 150  # Increased jump height
jump_velocity = -15  # Increased jump velocity for higher jumps
player_velocity_y = 0

default_gravity = 1  # Reduced gravity to extend air time
gravity = default_gravity

# Game state
high_score = load_high_score()
running = False  # Game starts from the menu

# Function to show menu
def show_menu():
    menu_running = True
    while menu_running:
        screen.fill(WHITE)
        title_text = FONT.render("Temple Run Clone", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        
        start_button = pygame.Rect(WIDTH // 2 - 100, 250, 200, 50)
        pygame.draw.rect(screen, GREEN, start_button)
        
        start_text = FONT.render("Start New Game", True, BLACK)
        highscore_text = FONT.render(f"Highscore: {high_score}s", True, BLACK)
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 260))
        screen.blit(highscore_text, (WIDTH // 2 - highscore_text.get_width() // 2, 360))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return True

# Start the game
running = show_menu()

def reset_game():
    global player_y, player_lane, jumping, obstacles, start_time
    player_y = LANES[1]
    player_lane = 1
    jumping = False
    obstacles.clear()
    start_time = time.time()

# Obstacle setup
obstacles = []
obstacle_spawn_timer = 0
spawn_delay = 1000  # Initial spawn delay in milliseconds

# Timer
start_time = time.time()
clock = pygame.time.Clock()

while running:
    screen.fill(GREEN)
    
    # Draw lane separators
    pygame.draw.line(screen, BLACK, (0, 225), (WIDTH, 225), 5)
    pygame.draw.line(screen, BLACK, (0, 375), (WIDTH, 375), 5)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and player_lane > 0:
                player_lane -= 1
                player_y = LANES[player_lane]
            elif event.key == pygame.K_DOWN and player_lane < 2:
                player_lane += 1
                player_y = LANES[player_lane]
            elif event.key == pygame.K_SPACE and not jumping:
                jumping = True
                player_velocity_y = jump_velocity
    
    # Jump physics
    if jumping:
        player_y += player_velocity_y
        player_velocity_y += gravity
        if player_y >= LANES[player_lane]:  # Land back on the lane
            player_y = LANES[player_lane]
            jumping = False
    
    # Spawn obstacles
    if pygame.time.get_ticks() - obstacle_spawn_timer > spawn_delay:
        obstacle_lane = random.randint(0, 2)
        obstacles.append([WIDTH, LANES[obstacle_lane]])
        obstacle_spawn_timer = pygame.time.get_ticks()
    
    # Move and draw obstacles
    for obstacle in obstacles[:]:
        obstacle[0] -= SPEED
        screen.blit(obstacle_img, (obstacle[0], obstacle[1]))
        if obstacle[0] < -OBSTACLE_WIDTH:
            obstacles.remove(obstacle)
    
    # Check for collisions
    elapsed_time = int(time.time() - start_time)
    for obstacle in obstacles:
        if player_x + PLAYER_SIZE > obstacle[0] and player_x < obstacle[0] + OBSTACLE_WIDTH:
            if player_y == obstacle[1] and not jumping:
                print("Game Over! Restarting...")
                if elapsed_time > high_score:
                    high_score = elapsed_time
                    save_high_score(high_score)
                reset_game()
                break
    
    # Draw player
    screen.blit(player_img, (player_x, player_y))
    
    # Timer
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_text = FONT.render(f"Time: {minutes:02}:{seconds:02}", True, BLACK)
    screen.blit(timer_text, (10, 10))
    
    # Measure FPS
    fps = int(clock.get_fps())
    fps_text = FONT.render(f"FPS: {fps}", True, BLACK)
    screen.blit(fps_text, (WIDTH - 100, 10))  # Display FPS at the top right corner
    
    pygame.display.flip()
    clock.tick(31)  # Cap FPS at 30

    

pygame.quit()

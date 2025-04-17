
# Import required modules
import pygame
import random
import time
import os

# Initialize pygame
pygame.init()

# Constants for screen size and colors
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (160, 32, 240)

# Constants for player and obstacle sizes
PLAYER_SIZE = 50
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 50, 50
LANES = [150, 300, 450]
FONT = pygame.font.Font(None, 36)

# Base directory for saving files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR, "highscore.txt")
DIFFICULTY_FILE = os.path.join(BASE_DIR, "difficulty.txt")

# Difficulty speed boundaries
MIN_SPEED = 3
MAX_SPEED = 12

# Set up display window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DashRush")

# Create game assets
player_img = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
player_img.fill(RED)
obstacle_img = pygame.Surface((OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
obstacle_img.fill(BLUE)
chaser_img = pygame.Surface((OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
chaser_img.fill(PURPLE)
powerup_img = pygame.Surface((30, 30))
powerup_img.fill((255, 255, 0))

# Load/save utility functions
def load_high_score():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            return int(file.read().strip())
    return 0

def save_high_score(score):
    with open(SAVE_FILE, "w") as file:
        file.write(str(score))

def load_difficulty():
    if os.path.exists(DIFFICULTY_FILE):
        with open(DIFFICULTY_FILE, "r") as file:
            return int(file.read().strip())
    return 50

def save_difficulty(difficulty):
    with open(DIFFICULTY_FILE, "w") as file:
        file.write(str(difficulty))

def get_speed_from_difficulty(difficulty):
    return MIN_SPEED + (MAX_SPEED - MIN_SPEED) * (difficulty / 100)

def get_spawn_delay(difficulty):
    return max(500, 1500 - 10 * difficulty)

# AI Agent class for DDA
class DDAAgent:
    def __init__(self, initial_difficulty):
        self.difficulty = initial_difficulty
        self.recent_scores = []
        self.performance_streak = 0
        self.last_performance = None
        self.powerup_assist = False

    def update_difficulty(self, elapsed_time, high_score):
        performance_ratio = elapsed_time / high_score if high_score > 0 else 0
        self.recent_scores.append(elapsed_time)
        if len(self.recent_scores) > 5:
            self.recent_scores.pop(0)

        # Evaluate current performance
        if performance_ratio > 0.8:
            current = "good"
        elif performance_ratio < 0.3:
            current = "bad"
        else:
            current = "neutral"

        # Update streak tracking
        if current == self.last_performance and current in ["good", "bad"]:
            self.performance_streak += 1
        elif current in ["good", "bad"]:
            self.performance_streak = 1
        else:
            self.performance_streak = 0

        self.last_performance = current

        # Adjust difficulty only after 3 same-type performances
        if self.performance_streak >= 3:
            if current == "good":
                self.difficulty = min(100, self.difficulty + 5)
                self.powerup_assist = False
            elif current == "bad":
                self.difficulty = max(0, self.difficulty - 5)
                self.powerup_assist = True
            self.performance_streak = 0  # Reset streak after adjustment

        else:
            self.powerup_assist = (current == "bad")

        return self.difficulty

    def should_drop_extra_powerups(self):
        return self.powerup_assist

# Game state
player_x = 100
player_y = LANES[1]
player_lane = 1
jumping = False
jump_velocity = -15
player_velocity_y = 0
gravity = 1
high_score = load_high_score()
difficulty = load_difficulty()
session_difficulty = difficulty
dda_agent = DDAAgent(difficulty)
SPEED = get_speed_from_difficulty(session_difficulty)
running = False

# Menu
def show_menu():
    menu_running = True
    while menu_running:
        screen.fill(WHITE)
        title_text = FONT.render("DashRush", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        start_button = pygame.Rect(WIDTH // 2 - 100, 250, 200, 50)
        pygame.draw.rect(screen, GREEN, start_button)
        start_text = FONT.render("Start Game", True, BLACK)
        highscore_text = FONT.render(f"Highscore: {high_score}s", True, BLACK)
        diff_text = FONT.render(f"Difficulty: {difficulty}", True, BLACK)
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 260))
        screen.blit(highscore_text, (WIDTH // 2 - highscore_text.get_width() // 2, 330))
        screen.blit(diff_text, (WIDTH // 2 - diff_text.get_width() // 2, 370))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    save_difficulty(difficulty)
                    return True

running = show_menu()

def adjust_difficulty(elapsed_time):
    global difficulty, session_difficulty
    difficulty = dda_agent.update_difficulty(elapsed_time, high_score)
    session_difficulty = difficulty
    save_difficulty(difficulty)

def reset_game():
    global player_y, player_lane, jumping, obstacles, chasers, powerups
    global start_time, SPEED, obstacle_spawn_timer, chaser_spawn_timer, session_difficulty
    player_y = LANES[1]
    player_lane = 1
    jumping = False
    obstacles.clear()
    chasers.clear()
    powerups.clear()
    start_time = time.time()
    session_difficulty = difficulty
    SPEED = get_speed_from_difficulty(session_difficulty)
    obstacle_spawn_timer = pygame.time.get_ticks()
    chaser_spawn_timer = pygame.time.get_ticks()

obstacles = []
chasers = []
powerups = []

obstacle_spawn_timer = 0
chaser_spawn_timer = 0
powerup_timer = 0
powerup_interval = 8000
chaser_interval = 3000

spawn_delay = get_spawn_delay(session_difficulty)
start_time = time.time()
clock = pygame.time.Clock()

# Main game loop
while running:
    screen.fill(GREEN)
    pygame.draw.line(screen, BLACK, (0, 225), (WIDTH, 225), 5)
    pygame.draw.line(screen, BLACK, (0, 375), (WIDTH, 375), 5)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and player_lane > 0:
                player_lane -= 1
            elif event.key == pygame.K_DOWN and player_lane < 2:
                player_lane += 1
            elif event.key == pygame.K_SPACE and not jumping:
                jumping = True
                player_velocity_y = jump_velocity

    target_y = LANES[player_lane]
    if not jumping:
        player_y += (target_y - player_y) * 0.2
    if jumping:
        player_y += player_velocity_y
        player_velocity_y += gravity
        if player_y >= LANES[player_lane]:
            player_y = LANES[player_lane]
            jumping = False

    current_time = pygame.time.get_ticks()

    if current_time - obstacle_spawn_timer > spawn_delay:
        lane = random.randint(0, 2)
        obstacles.append([WIDTH, LANES[lane]])
        obstacle_spawn_timer = current_time

    if current_time - chaser_spawn_timer > chaser_interval:
        lane = random.randint(0, 2)
        direction = random.choice([-1, 1])
        chasers.append([WIDTH, LANES[lane], direction])
        chaser_spawn_timer = current_time

    if (session_difficulty <= 30 or dda_agent.should_drop_extra_powerups()) and current_time - powerup_timer > powerup_interval:
        lane = random.randint(0, 2)
        powerups.append([WIDTH, LANES[lane]])
        powerup_timer = current_time

    for obstacle in obstacles[:]:
        obstacle[0] -= SPEED
        screen.blit(obstacle_img, (obstacle[0], obstacle[1]))
        if obstacle[0] < -OBSTACLE_WIDTH:
            obstacles.remove(obstacle)

    for chaser in chasers[:]:
        chaser_speed = 0.8 * SPEED
        vertical_speed = 1 + (session_difficulty / 10)
        chaser[0] -= chaser_speed
        if random.random() < 0.02:
            chaser[2] *= -1
        chaser[1] += chaser[2] * vertical_speed
        chaser[1] = max(min(chaser[1], LANES[2]), LANES[0])
        screen.blit(chaser_img, (chaser[0], chaser[1]))
        if chaser[0] < -OBSTACLE_WIDTH:
            chasers.remove(chaser)

    for powerup in powerups[:]:
        powerup[0] -= SPEED
        screen.blit(powerup_img, (powerup[0], powerup[1]))
        if powerup[0] < -30:
            powerups.remove(powerup)

    elapsed_time = int(time.time() - start_time)

    for obstacle in obstacles:
        if player_x + PLAYER_SIZE > obstacle[0] and player_x < obstacle[0] + OBSTACLE_WIDTH:
            if abs(player_y - obstacle[1]) < 10 and not jumping:
                if elapsed_time > high_score:
                    high_score = elapsed_time
                    save_high_score(high_score)
                adjust_difficulty(elapsed_time)
                reset_game()
                break

    for chaser in chasers:
        if player_x + PLAYER_SIZE > chaser[0] and player_x < chaser[0] + OBSTACLE_WIDTH:
            if abs(player_y - chaser[1]) < 10:
                if elapsed_time > high_score:
                    high_score = elapsed_time
                    save_high_score(high_score)
                adjust_difficulty(elapsed_time)
                reset_game()
                break

    for powerup in powerups[:]:
        if player_x + PLAYER_SIZE > powerup[0] and player_x < powerup[0] + 30:
            if abs(player_y - powerup[1]) < 10:
                session_difficulty = max(0, session_difficulty - 10)
                SPEED = get_speed_from_difficulty(session_difficulty)
                spawn_delay = get_spawn_delay(session_difficulty)
                powerups.remove(powerup)

    screen.blit(player_img, (player_x, player_y))
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_text = FONT.render(f"Time: {minutes:02}:{seconds:02}", True, BLACK)
    screen.blit(timer_text, (10, 10))
    fps = int(clock.get_fps())
    screen.blit(FONT.render(f"FPS: {fps}", True, BLACK), (WIDTH - 100, 10))
    screen.blit(FONT.render(f"Difficulty: {session_difficulty}", True, BLACK), (WIDTH // 2 - 80, 10))
    pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 100, 40, 200, 15), 2)
    pygame.draw.rect(screen, RED, (WIDTH // 2 - 100, 40, 2 * session_difficulty, 15))

    feedback_msg = ""
    if dda_agent.powerup_assist:
        feedback_msg = "You're struggling — AI Assist Activated!"
    elif session_difficulty >= 90:
        feedback_msg = "You're crushing it — max difficulty soon!"
    feedback_text = FONT.render(feedback_msg, True, BLACK)
    screen.blit(feedback_text, (WIDTH // 2 - feedback_text.get_width() // 2, HEIGHT - 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

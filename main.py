import random
import math
import pygame
from pygame import mixer

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# --- Asset Loading ---
# Images
background_img = pygame.image.load("space.png")
icon_img = pygame.image.load('logo.png')
pygame.display.set_icon(icon_img)
pygame.display.set_caption('Galaxy Defenders')

enemyImg_template = pygame.image.load("enemy.png")
enemy_width = enemyImg_template.get_width()
enemy_height = enemyImg_template.get_height()

bulletImg = pygame.image.load("bullet.png")
bullet_width = bulletImg.get_width()
bullet_height = bulletImg.get_height()

intro_bg_img = pygame.image.load("intro.png")
intro_bg_img = pygame.transform.scale(intro_bg_img, (screen_width, screen_height))
player1_preview_img = pygame.image.load("player1.png")
player2_preview_img = pygame.image.load("player2.png")

# Fonts
font = pygame.font.Font('freesansbold.ttf', 32)
over_font = pygame.font.Font('freesansbold.ttf', 64)
intro_title_font = pygame.font.Font('freesansbold.ttf', 70)
intro_choice_font = pygame.font.Font('freesansbold.ttf', 40)
intro_instruction_font = pygame.font.Font('freesansbold.ttf', 25)
pause_font = pygame.font.Font('freesansbold.ttf', 64)

# --- Game Constants ---
player_speed = 5
base_enemy_speed = 1.5
num_of_enemies = 6
enemy_row_drop_amount = enemy_height / 2
bullet_speed = 10
MAX_SCORE_TO_WIN = 100
INITIAL_LIVES = 3

# --- Game Variables (will be initialized/reset) ---
playerImg = None
player_width = 0
player_height = 0
playerX, playerY = 0, 0
playerX_change, playerY_change = 0, 0

enemyImg_list = []
enemyX, enemyY, enemyX_change_list = [], [], []

bulletX, bulletY = 0, 0
bulletY_change = -bullet_speed
bullet_state = "ready"

score_value = 0
amounts_of_lives = INITIAL_LIVES
game_is_over = False
win_condition_met = False
GAME_OVER_ENEMY_Y_THRESHOLD = 0

# --- Game State ---
current_state = "INTRO"  # "INTRO", "PLAYING", "PAUSED", "GAME_OVER"


# --- Helper Functions ---
def draw_text(surface, text, text_font, color, x, y, center=False):
    text_surface = text_font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def reset_game_state():
    global playerX, playerY, playerX_change, playerY_change, GAME_OVER_ENEMY_Y_THRESHOLD
    global score_value, amounts_of_lives, game_is_over, win_condition_met
    global enemyX, enemyY, enemyX_change_list, enemyImg_list
    global bullet_state, bulletX, bulletY

    playerX = (screen_width - player_width) / 2
    playerY = screen_height - player_height - 30
    playerX_change = 0
    playerY_change = 0
    GAME_OVER_ENEMY_Y_THRESHOLD = playerY

    score_value = 0
    amounts_of_lives = INITIAL_LIVES
    game_is_over = False
    win_condition_met = False

    enemyX = []
    enemyY = []
    enemyX_change_list = []
    enemyImg_list = []
    for i in range(num_of_enemies):
        enemyImg_list.append(enemyImg_template)
        enemyX.append(random.randint(0, screen_width - enemy_width))
        enemyY.append(random.randint(50, 150))
        initial_direction = base_enemy_speed if random.choice([True, False]) else -base_enemy_speed
        enemyX_change_list.append(initial_direction)

    bullet_state = "ready"
    bulletX = 0
    bulletY = playerY


def show_scores_and_lives(x, y):
    score_render = font.render("Score: " + str(score_value) + " Lives: " + str(amounts_of_lives), True, (255, 255, 255))
    screen.blit(score_render, (x, y))


def display_final_message():
    message = "GAME OVER"
    if win_condition_met:
        message = "YOU WIN!"
    draw_text(screen, message, over_font, (255, 255, 255), screen_width / 2, screen_height / 2 - 50, center=True)


def fire_bullet_func(pX, pY):
    global bullet_state, bulletX, bulletY
    if bullet_state == "ready":
        bullet_state = "fire"
        bulletX = pX + (player_width / 2) - (bullet_width / 2)
        bulletY = pY


def is_aabb_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    rect1 = pygame.Rect(x1, y1, w1, h1)
    rect2 = pygame.Rect(x2, y2, w2, h2)
    return rect1.colliderect(rect2)


def is_distance_collision(obj1_center_x, obj1_center_y, obj2_center_x, obj2_center_y, threshold):
    distance = math.sqrt(math.pow(obj1_center_x - obj2_center_x, 2) + math.pow(obj1_center_y - obj2_center_y, 2))
    return distance < threshold


def draw_player(x, y):
    if playerImg:
        screen.blit(playerImg, (x, y))


def draw_enemy(x, y, index):
    screen.blit(enemyImg_list[index], (x, y))


def draw_bullet(x, y):
    screen.blit(bulletImg, (x, y))


# --- Main Loop ---
mixer.music.load("intro_song.mpeg")
mixer.music.play(-1)

running = True
while running:
    screen.fill((0, 0, 0))

    if current_state == "INTRO":
        screen.blit(intro_bg_img, (0, 0))
        draw_text(screen, "Galaxy Defenders", intro_title_font, (255, 255, 255), screen_width / 2, screen_height / 4,
                  center=True)
        choice1_y = screen_height / 2 - 20
        choice2_y = screen_height / 2 + 80
        instruction_y = screen_height / 2 + 180
        exit_instruction_y = instruction_y + 40

        p1_preview_x = screen_width / 4 - player1_preview_img.get_width() / 2
        screen.blit(player1_preview_img, (p1_preview_x, choice1_y - player1_preview_img.get_height() / 2))
        draw_text(screen, "Press 1 for Player 1", intro_choice_font, (255, 255, 255), screen_width * 0.6, choice1_y,
                  center=True)
        p2_preview_x = screen_width / 4 - player2_preview_img.get_width() / 2
        screen.blit(player2_preview_img, (p2_preview_x, choice2_y - player2_preview_img.get_height() / 2))
        draw_text(screen, "Press 2 for Player 2", intro_choice_font, (255, 255, 255), screen_width * 0.6, choice2_y,
                  center=True)
        draw_text(screen, "Select your ship!", intro_instruction_font, (200, 200, 200), screen_width / 2, instruction_y,
                  center=True)
        draw_text(screen, "Press ESC to Exit Game", intro_instruction_font, (200, 200, 200), screen_width / 2, exit_instruction_y,
                  center=True)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # ESC quits the game from INTRO
                    running = False
                selected_player_path = None
                if event.key == pygame.K_1: selected_player_path = "player1.png"
                elif event.key == pygame.K_2: selected_player_path = "player2.png"

                if selected_player_path:
                    playerImg = pygame.image.load(selected_player_path)
                    player_width = playerImg.get_width()
                    player_height = playerImg.get_height()
                    reset_game_state()
                    mixer.music.stop()
                    mixer.music.load("background.wav")
                    mixer.music.play(-1)
                    current_state = "PLAYING"

    elif current_state == "PLAYING":
        screen.blit(background_img, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # ESC goes to INTRO
                    current_state = "INTRO"
                    mixer.music.stop()
                    mixer.music.load("intro_song.mpeg")
                    mixer.music.play(-1)
                elif event.key == pygame.K_p: # 'P' pauses the game
                    current_state = "PAUSED"
                    mixer.music.pause()
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a: playerX_change = -player_speed
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d: playerX_change = player_speed
                elif event.key == pygame.K_UP or event.key == pygame.K_w: playerY_change = -player_speed
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s: playerY_change = player_speed
                elif event.key == pygame.K_SPACE:
                    if bullet_state == "ready":
                        bullet_sound = mixer.Sound('laser.wav'); bullet_sound.play()
                        fire_bullet_func(playerX, playerY)
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d): playerX_change = 0
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s): playerY_change = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and bullet_state == "ready": # Left mouse click
                    bullet_sound = mixer.Sound('laser.wav'); bullet_sound.play()
                    fire_bullet_func(playerX, playerY)

        playerX += playerX_change; playerY += playerY_change
        if playerX <= 0: playerX = 0
        elif playerX >= screen_width - player_width: playerX = screen_width - player_width
        if playerY <= 0: playerY = 0
        elif playerY >= screen_height - player_height: playerY = screen_height - player_height

        for i in range(num_of_enemies):
            if game_is_over: break
            enemyX[i] += enemyX_change_list[i]
            wall_hit = False
            if enemyX[i] <= 0 and enemyX_change_list[i] < 0:
                enemyX[i] = 0; enemyX_change_list[i] *= -1; wall_hit = True
            elif enemyX[i] >= screen_width - enemy_width and enemyX_change_list[i] > 0:
                enemyX[i] = screen_width - enemy_width; enemyX_change_list[i] *= -1; wall_hit = True
            if wall_hit: enemyY[i] += enemy_row_drop_amount

            life_lost_this_iteration = False
            if is_aabb_collision(playerX, playerY, player_width, player_height, enemyX[i], enemyY[i], enemy_width, enemy_height) or \
               (enemyY[i] + enemy_height >= GAME_OVER_ENEMY_Y_THRESHOLD and enemyY[i] < screen_height): # Check enemy is on screen
                amounts_of_lives -= 1; life_lost_this_iteration = True
                if amounts_of_lives <= 0:
                    game_is_over = True; win_condition_met = False
                    for j in range(num_of_enemies): enemyY[j] = screen_height + 100 # Move enemies off-screen
                    break
                else: # Player loses a life but game continues
                    playerX = (screen_width - player_width) / 2 # Reset player
                    playerY = screen_height - player_height - 30
                    enemyX[i] = random.randint(0, screen_width - enemy_width) # Reset specific enemy
                    enemyY[i] = random.randint(50, 100)
            if life_lost_this_iteration and amounts_of_lives > 0: continue

        if bullet_state == "fire" and not game_is_over:
            bulletY += bulletY_change
            if bulletY + bullet_height <= 0: bullet_state = "ready"
            else:
                for i in range(num_of_enemies):
                    if enemyY[i] > screen_height: continue # Skip off-screen enemies
                    bullet_cx = bulletX + bullet_width / 2; bullet_cy = bulletY + bullet_height / 2
                    enemy_cx = enemyX[i] + enemy_width / 2; enemy_cy = enemyY[i] + enemy_height / 2
                    coll_thresh = (enemy_width / 2 + bullet_width / 2) * 0.8
                    if is_distance_collision(enemy_cx, enemy_cy, bullet_cx, bullet_cy, coll_thresh):
                        explosion_sound = mixer.Sound("explosion.wav"); explosion_sound.play()
                        bullet_state = "ready"; score_value += 1
                        enemyX[i] = random.randint(0, screen_width - enemy_width)
                        enemyY[i] = random.randint(50, 100) # Respawn enemy
                        if score_value >= MAX_SCORE_TO_WIN:
                            game_is_over = True; win_condition_met = True
                            for j in range(num_of_enemies): enemyY[j] = screen_height + 100 # Move enemies off-screen
                        break
        if game_is_over:
            current_state = "GAME_OVER"; mixer.music.stop()
            # Optional: Play win/lose sound here

        draw_player(playerX, playerY)
        for i in range(num_of_enemies):
            if enemyY[i] < screen_height: draw_enemy(enemyX[i], enemyY[i], i)
        if bullet_state == "fire": draw_bullet(bulletX, bulletY)
        show_scores_and_lives(10, 10)

    elif current_state == "PAUSED":
        screen.blit(intro_bg_img, (0,0))
        draw_text(screen, "PAUSED", pause_font, (255, 255, 255), screen_width / 2, screen_height / 3, center=True)
        draw_text(screen, "Press P to Resume", intro_instruction_font, (200, 200, 200), screen_width / 2, screen_height / 2, center=True)
        draw_text(screen, "Press ESC for Main Menu", intro_instruction_font, (200, 200, 200), screen_width / 2, screen_height / 2 + 40, center=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # ESC goes to INTRO
                    current_state = "INTRO"
                    mixer.music.stop() # Stop paused music
                    mixer.music.load("intro_song.mpeg")
                    mixer.music.play(-1)
                elif event.key == pygame.K_p: # 'P' resumes the game
                    current_state = "PLAYING"
                    mixer.music.unpause()

    elif current_state == "GAME_OVER":
        screen.blit(background_img, (0, 0))
        display_final_message()
        draw_text(screen, "Final Score: " + str(score_value), font, (255, 255, 255), screen_width / 2, screen_height / 2 + 40, center=True)
        draw_text(screen, "Press ENTER or ESC for Main Menu", intro_instruction_font, (200, 200, 200),
                  screen_width / 2, screen_height * 0.75, center=True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN: # ESC or ENTER goes to INTRO
                    current_state = "INTRO"
                    mixer.music.stop()
                    mixer.music.load("intro_song.mpeg")
                    mixer.music.play(-1)

    pygame.display.update()

pygame.quit()
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 11:05:00 2013

@author: Leo
"""

import pygame
from sys import exit
from pygame.locals import *
from gameRole import *
import random

# Initialize the game
pygame.init()

# Define constants
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 700

# Initialize variables globally
bullet_img = None
enemy1_img = None
enemy1_down_imgs = []
enemy1_rect = None  # Define enemy1_rect globally
enemies1 = pygame.sprite.Group()
enemies_down = pygame.sprite.Group()
shoot_frequency = 0
enemy_frequency = 0
player_down_index = 16
score = 0
clock = pygame.time.Clock()
running = True
scores = []

# Function to initialize or reset the game
def init_game():
    global screen, bullet_sound, enemy1_down_sound, game_over_sound, background, game_over, plane_img, player, enemies1, enemies_down, shoot_frequency, enemy_frequency, player_down_index, score, clock, running, bullet_img, enemy1_img, enemy1_down_imgs, enemy1_rect, to_scoreboard, score_board

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Aircraft Battle')

    # Load game music
    bullet_sound = pygame.mixer.Sound('resources/sound/bullet.wav')
    enemy1_down_sound = pygame.mixer.Sound('resources/sound/enemy1_down.wav')
    game_over_sound = pygame.mixer.Sound('resources/sound/game_over.wav')
    bullet_sound.set_volume(0.3)
    enemy1_down_sound.set_volume(0.3)
    game_over_sound.set_volume(0.3)
    pygame.mixer.music.load('resources/sound/game_music.wav')
    pygame.mixer.music.play(-1, 0.0)
    pygame.mixer.music.set_volume(0.25)

    # Load background image
    background = pygame.image.load('resources/image/background.png').convert()
    game_over = pygame.image.load('resources/image/gameover.png')
    score_board = pygame.image.load('resources/image/score_board.png')

    filename = 'resources/image/shoot.png'
    plane_img = pygame.image.load(filename)

    # Set parameters related to the player
    player_rect = []
    player_rect.append(pygame.Rect(0, 99, 102, 126))        # Player sprite image area
    player_rect.append(pygame.Rect(165, 360, 102, 126))
    player_rect.append(pygame.Rect(165, 234, 102, 126))     # Player explosion sprite image area
    player_rect.append(pygame.Rect(330, 624, 102, 126))
    player_rect.append(pygame.Rect(330, 498, 102, 126))
    player_rect.append(pygame.Rect(432, 624, 102, 126))
    player_pos = [200, 600]
    player = Player(plane_img, player_rect, player_pos)

    # Define surface parameters for the bullet object
    bullet_rect = pygame.Rect(1004, 987, 9, 21)
    bullet_img = plane_img.subsurface(bullet_rect)

    # Define surface parameters for the enemy object
    enemy1_rect = pygame.Rect(534, 612, 57, 43)  # Initialize enemy1_rect here
    enemy1_img = plane_img.subsurface(enemy1_rect)
    enemy1_down_imgs = []
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 347, 57, 43)))
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(873, 697, 57, 43)))
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 296, 57, 43)))
    enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(930, 697, 57, 43)))

    enemies1 = pygame.sprite.Group()
    enemies_down = pygame.sprite.Group()

    shoot_frequency = 0
    enemy_frequency = 0

    player_down_index = 16

    score = 0

    clock = pygame.time.Clock()

    running = True

# Function to draw a button
show_scoreboard = False  # New global variable

def draw_button(text, x, y, width, height, inactive_color, active_color, action=None):
    global show_scoreboard  # Access the global variable

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Check if mouse is over button and change color
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1 and action is not None:
            # Instead of calling the action directly, set the flag to show the scoreboard
            if action == to_scoreboard:
                show_scoreboard = True  # Set flag to True when "Score Board" button is clicked
            elif action == back_to_game_over:  # For "Back" button on scoreboard
                show_scoreboard = False  # Set flag to False to go back to the game over screen
            else:
                action()  # Call other actions normally (like restart_game)
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))

    # Render button text
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=((x + (width / 2)), (y + (height / 2))))
    screen.blit(text_surf, text_rect)


# Restart the game
def restart_game():
    init_game()

def to_scoreboard():
    screen.blit(score_board, (0, 0))
    font = pygame.font.Font(None, 36)
    y_offset = 200
    for i, score in enumerate(scores):
        score_text = font.render(f"{i + 1}. {score}", True, (255, 255, 255))
        screen.blit(score_text, (150, y_offset))
        y_offset += 40

    # Draw "Back" button to go back to the game over screen
    draw_button('Back', 150, 600, 180, 50, (200, 0, 0), (255, 0, 0), back_to_game_over)

def save_score():
    global score, scores
    scores.append(score)  # Add current score to the list
    scores.sort(reverse=True)  # Sort the scores in descending order

def back_to_game_over():
    global show_scoreboard
    show_scoreboard = False  # Return to the game over screen

def player_dies():
    global running, player_down_index
    player.img_index = player_down_index // 8
    screen.blit(player.image[player.img_index], player.rect)
    player_down_index += 1
    if player_down_index > 47:
        save_score()  # Save the score when the player dies
        running = False

# Initialize game for the first time
init_game()

# Main game loop
while True:
    while running:
        # Control the game's maximum frame rate to 60
        clock.tick(45)

        # Control bullet firing frequency and fire bullets
        if not player.is_hit:
            if shoot_frequency % 15 == 0:
                bullet_sound.play()
                player.shoot(bullet_img)
            shoot_frequency += 1
            if shoot_frequency >= 15:
                shoot_frequency = 0

        # Generate enemy planes
        if enemy_frequency % 50 == 0:
            enemy1_pos = [random.randint(0, SCREEN_WIDTH - enemy1_rect.width), 0]
            enemy1 = Enemy(enemy1_img, enemy1_down_imgs, enemy1_pos)
            enemies1.add(enemy1)
        enemy_frequency += 1
        if enemy_frequency >= 100:
            enemy_frequency = 0

        # Move bullets; if they go out of the window range, delete them
        for bullet in player.bullets:
            bullet.move()
            if bullet.rect.bottom < 0:
                player.bullets.remove(bullet)

        # Move enemy planes; if they go out of the window range, delete them
        for enemy in enemies1:
            enemy.move()
            # Check if the player is hit
            if pygame.sprite.collide_circle(enemy, player):
                enemies_down.add(enemy)
                enemies1.remove(enemy)
                player.is_hit = True
                game_over_sound.play()
                break
            if enemy.rect.top > SCREEN_HEIGHT:
                enemies1.remove(enemy)

        # Add hit enemy objects to the destroyed enemy Group to render the destruction animation
        enemies1_down = pygame.sprite.groupcollide(enemies1, player.bullets, 1, 1)
        for enemy_down in enemies1_down:
            enemies_down.add(enemy_down)

        # Draw background
        screen.fill(0)
        screen.blit(background, (0, 0))

        # Draw player plane
        if not player.is_hit:
            screen.blit(player.image[player.img_index], player.rect)
            # Change the image index to make the plane have an animation effect
            player.img_index = shoot_frequency // 8
        else:
            player_dies()

        # Draw destruction animation
        for enemy_down in enemies_down:
            if enemy_down.down_index == 0:
                enemy1_down_sound.play()
            if enemy_down.down_index > 7:
                enemies_down.remove(enemy_down)
                score += 1000
                continue
            screen.blit(enemy_down.down_imgs[enemy_down.down_index // 2], enemy_down.rect)
            enemy_down.down_index += 1

        # Draw bullets and enemy planes
        player.bullets.draw(screen)
        enemies1.draw(screen)

        # Draw the score
        score_font = pygame.font.Font(None, 36)
        score_text = score_font.render(str(score), True, (128, 128, 128))
        text_rect = score_text.get_rect()
        text_rect.topleft = [10, 10]
        screen.blit(score_text, text_rect)

        # Update the screen
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Listen for keyboard events
        key_pressed = pygame.key.get_pressed()
        # If the player is hit, ignore the input
        if not player.is_hit:
            if key_pressed[K_w] or key_pressed[K_UP]:
                player.moveUp()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                player.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                player.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                player.moveRight()

    # Game over screen
    font = pygame.font.Font(None, 48)
    text = font.render('Score: ' + str(score), True, (255, 0, 0))
    text_rect = text.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.centery = screen.get_rect().centery + 65
    screen.blit(game_over, (0, 0))
    screen.blit(text, text_rect)

    # Draw Restart Button
    draw_button('Restart', 150, 450, 180, 50, (0, 200, 0), (0, 255, 0), restart_game)
    draw_button('Score Board', 150, 510, 180, 50, (0, 200, 0), (0, 255, 0), to_scoreboard)

    # Check if the scoreboard should be displayed
    if show_scoreboard:  # Check the flag
        to_scoreboard()  # Display the scoreboard

    # Check for events on game over screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    pygame.display.update()
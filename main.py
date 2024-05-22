import pygame
import random
import asyncio

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dodge")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

#Assets
spaceship_img = pygame.image.load("graphics/spaceship.png")
asteroid_img = pygame.image.load("graphics/asteroid.png")
background_img = pygame.image.load("graphics/spacebackground.jpg")
astronaut_img = pygame.image.load("graphics/astronauthi.png")
intro_bg_img = pygame.image.load("graphics/introbg.jpg")
alien_img = pygame.image.load("graphics/alien.png")
bullet_img = pygame.Surface((15, 5))
astronaut_win_img = pygame.image.load("graphics/astronautwin.png")

#Scaling image
spaceship_img = pygame.transform.scale(spaceship_img, (50, 50))
asteroid_img = pygame.transform.scale(asteroid_img, (50, 50))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
astronaut_img = pygame.transform.scale(astronaut_img, (200, 200))
astronaut_win_img = pygame.transform.scale(astronaut_win_img, (200, 200))
intro_bg_img = pygame.transform.scale(intro_bg_img, (WIDTH, HEIGHT))
alien_img = pygame.transform.scale(alien_img, (80, 80))  # Scale alien image

spaceship_x = 50
spaceship_y = HEIGHT // 2
spaceship_speed = 5

asteroids = []
asteroid_speed = 5
asteroid_timer = 0

score = 0
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# Alien
alien_x = WIDTH - 780
alien_y = HEIGHT // 2
alien_speed = 7
alien_timer = 0
alien_shoot_timer = 0
alien_shoot_cooldown = 1000  # Time between alien shots millisecs
alien_bullets = []
last_alien_shoot_time = 0

# User bullet
bullet_speed = 10
user_bullets = []

# Game states
INTRO = 0
PLAYING = 1
GAME_OVER = 2
WIN = 3
state = INTRO
start_time = 0

def draw_intro():
    screen.blit(intro_bg_img, (0, 0))
    screen.blit(astronaut_img, (WIDTH // 3 + 40, HEIGHT - 430))
    title_text = big_font.render("Space Dodge", True, WHITE)
    start_text = font.render("Press ENTER to Start", True, WHITE)
    instructions_text = font.render("You can use the arrow keys to move the spaceship in all directions.", True, WHITE)
    instructions_text2 = font.render("Press SPACE to shoot bullets.", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4 - 50))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT - 100))
    screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, HEIGHT -200))
    screen.blit(instructions_text2, (WIDTH // 2 - instructions_text2.get_width() // 2, HEIGHT -160))

def draw_game_over():
    game_over_text = big_font.render("Game Over", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))

def draw_win():
    screen.fill(BLACK)
    screen.blit(astronaut_win_img, (WIDTH // 2 - astronaut_win_img.get_width() // 2, HEIGHT // 4))
    win_text = big_font.render("You Win!", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 4 + astronaut_win_img.get_height()))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 4 + astronaut_win_img.get_height() + 50))

def draw_alien():
    screen.blit(alien_img, (alien_x, alien_y))

def move_alien():
    global alien_y, alien_speed
    # Change alien direction if it reaches top or bottom of the screen
    if alien_y <= 0 or alien_y + 50 >= HEIGHT:
        alien_speed *= -1
    alien_y += alien_speed

def alien_shoot():
    global alien_shoot_timer, last_alien_shoot_time, alien_bullets
    current_time = pygame.time.get_ticks()
    if current_time - alien_shoot_timer > alien_shoot_cooldown:
        alien_bullets.append((alien_x + 35, alien_y + 20))  # Adjust bullet position
        alien_shoot_timer = current_time

def draw_alien_bullets():
    if state != WIN:
        for bullet in alien_bullets:
            pygame.draw.rect(screen, RED, (bullet[0], bullet[1], 30, 5))

def draw_bullets():
    for bullet in user_bullets:
        pygame.draw.rect(screen, WHITE, (bullet[0], bullet[1], 30, 5))

def move_user_bullets():
    global user_bullets
    new_bullets = []
    for bullet in user_bullets:
        bullet[0] -= 4  # Decrease x-coordinate to move bullet leftward
        if bullet[0] > 0:
            new_bullets.append(bullet)
    user_bullets = new_bullets

def move_alien_bullets():
    global alien_bullets
    new_bullets = []
    for bullet in alien_bullets:
        bullet_x, bullet_y = bullet
        bullet_x += 4  # Move bullet to the right
        if bullet_x < WIDTH:
            new_bullets.append((bullet_x, bullet_y))
    alien_bullets = new_bullets


def collision_detection():
    global state
    spaceship_rect = pygame.Rect(spaceship_x, spaceship_y, 50, 50)
    for bullet in user_bullets:
        if score >= 10 and alien_x < bullet[0] < alien_x + 50 and alien_y < bullet[1] < alien_y + 50:
            state = WIN
            return
    for bullet in alien_bullets:
        if spaceship_rect.collidepoint(bullet[0], bullet[1]):
            state = GAME_OVER
            return
    for asteroid_x, asteroid_y in asteroids:
        asteroid_rect = pygame.Rect(asteroid_x, asteroid_y, 50, 50)
        if spaceship_rect.colliderect(asteroid_rect):
            state = GAME_OVER
            return

def reset_game():
    global spaceship_x, spaceship_y, asteroids, asteroid_timer, score, alien_x, alien_y, alien_timer, alien_shoot_timer
    spaceship_x = 50
    spaceship_y = HEIGHT // 2
    asteroids = []
    asteroid_timer = 0
    score = 0
    alien_x = WIDTH - 780
    alien_y = HEIGHT // 2
    alien_timer = 0
    alien_shoot_timer = 0
    user_bullets.clear()
    alien_bullets.clear()
    last_alien_shoot_time = 0
    state = INTRO

# Main game loop
async def main():
    global state, spaceship_x, spaceship_y, asteroids, asteroid_timer, start_time, score, alien_bullets
    running = True
    last_alien_shoot_time = pygame.time.get_ticks()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and state == PLAYING:
                    user_bullets.append([spaceship_x + 50, spaceship_y + 22])  # Adjust bullet position
                elif event.key == pygame.K_r:  # Restart game
                    reset_game()

        keys = pygame.key.get_pressed()

        if state == INTRO:
            if keys[pygame.K_RETURN]:
                state = PLAYING
                score = 0
                spaceship_x = 50
                spaceship_y = HEIGHT // 2
                asteroids = []
                asteroid_timer = 0
                start_time = pygame.time.get_ticks()  # Set start time here
            draw_intro()

        elif state == PLAYING:
            if keys[pygame.K_UP] and spaceship_y > 0:
                spaceship_y -= spaceship_speed
            if keys[pygame.K_DOWN] and spaceship_y < HEIGHT - 50:
                spaceship_y += spaceship_speed
            if keys[pygame.K_RIGHT] and spaceship_x < WIDTH - 50:
                spaceship_x += spaceship_speed
            if keys[pygame.K_LEFT] and spaceship_x > 0:
                spaceship_x -= spaceship_speed

            asteroid_timer += 1
            if asteroid_timer > 30:
                asteroid_x = WIDTH
                asteroid_y = random.randint(0, HEIGHT - 50)
                asteroids.append((asteroid_x, asteroid_y))
                asteroid_timer = 0

            screen.blit(background_img, (0, 0))

            for i, (asteroid_x, asteroid_y) in enumerate(asteroids):
                screen.blit(asteroid_img, (asteroid_x, asteroid_y))
                asteroids[i] = (asteroid_x - asteroid_speed, asteroid_y)
                if asteroid_x < -50:
                    asteroids.pop(i)
                    score += 1
                if spaceship_x < asteroid_x + 50 and spaceship_x + 50 > asteroid_x and spaceship_y < asteroid_y + 50 and spaceship_y + 50 > asteroid_y:
                    state = GAME_OVER

            if score >= 10:
                asteroids = []
                move_alien()
                current_time = pygame.time.get_ticks()
                if current_time - last_alien_shoot_time >= 1000:
                    alien_shoot()
                    last_alien_shoot_time = current_time
                draw_alien()

            move_alien_bullets()
            for bullet in alien_bullets:
                if bullet[0] > 850:
                    alien_bullets.remove(bullet)

            collision_detection()

            draw_bullets()
            move_user_bullets()
            for bullet in user_bullets:
                if bullet[0] < -50:
                    user_bullets.remove(bullet)

            screen.blit(spaceship_img, (spaceship_x + 50, spaceship_y))

            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

        elif state == GAME_OVER:
            if keys[pygame.K_r]:
                state = INTRO
            draw_game_over()

        elif state == WIN:
            if keys[pygame.K_r]:
                state = INTRO
            draw_win()
            if state != WIN:
                draw_alien_bullets()

        draw_alien_bullets()
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        await asyncio.sleep(0)
asyncio.run(main())


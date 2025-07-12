import pygame
import random
import sys
import os

def resource_path(relative_path):
    """ Get the absolute path to a resource, works for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Initialize
pygame.init()
pygame.mixer.init()

# Window setup
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Buster")


# Load the background image with error handling
try:
    menu_background = pygame.image.load(resource_path("menu_background.png"))
    menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))
except Exception as e:
    print(f"Error loading menu background: {e}")
    menu_background = pygame.Surface((WIDTH, HEIGHT))
    menu_background.fill((30, 30, 30))

# Colors
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (255, 50, 50)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 50)

# Fonts
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 50)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Sound files
background_music = resource_path("background_music.mp3")
shoot_sound = resource_path("shoot.mp3")
hit_sound = resource_path("hit.mp3")
game_over_sound = resource_path("game_over.mp3")
click_sound = resource_path("click.wav")
powerup_sound = resource_path("powerup.wav")
victory_music = resource_path("victory_music.mp3")
arena_music = resource_path("arena_music.mp3")

# Mixer channels
channel_fx_shoot = pygame.mixer.Channel(1)
channel_fx_hit = pygame.mixer.Channel(2)
channel_fx_ui = pygame.mixer.Channel(3)
channel_fx_powerup = pygame.mixer.Channel(4)

# Sound volumes
background_music_volume = 0.5
shoot_sound_volume = 0.5
hit_sound_volume = 0.5
click_sound_volume = 0.5
powerup_sound_volume = 0.5

# Play music
def play_background_music():
    pygame.mixer.music.set_volume(background_music_volume)
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load(background_music)
        pygame.mixer.music.play(-1)

def play_fx(mp3_file, channel, volume):
    fx = pygame.mixer.Sound(mp3_file)
    fx.set_volume(volume)
    channel.play(fx)

# Game state
game_state = "menu"
pause = False

# Add a timer for the "GET READY!" state
get_ready_start_time = 0
get_ready_duration = 2000  # 2 seconds

# Player
player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 60, 50, 50)
player_speed = 10
sprint_speed = 20
shield = False
shield_duration = 3000  # milliseconds
shield_end_time = 0

# Shield animation
shield_animation_radius = 60  # Initial radius of the shield animation
shield_animation_growth = 2   # Growth rate of the shield animation

# Sprint
energy = 100
max_energy = 100
energy_regen_rate = 0.1
energy_drain_rate = 0.5

# Dash cooldown
dash_cooldown = 2000  # Cooldown time in milliseconds (2 seconds)
last_dash_time = 0    # Tracks the last time the player dashed

# Dash animation
dash_animation_active = False
dash_animation_start_time = 0
dash_animation_duration = 200  # Duration of the dash animation in milliseconds

# Bullets
bullets = []
bullet_speed = 15  # Player bullet speed

# Shooting cooldown
shoot_cooldown = 300  # Cooldown time in milliseconds
last_shot_time = 0    # Tracks the last time a bullet was fired

# Enemies
enemies = []
enemy_spawn_time = 1000
enemy_speed = 4
last_enemy_spawn = pygame.time.get_ticks()

# Enemy spawn cooldown
enemy_spawn_cooldown = 2000  # Cooldown time in milliseconds (1 second)
enemy_spawn_resume_time = 0  # Tracks when enemy spawning can resume

# Enemy bullets
enemy_bullets = []
enemy_bullet_speed = 12  # Enemy bullet speed
enemy_shoot_cooldown = 1000  # Cooldown time in milliseconds
last_enemy_shoot_time = 0    # Tracks the last time an enemy shot

# Power-ups
powerups = []
powerup_spawn_time = 5000
last_powerup_spawn = pygame.time.get_ticks()

# Score & health
score = 0
health = 5
max_health = 5
level = 0
high_score = 0

# Splash effect
splash_active = False
splash_start_time = 0
splash_duration = 500  # Duration of the splash effect in milliseconds

# Health bar blink animation
health_blink_active = False
health_blink_start_time = 0
health_blink_duration = 1000  # Duration of the blink effect in milliseconds

# Arena mode variables
arena_enemy = pygame.Rect(WIDTH//2 - 25, 50, 50, 50)  # Enemy starts at the top center
arena_enemy_health = 5
arena_enemy_max_health = 5
arena_enemy_speed = 7
arena_enemy_dodge_cooldown = 2000  # 2 seconds
arena_enemy_last_dodge = 0

player_health = 20
player_max_health = 20
player_dodge_cooldown = 2000  # 2 seconds
player_last_dodge = 0

# Arena mode destruction effect
enemy_pieces = []  # List to store enemy pieces
enemy_destroyed = False  # Flag to track if the enemy is destroyed
enemy_destroy_start_time = 0  # Timer for the destruction effect
enemy_destroy_duration = 2000  # Duration of the destruction effect in milliseconds

# Survival mode destruction effect
survival_enemy_pieces = []  # List to store enemy pieces
survival_enemy_destroyed = False  # Flag to track if an enemy is destroyed
survival_enemy_destroy_start_time = 0  # Timer for the destruction effect
survival_enemy_destroy_duration = 2000  # Duration of the destruction effect in milliseconds

global victory_music_playing
victory_music_playing = False  # Flag to track if victory music is playing


# Centralized button definitions
BUTTONS = {
    "start": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 100, 200, 50),
    "settings": pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 50),
    "exit": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50),
    "try_again": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 40, 200, 50),
    "menu_pause": pygame.Rect(WIDTH//2 - 55, HEIGHT//2 + 20, 110, 50),
    "survival": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 50),
    "arena": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50),
    "back": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50),
    "menu_settings": pygame.Rect(WIDTH//2 - 55, HEIGHT - 100, 110, 50),
    "menu_game_over": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50),
    "menu_victory": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50),
}

def draw_button(text, rect, color, alpha=150):
    button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    button_surface.fill((*color, alpha))
    WIN.blit(button_surface, (rect.x, rect.y))
    label = font.render(text, True, WHITE)
    WIN.blit(label, (rect.x + rect.width//2 - label.get_width()//2, rect.y + rect.height//2 - label.get_height()//2))

# Sliders
slider_width = 200
slider_height = 10
slider_x = WIDTH // 2 - slider_width // 2
slider_y_music = HEIGHT // 2 - 100
slider_y_shoot = HEIGHT // 2
slider_y_hit = HEIGHT // 2 + 100

slider_music_rect = pygame.Rect(slider_x, slider_y_music, slider_width, slider_height)
slider_shoot_rect = pygame.Rect(slider_x, slider_y_shoot, slider_width, slider_height)
slider_hit_rect = pygame.Rect(slider_x, slider_y_hit, slider_width, slider_height)

# Slider logic
def draw_slider(rect, volume):
    pygame.draw.rect(WIN, WHITE, rect)
    pygame.draw.rect(WIN, GREEN, (rect.x, rect.y, volume * rect.width, rect.height))

def handle_slider_movement(rect, volume, mouse_x):
    if rect.collidepoint(mouse_x, pygame.mouse.get_pos()[1]):
        new_volume = (mouse_x - rect.x) / rect.width
        return max(0, min(new_volume, 1))
    return volume

# Reset game
def reset_game():
    global player, bullets, enemies, score, health, enemy_speed, energy, level, enemy_spawn_time, high_score
    global powerups, shield, shield_end_time, last_shot_time, last_dash_time, enemy_bullets, last_enemy_shoot_time
    global arena_enemy_health, player_health, enemy_pieces, enemy_destroyed, enemy_destroy_start_time
    global survival_enemy_pieces, survival_enemy_destroyed, survival_enemy_destroy_start_time
    global shield_animation_radius, shield_animation_growth, victory_music_playing
    global enemy_target_x, enemy_target_y

    player.x = WIDTH//2 - 25
    player.y = HEIGHT - 60
    bullets = []
    enemies = []
    enemy_bullets = []
    powerups = []
    score = 0
    health = max_health
    enemy_speed = 4
    energy = max_energy
    level = 1
    enemy_spawn_time = 1000
    shield = False
    shield_end_time = 0
    last_shot_time = 0
    last_dash_time = 0
    last_enemy_shoot_time = 0
    arena_enemy_health = arena_enemy_max_health
    player_health = player_max_health
    enemy_pieces = []
    enemy_destroyed = False
    enemy_destroy_start_time = 0
    survival_enemy_pieces = []
    survival_enemy_destroyed = False
    survival_enemy_destroy_start_time = 0
    shield_animation_radius = 60
    shield_animation_growth = 2
    victory_music_playing = False
    enemy_target_x = WIDTH // 2
    enemy_target_y = 50

# Enemy AI – Move towards the player
def move_enemy(enemy):
    if enemy.centerx < player.centerx:
        enemy.x += 1
    elif enemy.centerx > player.centerx:
        enemy.x -= 1
    enemy.y += enemy_speed

# Power-up spawn logic
def spawn_powerup():
    powerup_type = random.choice(["health", "shield", "clear_enemies"])  # Added new types
    powerup = {"type": powerup_type, "rect": pygame.Rect(random.randint(0, WIDTH-50), -50, 50, 50)}
    powerups.append(powerup)

def create_survival_enemy_pieces(enemy_rect, piece_size=10):
    pieces = []
    for i in range(enemy_rect.width // piece_size):
        for j in range(enemy_rect.height // piece_size):
            piece_rect = pygame.Rect(
                enemy_rect.x + i * piece_size,
                enemy_rect.y + j * piece_size,
                piece_size,
                piece_size
            )
            piece_velocity = [random.randint(-5, 5), random.randint(-5, 5)]  # Random velocity
            pieces.append({"rect": piece_rect, "velocity": piece_velocity})
    return pieces

# Game loop
running = True
dragging_slider = None
play_background_music()

print(f"Music busy: {pygame.mixer.music.get_busy()}")  # Check if music is playing
print(f"Music volume: {pygame.mixer.music.get_volume()}")  # Check the current volume

while running:
    clock.tick(FPS)
    WIN.fill(BLACK)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Toggle pause for "play" and "arena" game states
                if game_state in ["play", "arena"]:
                    pause = not pause

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if game_state == "menu":
                if not pause:  # Handle main menu buttons
                    if BUTTONS["start"].collidepoint(mx, my):
                        play_fx(click_sound, channel_fx_ui, click_sound_volume)
                        pause = True  # Show game mode selection
                    elif BUTTONS["settings"].collidepoint(mx, my):
                        play_fx(click_sound, channel_fx_ui, click_sound_volume)
                        game_state = "settings"
                    elif BUTTONS["exit"].collidepoint(mx, my):
                        play_fx(click_sound, channel_fx_ui, click_sound_volume)
                        pygame.quit()
                        sys.exit()
                else:  # Handle game mode selection buttons
                    if BUTTONS["survival"].collidepoint(mx, my):
                        play_fx(click_sound, channel_fx_ui, click_sound_volume)
                        reset_game()
                        get_ready_start_time = pygame.time.get_ticks()  # Start the "GET READY!" timer
                        game_state = "get_ready_survival"  # Temporary state for Survival mode
                    elif BUTTONS["arena"].collidepoint(mx, my):
                        play_fx(click_sound, channel_fx_ui, click_sound_volume)
                        reset_game()  # Reset all variables
                        get_ready_start_time = pygame.time.get_ticks()  # Start the "GET READY!" timer
                        game_state = "get_ready_arena"  # Temporary state for Arena mode
                        pause = False  # Ensure the game is not paused
                        print("Clicked on Arena button. Transitioning to 'get_ready_arena' state.")  # Debugging output
                    elif BUTTONS["back"].collidepoint(mx, my):  # Handle "Back" button click
                        play_fx(click_sound, channel_fx_ui, click_sound_volume)
                        pause = False  # Return to the main menu

            elif game_state == "game_over":
                if BUTTONS["try_again"].collidepoint(mx, my):
                    play_fx(click_sound, channel_fx_ui, click_sound_volume)
                    reset_game()
                    play_background_music()  # Restart background music
                    pause = False  # Reset pause state
                    game_state = "play"
                elif BUTTONS["menu_game_over"].collidepoint(mx, my):
                    play_fx(click_sound, channel_fx_ui, click_sound_volume)
                    reset_game()
                    play_background_music()  # Restart background music
                    pause = False  # Reset pause state
                    game_state = "menu"

            if pause:  # Handle "MENU" button in pause menu
                if BUTTONS["menu_pause"].collidepoint(mx, my):
                    play_fx(click_sound, channel_fx_ui, click_sound_volume)
                    reset_game()
                    pause = False  # Reset pause state
                    game_state = "menu"

    # Handle the "GET READY!" state
    if game_state == "get_ready_survival":
        # Display the "GET READY!" text
        get_ready_text = big_font.render("GET READY!", True, WHITE)
        WIN.blit(get_ready_text, (WIDTH//2 - get_ready_text.get_width()//2, HEIGHT//2 - get_ready_text.get_height()//2))

        # Transition to Survival mode after the delay
        if current_time - get_ready_start_time > get_ready_duration:
            game_state = "play"  # Transition to Survival mode
            pause = False  # Ensure the game starts unpaused

    elif game_state == "get_ready_arena":
        # Display the "GET READY!" text
        get_ready_text = big_font.render("GET READY!", True, WHITE)
        WIN.blit(get_ready_text, (WIDTH//2 - get_ready_text.get_width()//2, HEIGHT//2 - get_ready_text.get_height()//2))

        # Transition to Arena mode after the delay
        if current_time - get_ready_start_time > get_ready_duration:
            print("Transitioning to 'arena' state...")  # Debugging output
            game_state = "arena"  # Transition to Arena mode
            pause = False  # Ensure the game starts unpaused

            # Stop any currently playing music
            pygame.mixer.music.stop()

            # Play arena music
            pygame.mixer.music.load(arena_music)
            pygame.mixer.music.set_volume(background_music_volume)  # Use the same volume setting
            pygame.mixer.music.play(-1)  # Loop the arena music

            # Initialize enemy target position to avoid errors
            enemy_target_x = random.randint(0, WIDTH - arena_enemy.width)
            enemy_target_y = random.randint(0, HEIGHT // 2 - arena_enemy.height)

            # Reset player and enemy positions
            player.x = WIDTH // 2 - player.width // 2
            player.y = HEIGHT - player.height - 10
            arena_enemy.x = WIDTH // 2 - arena_enemy.width // 2
            arena_enemy.y = 50

    elif game_state == "menu":
        # Draw the background
        WIN.blit(menu_background, (0, 0))

        # Draw the title
        title = big_font.render(" ", True, WHITE)
        WIN.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        if not pause:  # Show the main menu buttons
            draw_button("START", BUTTONS["start"], BLUE, alpha=150)
            draw_button("SETTINGS", BUTTONS["settings"], BLUE, alpha=150)
            draw_button("EXIT", BUTTONS["exit"], RED, alpha=150)
        else:  # Show the game mode selection buttons
            draw_button("SURVIVAL", BUTTONS["survival"], BLUE, alpha=150)
            draw_button("ARENA", BUTTONS["arena"], BLUE, alpha=150)
            draw_button("BACK", BUTTONS["back"], RED, alpha=150)

    elif game_state == "play":
        if not pause:
            keys = pygame.key.get_pressed()

            # Handle dash input with cooldown
            current_time = pygame.time.get_ticks()
            if keys[pygame.K_LSHIFT] and current_time - last_dash_time >= dash_cooldown:
                last_dash_time = current_time  # Update the last dash time
                dash_animation_active = True  # Activate the dash animation
                dash_animation_start_time = pygame.time.get_ticks()  # Record the start time
                player.x += sprint_speed * 10 if keys[pygame.K_d] and player.right < WIDTH else 0
                player.x -= sprint_speed * 10 if keys[pygame.K_a] and player.left > 0 else 0

            # Restrict movement to left and right only
            if keys[pygame.K_a] and player.left > 0:
                player.x -= player_speed
            if keys[pygame.K_d] and player.right < WIDTH:
                player.x += player_speed

            # Ensure the player's y-position remains constant
            player.y = HEIGHT - 60

            # Handle shooting with cooldown
            if keys[pygame.K_SPACE]:
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time >= shoot_cooldown:  # Check if cooldown has elapsed
                    bullet = pygame.Rect(player.centerx - 5, player.y, 10, 20)
                    bullets.append(bullet)
                    play_fx(shoot_sound, channel_fx_shoot, shoot_sound_volume)
                    last_shot_time = current_time  # Update the last shot time

            # Remove off-screen bullets
            for bullet in bullets[:]:
                bullet.y -= bullet_speed
                if bullet.bottom < 0:
                    bullets.remove(bullet)

            # Limit the number of bullets
            if len(bullets) > 50:
                bullets = bullets[-50:]

            if current_time >= enemy_spawn_resume_time:  # Check if cooldown has elapsed
                if current_time - last_enemy_spawn > enemy_spawn_time:
                    for _ in range(1 + (level // 5)):
                        enemy = pygame.Rect(random.randint(0, WIDTH-50), -50, 50, 50)
                        enemies.append(enemy)
                    last_enemy_spawn = current_time

            # Enemy shooting logic
            if current_time - last_enemy_shoot_time > enemy_shoot_cooldown:
                for enemy in enemies:
                    if random.random() < 0.3:  # 30% chance for an enemy to shoot
                        bullet = pygame.Rect(enemy.centerx - 5, enemy.bottom, 10, 20)
                        enemy_bullets.append(bullet)
                last_enemy_shoot_time = current_time

            if game_state == "play" and not pause:
                # Move enemy bullets
                for bullet in enemy_bullets[:]:
                    bullet.y += enemy_bullet_speed
                    if bullet.top > HEIGHT:  # Remove bullets that go off-screen
                        enemy_bullets.remove(bullet)
                    elif bullet.colliderect(player):  # Check collision with the player
                        if not shield:  # If the shield is not active, reduce health
                            health -= 1
                        enemy_bullets.remove(bullet)
                        if health <= 0:
                            pygame.mixer.music.stop()
                            play_fx(game_over_sound, channel_fx_hit, hit_sound_volume)
                            game_state = "game_over"

                # Update enemies
                for enemy in enemies[:]:
                    move_enemy(enemy)
                    if enemy.colliderect(player):
                        if not shield:
                            health -= 1
                            enemies.remove(enemy)
                        if health <= 0:
                            pygame.mixer.music.stop()
                            play_fx(game_over_sound, channel_fx_hit, hit_sound_volume)
                            game_state = "game_over"
                            break

                    for bullet in bullets[:]:
                        if enemy.colliderect(bullet):
                            bullets.remove(bullet)
                            enemies.remove(enemy)
                            score += 1
                            play_fx(hit_sound, channel_fx_hit, hit_sound_volume)

                            # Trigger destruction animation
                            survival_enemy_destroyed = True
                            survival_enemy_destroy_start_time = pygame.time.get_ticks()
                            survival_enemy_pieces = create_survival_enemy_pieces(enemy)
                            break

                # Animate enemy pieces
                if survival_enemy_destroyed:
                    elapsed_time = pygame.time.get_ticks() - survival_enemy_destroy_start_time
                    if elapsed_time < survival_enemy_destroy_duration:
                        for piece in survival_enemy_pieces:
                            piece["rect"].x += piece["velocity"][0]
                            piece["rect"].y += piece["velocity"][1]
                            pygame.draw.rect(WIN, RED, piece["rect"])  # Draw each piece
                    else:
                        survival_enemy_destroyed = False  # Reset the destruction state
                        survival_enemy_pieces = []  # Clear the pieces

                # Deactivate shield after 5 seconds
                if shield and pygame.time.get_ticks() > shield_end_time:
                    shield = False

                # Animate the shield
                if shield:
                    shield_animation_radius += shield_animation_growth
                    if shield_animation_radius > 80 or shield_animation_radius < 60:  # Bounce between 60 and 80
                        shield_animation_growth *= -1  # Reverse the growth direction

                # Draw the shield animation
                if shield:
                    pygame.draw.circle(WIN, BLUE, player.center, shield_animation_radius, 2)  # Draw a glowing circle

            # Draw enemy bullets
            for bullet in enemy_bullets:
                pygame.draw.rect(WIN, RED, bullet)

            # Update enemies
            for enemy in enemies[:]:
                move_enemy(enemy)
                if enemy.colliderect(player):
                    if not shield:
                        health -= 1
                        enemies.remove(enemy)
                    if health <= 0:
                        pygame.mixer.music.stop()
                        play_fx(game_over_sound, channel_fx_hit, hit_sound_volume)
                        game_state = "game_over"
                        break

                for bullet in bullets[:]:
                    if enemy.colliderect(bullet):
                        bullets.remove(bullet)
                        enemies.remove(enemy)
                        score += 1
                        play_fx(hit_sound, channel_fx_hit, hit_sound_volume)
                        break

            # Limit the number of enemies
            if len(enemies) > 20:
                enemies = enemies[-20:]

            if game_state == "play" and not pause:
                # Spawn power-ups
                if current_time - last_powerup_spawn > powerup_spawn_time:
                    spawn_powerup()
                    last_powerup_spawn = current_time

                # Update power-ups
                for powerup in powerups[:]:
                    powerup["rect"].y += 5
                    if powerup["rect"].top > HEIGHT:
                        powerups.remove(powerup)
                    elif powerup["rect"].colliderect(player):
                        play_fx(powerup_sound, channel_fx_powerup, powerup_sound_volume)

                        if powerup["type"] == "health":
                            health = min(max_health, health + 1)  # Restore health
                            health_blink_active = True  # Activate the blink effect
                            health_blink_start_time = pygame.time.get_ticks()  # Record the start time
                        elif powerup["type"] == "shield":
                            shield = True  # Activate shield
                            shield_end_time = pygame.time.get_ticks() + 5000  # Shield lasts for 5 seconds
                        elif powerup["type"] == "clear_enemies":
                            enemies.clear()  # Clear all enemies from the screen
                            enemy_bullets.clear()  # Clear all enemy bullets from the screen
                            splash_active = True  # Activate the splash effect
                            splash_start_time = pygame.time.get_ticks()  # Record the start time
                            enemy_spawn_resume_time = pygame.time.get_ticks() + enemy_spawn_cooldown  # Set the cooldown timer

                        powerups.remove(powerup)  # Remove the power-up after collection

                # Draw the splash effect
                if splash_active:
                    elapsed_time = pygame.time.get_ticks() - splash_start_time
                    if elapsed_time < splash_duration:
                        # Draw a semi-transparent yellow overlay
                        splash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        splash_surface.fill((255, 255, 0, 128))  # Yellow with 50% transparency
                        WIN.blit(splash_surface, (0, 0))
                    else:
                        splash_active = False  # Deactivate the splash effect after the duration

                # Deactivate shield after 5 seconds
                if shield and pygame.time.get_ticks() > shield_end_time:
                    shield = False

                # Animate the shield
                if shield:
                    shield_animation_radius += shield_animation_growth
                    if shield_animation_radius > 80 or shield_animation_radius < 60:  # Bounce between 60 and 80
                        shield_animation_growth *= -1  # Reverse the growth direction

                # Draw power-ups
                for powerup in powerups:
                    if powerup["type"] == "health":
                        pygame.draw.rect(WIN, GREEN, powerup["rect"])  # Health power-up
                    elif powerup["type"] == "shield":
                        pygame.draw.rect(WIN, BLUE, powerup["rect"])  # Shield power-up
                    elif powerup["type"] == "clear_enemies":
                        pygame.draw.rect(WIN, YELLOW, powerup["rect"])  # Clear enemies power-up

            new_level = score // 10 + 1
            if new_level > level:
                level = new_level
                enemy_speed += 0.5
                enemy_spawn_time = max(300, enemy_spawn_time - 50)

            if score > high_score:
                high_score = score

        pygame.draw.rect(WIN, BLUE, player)

        # Draw the shield animation
        if shield:
            pygame.draw.circle(WIN, BLUE, player.center, shield_animation_radius, 2)  # Draw a glowing circle

        # Draw dash animation
        if dash_animation_active:
            elapsed_time = pygame.time.get_ticks() - dash_animation_start_time
            if elapsed_time < dash_animation_duration:
                # Draw a glowing outline around the player
                pygame.draw.rect(WIN, YELLOW, player.inflate(10, 10), 3)  # Slightly larger rectangle
            else:
                dash_animation_active = False  # Deactivate the dash animation

        # Draw health bar with blink animation
        pygame.draw.rect(WIN, WHITE, (WIDTH//2 - 100, 10, 200, 20))  # Background of health bar
        if health_blink_active:
            elapsed_time = pygame.time.get_ticks() - health_blink_start_time
            if elapsed_time < health_blink_duration:
                # Alternate visibility every 100 milliseconds
                if (elapsed_time // 100) % 2 == 0:
                    pygame.draw.rect(WIN, RED, (WIDTH//2 - 100, 10, (health / max_health) * 200, 20))
            else:
                health_blink_active = False  # Deactivate the blink effect
                pygame.draw.rect(WIN, RED, (WIDTH//2 - 100, 10, (health / max_health) * 200, 20))
        else:
            pygame.draw.rect(WIN, RED, (WIDTH//2 - 100, 10, (health / max_health) * 200, 20))

        # Draw score and level
        WIN.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        WIN.blit(font.render(f"Level: {level}", True, WHITE), (WIDTH - 150, 10))
        WIN.blit(font.render(f"High Score: {high_score}", True, WHITE), (10, 40))

        for bullet in bullets:
            pygame.draw.rect(WIN, BLUE, bullet)

        for enemy in enemies:
            pygame.draw.rect(WIN, RED, enemy)

        for powerup in powerups:
            if powerup["type"] == "health":
                pygame.draw.rect(WIN, GREEN, powerup["rect"])  # Health power-up
            elif powerup["type"] == "shield":
                pygame.draw.rect(WIN, BLUE, powerup["rect"])  # Shield power-up
            elif powerup["type"] == "clear_enemies":
                pygame.draw.rect(WIN, YELLOW, powerup["rect"])  # Clear enemies power-up

        if pause:
            pause_text = big_font.render("PAUSED", True, WHITE)
            WIN.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
            
            # Add a "MENU" button below the pause text
            draw_button("MENU", BUTTONS["menu_pause"], BLUE)

    elif game_state == "arena":
        # Draw the player
        pygame.draw.rect(WIN, BLUE, player)

        # Draw the enemy or handle its destruction
        if not enemy_destroyed:
            pygame.draw.rect(WIN, RED, arena_enemy)  # Draw the enemy if not destroyed
        else:
            # Animate enemy pieces
            for piece in enemy_pieces:
                piece["rect"].x += piece["velocity"][0]
                piece["rect"].y += piece["velocity"][1]
                pygame.draw.rect(WIN, RED, piece["rect"])  # Draw each piece

            # Check if the destruction effect duration has elapsed
            elapsed_time = pygame.time.get_ticks() - enemy_destroy_start_time
            print(f"Destruction animation running... Elapsed time: {elapsed_time} ms")  # Debugging output
            if elapsed_time > enemy_destroy_duration:
                pygame.mixer.music.stop()  # Stop the arena music
                game_state = "victory"  # Transition to victory state
                print("Transitioning to 'victory' state...")  # Debugging output

        # Draw health bars with labels
        pygame.draw.rect(WIN, WHITE, (50, 10, 200, 20))  # Player health bar background
        pygame.draw.rect(WIN, GREEN, (50, 10, (player_health / player_max_health) * 200, 20))  # Player health
        player_label = font.render("Player", True, WHITE)
        WIN.blit(player_label, (50, 35))  # Label above the player health bar

        pygame.draw.rect(WIN, WHITE, (WIDTH - 250, 10, 200, 20))  # Enemy health bar background
        pygame.draw.rect(WIN, GREEN, (WIDTH - 250, 10, (arena_enemy_health / arena_enemy_max_health) * 200, 20))  # Enemy health
        enemy_label = font.render("Enemy", True, WHITE)
        WIN.blit(enemy_label, (WIDTH - 250, 35))  # Label above the enemy health bar

        if not pause:
            # Player controls (restricted to bottom half of the screen)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and player.left > 0:
                player.x -= player_speed
            if keys[pygame.K_d] and player.right < WIDTH:
                player.x += player_speed
            if keys[pygame.K_w] and player.top > HEIGHT // 2:
                player.y -= player_speed
            if keys[pygame.K_s] and player.bottom < HEIGHT:
                player.y += player_speed
            if keys[pygame.K_LSHIFT] and pygame.time.get_ticks() - player_last_dodge >= player_dodge_cooldown:
                player_last_dodge = pygame.time.get_ticks()
                player.x += sprint_speed * 10 if keys[pygame.K_d] and player.right < WIDTH else 0
                player.x -= sprint_speed * 10 if keys[pygame.K_a] and player.left > 0 else 0

            # Shooting logic
            if keys[pygame.K_SPACE]:
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time >= shoot_cooldown:
                    bullet = pygame.Rect(player.centerx - 5, player.y, 10, 20)
                    bullets.append(bullet)
                    play_fx(shoot_sound, channel_fx_shoot, shoot_sound_volume)
                    last_shot_time = current_time

            # Move bullets
            for bullet in bullets[:]:
                bullet.y -= bullet_speed
                if bullet.bottom < 0:
                    bullets.remove(bullet)
                elif bullet.colliderect(arena_enemy):
                    bullets.remove(bullet)
                    arena_enemy_health -= 1
                    play_fx(hit_sound, channel_fx_hit, hit_sound_volume)


            # Improved Arena Enemy AI
            # 1. Smarter movement: track player, randomize target, and sometimes dash toward player
            ai_retarget = False
            if abs(arena_enemy.centerx - enemy_target_x) < 5 and abs(arena_enemy.centery - enemy_target_y) < 5:
                ai_retarget = True
            # Occasionally retarget even if not reached
            if random.random() < 0.01:
                ai_retarget = True
            if ai_retarget:
                # 70% chance to target player, 30% random
                if random.random() < 0.7:
                    enemy_target_x = player.centerx + random.randint(-30, 30)
                    enemy_target_y = player.centery - random.randint(30, 80)
                    enemy_target_y = max(0, min(enemy_target_y, HEIGHT // 2 - arena_enemy.height))
                else:
                    enemy_target_x = random.randint(0, WIDTH - arena_enemy.width)
                    enemy_target_y = random.randint(0, HEIGHT // 2 - arena_enemy.height)

            # Move enemy toward the target position, with some jitter
            move_x = enemy_target_x - arena_enemy.centerx
            move_y = enemy_target_y - arena_enemy.centery
            if abs(move_x) > 2:
                arena_enemy.x += int(arena_enemy_speed * (1 if move_x > 0 else -1))
            if abs(move_y) > 2:
                arena_enemy.y += int(arena_enemy_speed * (1 if move_y > 0 else -1))
            # Add jitter for unpredictability
            if random.random() < 0.05:
                arena_enemy.x += random.choice([-1, 1]) * random.randint(0, 2)
                arena_enemy.y += random.choice([-1, 1]) * random.randint(0, 2)
            # Clamp enemy position
            arena_enemy.x = max(0, min(arena_enemy.x, WIDTH - arena_enemy.width))
            arena_enemy.y = max(0, min(arena_enemy.y, HEIGHT // 2 - arena_enemy.height))

            # 2. Smarter dodging: dodge only if bullet is on a collision course and close
            for bullet in bullets:
                if bullet.y < arena_enemy.bottom and bullet.y > arena_enemy.top - 100:
                    if abs(bullet.centerx - arena_enemy.centerx) < 40:
                        # 70% chance to dodge, prefer direction with more space
                        if random.random() < 0.7:
                            if arena_enemy.centerx < WIDTH // 2:
                                arena_enemy.x += arena_enemy_speed * 6
                            else:
                                arena_enemy.x -= arena_enemy_speed * 6
                        else:
                            # Random dodge
                            arena_enemy.x += random.choice([-1, 1]) * arena_enemy_speed * 6
                        # Clamp after dodge
                        arena_enemy.x = max(0, min(arena_enemy.x, WIDTH - arena_enemy.width))

            # 3. Aggressive dash: sometimes dash toward player if far away
            if random.random() < 0.01 and abs(arena_enemy.centerx - player.centerx) > 100:
                dash_dir = 1 if player.centerx > arena_enemy.centerx else -1
                arena_enemy.x += dash_dir * arena_enemy_speed * 10
                arena_enemy.x = max(0, min(arena_enemy.x, WIDTH - arena_enemy.width))

            # 4. Predictive shooting: aim at player's future position with more accuracy
            # (handled below in the shooting logic)

            # Predictive shooting logic and bullet movement only if enemy is not destroyed
            current_time = pygame.time.get_ticks()
            if not enemy_destroyed:
                if current_time - last_enemy_shoot_time > enemy_shoot_cooldown:
                    # Predict the player's future position
                    player_future_x = player.centerx + (player_speed if keys[pygame.K_d] else -player_speed if keys[pygame.K_a] else 0)
                    player_future_y = player.centery + (player_speed if keys[pygame.K_s] else -player_speed if keys[pygame.K_w] else 0)

                    # Create a bullet aimed at the predicted position
                    bullet_dx = player_future_x - arena_enemy.centerx
                    bullet_dy = player_future_y - arena_enemy.centery
                    bullet_distance = max(1, (bullet_dx**2 + bullet_dy**2)**0.5)  # Avoid division by zero
                    bullet_velocity_x = (bullet_dx / bullet_distance) * enemy_bullet_speed
                    bullet_velocity_y = (bullet_dy / bullet_distance) * enemy_bullet_speed

                    # Add the bullet with velocity
                    enemy_bullets.append({"rect": pygame.Rect(arena_enemy.centerx - 5, arena_enemy.bottom, 10, 20),
                                          "velocity": (bullet_velocity_x, bullet_velocity_y)})

                    last_enemy_shoot_time = current_time

                # Move enemy bullets
                for bullet in enemy_bullets[:]:
                    bullet["rect"].x += bullet["velocity"][0]
                    bullet["rect"].y += bullet["velocity"][1]
                    if bullet["rect"].top > HEIGHT or bullet["rect"].bottom < 0 or bullet["rect"].left > WIDTH or bullet["rect"].right < 0:
                        enemy_bullets.remove(bullet)  # Remove bullets that go off-screen
                    elif bullet["rect"].colliderect(player):
                        enemy_bullets.remove(bullet)
                        player_health -= 1
                        play_fx(hit_sound, channel_fx_hit, hit_sound_volume)
            else:
                # If enemy is destroyed, clear all enemy bullets
                enemy_bullets.clear()

            # Check for game over or victory
            if arena_enemy_health <= 0 and not enemy_destroyed:
                print("Enemy health is 0. Triggering destruction effect.")  # Debugging output

            if enemy_destroyed:
                print(f"Animating {len(enemy_pieces)} enemy pieces...")  # Debugging output

            if arena_enemy_health <= 0 and not enemy_destroyed:
                print("Enemy health is 0. Triggering destruction effect.")  # Debugging output
                enemy_destroyed = True
                enemy_destroy_start_time = pygame.time.get_ticks()  # Start the destruction timer

                # Create enemy pieces
                piece_size = 10  # Size of each piece
                for i in range(arena_enemy.width // piece_size):
                    for j in range(arena_enemy.height // piece_size):
                        piece_rect = pygame.Rect(
                            arena_enemy.x + i * piece_size,
                            arena_enemy.y + j * piece_size,
                            piece_size,
                            piece_size
                        )
                        piece_velocity = [random.randint(-5, 5), random.randint(-5, 5)]  # Random velocity
                        enemy_pieces.append({"rect": piece_rect, "velocity": piece_velocity})

                print(f"Created {len(enemy_pieces)} enemy pieces for destruction animation.")  # Debugging output

            elif player_health <= 0:
                pygame.mixer.music.stop()  # Stop the arena music
                play_fx(game_over_sound, channel_fx_hit, hit_sound_volume)
                game_state = "game_over"

            # Draw bullets
            for bullet in bullets:
                pygame.draw.rect(WIN, BLUE, bullet)
            for bullet in enemy_bullets:
                pygame.draw.rect(WIN, RED, bullet["rect"])

        else:  # Pause menu
            pause_text = big_font.render("PAUSED", True, WHITE)
            WIN.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
            
            # Add a "MENU" button below the pause text
            draw_button("MENU", BUTTONS["menu_pause"], BLUE)

            # Handle "MENU" button click
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if BUTTONS["menu_pause"].collidepoint(mx, my):
                    play_fx(click_sound, channel_fx_ui, click_sound_volume)
                    reset_game()
                    pause = False  # Reset pause state
                    game_state = "menu"

    elif game_state == "victory":

        # Ensure the global declaration is before any assignment
        # Play victory music only once
        if not victory_music_playing:
            print("Loading and playing victory music...")  # Debugging output
            pygame.mixer.music.stop()  # Ensure no other music is playing
            try:
                pygame.mixer.music.load(victory_music)
                pygame.mixer.music.set_volume(background_music_volume)  # Use the same volume setting
                pygame.mixer.music.play(-1)  # Loop the victory music
                victory_music_playing = True  # Set the flag to prevent repeated playback
                print("Victory music is now playing.")  # Debugging output
            except pygame.error as e:
                print(f"Error loading victory music: {e}")  # Debugging output

        # Display "Victory" text
        victory_text = big_font.render("VICTORY!", True, GREEN)
        WIN.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, HEIGHT//2 - 50))

        # Add a "Menu" button
        draw_button("MENU", BUTTONS["menu_victory"], BLUE)

        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if BUTTONS["menu_victory"].collidepoint(mx, my):
                play_fx(click_sound, channel_fx_ui, click_sound_volume)
                reset_game()  # Reset all variables
                pygame.mixer.music.stop()  # Stop victory music
                play_background_music()  # Restart background music
                victory_music_playing = False  # Reset the flag
                game_state = "menu"  # Return to the main menu

    elif game_state == "settings":
        title = big_font.render("Settings", True, WHITE)
        WIN.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        # Add labels for each slider
        music_label = font.render("Music Volume", True, WHITE)
        shoot_label = font.render("Shoot Volume", True, WHITE)
        hit_label = font.render("Hit Volume", True, WHITE)

        # Position the labels above the sliders
        WIN.blit(music_label, (slider_music_rect.x, slider_music_rect.y - 30))
        WIN.blit(shoot_label, (slider_shoot_rect.x, slider_shoot_rect.y - 30))
        WIN.blit(hit_label, (slider_hit_rect.x, slider_hit_rect.y - 30))

        # Draw the sliders
        draw_slider(slider_music_rect, background_music_volume)
        draw_slider(slider_shoot_rect, shoot_sound_volume)
        draw_slider(slider_hit_rect, hit_sound_volume)

        # Draw the menu button
        draw_button("MENU", BUTTONS["menu_settings"], BLUE)

        # Handle slider interaction
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if slider_music_rect.collidepoint(mx, my):
                dragging_slider = "music"
            elif slider_shoot_rect.collidepoint(mx, my):
                dragging_slider = "shoot"
            elif slider_hit_rect.collidepoint(mx, my):
                dragging_slider = "hit"
            elif BUTTONS["menu_settings"].collidepoint(mx, my):  # Handle "MENU" button click
                play_fx(click_sound, channel_fx_ui, click_sound_volume)
                game_state = "menu"

        if event.type == pygame.MOUSEBUTTONUP:
            dragging_slider = None

        if event.type == pygame.MOUSEMOTION and dragging_slider:
            mx, _ = pygame.mouse.get_pos()
            if dragging_slider == "music":
                background_music_volume = handle_slider_movement(slider_music_rect, background_music_volume, mx)
                pygame.mixer.music.set_volume(background_music_volume)
            elif dragging_slider == "shoot":
                shoot_sound_volume = handle_slider_movement(slider_shoot_rect, shoot_sound_volume, mx)
            elif dragging_slider == "hit":
                hit_sound_volume = handle_slider_movement(slider_hit_rect, hit_sound_volume, mx)

    elif game_state == "game_over":
        # Display "GAME OVER" text
        game_over_text = big_font.render("GAME OVER", True, WHITE)
        WIN.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, 100))
        
        # Display the score reached
        score_text = font.render(f"Score: {score}", True, WHITE)
        WIN.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 180))
        
        # Place the "TRY AGAIN" button
        try_again_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 40, 200, 50)  # Adjusted size and position
        draw_button("TRY AGAIN", try_again_button, BLUE)
        
        # Place the "MENU" button below the "TRY AGAIN" button
        menu_button_game_over = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50)  # Adjusted position
        draw_button("MENU", menu_button_game_over, BLUE)

        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if try_again_button.collidepoint(mx, my):
                play_fx(click_sound, channel_fx_ui, click_sound_volume)
                reset_game()
                play_background_music()  # Restart background music
                pause = False  # Reset pause state
                game_state = "play"
            elif menu_button_game_over.collidepoint(mx, my):
                play_fx(click_sound, channel_fx_ui, click_sound_volume)
                reset_game()
                play_background_music()  # Restart background music
                pause = False  # Reset pause state
                game_state = "menu"

    pygame.display.update()

pygame.mixer.quit()
pygame.quit()
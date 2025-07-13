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
background_music_volume = 0.1
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

# Player (with float position for smooth movement)
player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 60, 50, 50)
player_pos_x = float(player.x)
player_pos_y = float(player.y)
player_speed = 25
sprint_speed = 35
shield = False
shield_duration = 3000  # milliseconds
shield_end_time = 0

# Shield animation
shield_animation_radius = 60  # Initial radius of the shield animation
shield_animation_growth = 2   # Growth rate of the shield animation

# Sprint
energy = 100
max_energy = 100
energy_drain_rate = 3.0  # Much faster drain for sprint
energy_cooldown = 5000   # 5 seconds cooldown before instant refill
energy_depleted_time = 0

# Dash cooldown
dash_cooldown = 1200  # Reduced cooldown for more frequent dashing
last_dash_time = 0    # Tracks the last time the player dashed

import math
# Dash animation (improved: smooth interpolation)
dash_animation_active = False
dash_animation_start_time = 0
dash_animation_duration = 100  # Much shorter for a snappy dash
dash_animation_max_outline = 30  # Max outline thickness
dash_animation_min_outline = 3   # Min outline thickness
dash_animation_max_alpha = 180   # Max alpha for the outline

# Bullets
bullets = []
bullet_speed = 15  # Player bullet speed

# Shooting cooldown
shoot_cooldown = 300  # Cooldown time in milliseconds
last_shot_time = 0    # Tracks the last time a bullet was fired


# Enemies
enemies = []
enemy_spawn_time = 1000
enemy_speed = 2  # Start slower at level 1
last_enemy_spawn = pygame.time.get_ticks()

# Boss variables
boss_active = False
boss = None
boss_health = 100
boss_max_health = 100
boss_attack_cooldown = 1000
boss_last_attack = 0
boss_bullets = []
boss_entry_y = 60

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

# Gun upgrade system
GUN_UPGRADE_DURATION = 8000  # 8 seconds duration for upgrades
rapid_fire_cooldown = 100  # ms, for rapid fire
# Store upgrades as a dict: {upgrade_name: expiration_time}
gun_upgrades = {}

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


# Survival mode destruction effect (support multiple simultaneous explosions)
survival_explosions = []  # Each item: {"pieces": [...], "start_time": int}
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
    enemy_speed = 2  # Keep initial speed slow
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


# Improved Survival Enemy AI – Smarter movement, dodging, and shooting
def move_enemy(enemy):
    # Simple vertical movement only, speed increases with level
    vertical_speed = enemy_speed + (level - 1) * 0.4  # Increase speed more gradually per level
    enemy.y += int(vertical_speed)
    # Clamp position
    enemy.y = max(-50, min(enemy.y, HEIGHT - enemy.height))

# Power-up spawn logic
def spawn_powerup():
    # Add new gun upgrade power-ups
    powerup_types = ["health", "shield", "clear_enemies", "double_gun", "triple_gun", "rapid_gun", "piercing_gun"]
    powerup_type = random.choice(powerup_types)
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

            # Sprint logic: hold LSHIFT to move faster while energy > 0
            current_time = pygame.time.get_ticks()
            sprinting = False
            if keys[pygame.K_LSHIFT] and energy > 0:
                sprinting = True
                player_speed_actual = sprint_speed
                energy -= energy_drain_rate
                if energy <= 0:
                    energy = 0
                    energy_depleted_time = current_time
            else:
                player_speed_actual = player_speed

            # Sprinting effect: store previous positions for trail
            if 'sprint_trail' not in globals():
                sprint_trail = []
            if sprinting:
                sprint_trail.append((player.x, player.y))
                if len(sprint_trail) > 10:
                    sprint_trail = sprint_trail[-10:]
            else:
                sprint_trail = []

            # Energy only recharges after full depletion and cooldown (5s countdown, then instant refill)
            if energy < max_energy:
                if energy == 0:
                    # Only refill after cooldown
                    if current_time - energy_depleted_time >= energy_cooldown:
                        energy = max_energy

            # Restrict movement to left and right only (smooth), use sprint speed if sprinting
            target_x = player_pos_x
            if keys[pygame.K_a] and player.left > 0:
                target_x -= player_speed_actual
            if keys[pygame.K_d] and player.right < WIDTH:
                target_x += player_speed_actual
            # Smoothly interpolate player x
            player_pos_x += (target_x - player_pos_x) * 0.4
            # Ensure the player's y-position remains constant
            player_pos_y = HEIGHT - 60
            player.x = int(player_pos_x)
            player.y = int(player_pos_y)

            # Handle gun upgrade expiration (combinable)
            now = pygame.time.get_ticks()
            expired = [k for k, v in gun_upgrades.items() if now > v]
            for k in expired:
                del gun_upgrades[k]

            # Handle shooting with combinable upgrades
            if keys[pygame.K_SPACE]:
                current_time = pygame.time.get_ticks()
                upgrades = set(gun_upgrades.keys())
                cooldown = rapid_fire_cooldown if 'rapid' in upgrades else shoot_cooldown
                if current_time - last_shot_time >= cooldown:
                    # Determine bullet pattern
                    bullet_defs = []
                    if 'triple' in upgrades:
                        # Wider spread for triple shot (shotgun style)
                        bullet_defs = [player.centerx - 30, player.centerx, player.centerx + 30]
                    elif 'double' in upgrades:
                        # Wider gap for double shot (shotgun style)
                        bullet_defs = [player.centerx - 22, player.centerx + 22]
                    else:
                        bullet_defs = [player.centerx]
                    for bx in bullet_defs:
                        bullet = {'rect': pygame.Rect(bx, player.y, 10, 20), 'piercing': 'piercing' in upgrades}
                        bullets.append(bullet)
                    play_fx(shoot_sound, channel_fx_shoot, shoot_sound_volume)
                    last_shot_time = current_time


            # Remove off-screen bullets
            for bullet in bullets[:]:
                bullet['rect'].y -= bullet_speed
                if bullet['rect'].bottom < 0:
                    bullets.remove(bullet)


            # Limit the number of bullets
            if len(bullets) > 50:
                bullets = bullets[-50:]


            # Boss fight trigger
            if not boss_active and score >= 100:
                boss_active = True
                boss = pygame.Rect(WIDTH//2 - 75, -150, 150, 100)
                boss_health = boss_max_health
                boss_bullets = []
                # Pause normal enemy spawns
                enemies.clear()
                enemy_bullets.clear()

            # Normal enemy spawn only if boss is not active
            if not boss_active:
                if current_time >= enemy_spawn_resume_time:  # Check if cooldown has elapsed
                    if current_time - last_enemy_spawn > enemy_spawn_time:
                        # Spawn only one enemy until level 20, then increase slowly
                        spawn_count = 1
                        if level >= 20:
                            spawn_count = 2
                        if level >= 40:
                            spawn_count = 3
                        for _ in range(spawn_count):
                            enemy = pygame.Rect(random.randint(0, WIDTH-50), -50, 50, 50)
                            enemies.append(enemy)
                        last_enemy_spawn = current_time

            # Enemy shooting logic removed for survival mode

            if game_state == "play" and not pause:
                # Move enemy bullets
                for bullet in enemy_bullets[:]:
                    bullet.y += enemy_bullet_speed
                    if bullet.top > HEIGHT:  # Remove bullets that go off-screen
                        enemy_bullets.remove(bullet)
                    elif bullet.colliderect(player):  # Check collision with the player
                        if not shield and not sprinting:  # If not shielded or sprinting, reduce health
                            health -= 1
                        enemy_bullets.remove(bullet)
                        if health <= 0:
                            pygame.mixer.music.stop()
                            play_fx(game_over_sound, channel_fx_hit, hit_sound_volume)
                            game_state = "game_over"

                # Update enemies

                for enemy in enemies[:]:
                    move_enemy(enemy)
                    # Remove enemy if it passes the bottom of the screen
                    if enemy.top > HEIGHT:
                        enemies.remove(enemy)
                        continue
                    # If shield is active, destroy only enemies overlapping the player
                    if shield and enemy.colliderect(player):
                        enemies.remove(enemy)
                        score += 1
                        play_fx(hit_sound, channel_fx_hit, hit_sound_volume)
                        survival_explosions.append({
                            "pieces": create_survival_enemy_pieces(enemy),
                            "start_time": pygame.time.get_ticks()
                        })
                        continue
                    if enemy.colliderect(player):
                        if not shield and not sprinting:
                            health -= 1
                            enemies.remove(enemy)
                        elif sprinting:
                            enemies.remove(enemy)
                        if health <= 0:
                            pygame.mixer.music.stop()
                            play_fx(game_over_sound, channel_fx_hit, hit_sound_volume)
                            game_state = "game_over"
                            break

                    # Track if this enemy was hit by a bullet this frame
                    hit_this_frame = False
                    for bullet in bullets[:]:
                        if enemy.colliderect(bullet['rect']):
                            bullets.remove(bullet)
                            enemies.remove(enemy)
                            score += 1
                            play_fx(hit_sound, channel_fx_hit, hit_sound_volume)
                            # Trigger destruction animation for this enemy
                            survival_explosions.append({
                                "pieces": create_survival_enemy_pieces(enemy),
                                "start_time": pygame.time.get_ticks()
                            })
                            hit_this_frame = True
                            break


                # Animate all active enemy explosions
                for explosion in survival_explosions[:]:
                    elapsed_time = pygame.time.get_ticks() - explosion["start_time"]
                    if elapsed_time < survival_enemy_destroy_duration:
                        for piece in explosion["pieces"]:
                            piece["rect"].x += piece["velocity"][0]
                            piece["rect"].y += piece["velocity"][1]
                            pygame.draw.rect(WIN, RED, piece["rect"])  # Draw each piece
                    else:
                        survival_explosions.remove(explosion)

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



            # Update enemies (skip if boss is active)
            if not boss_active:
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
                        if enemy.colliderect(bullet['rect']):
                            if bullet['piercing']:
                                enemies.remove(enemy)
                                score += 1
                                play_fx(hit_sound, channel_fx_hit, hit_sound_volume)
                                # Do NOT remove bullet, allow it to keep going
                                break
                            else:
                                bullets.remove(bullet)
                                enemies.remove(enemy)
                                score += 1
                                play_fx(hit_sound, channel_fx_hit, hit_sound_volume)
                                break

            # Boss logic
            if boss_active:
                # Move boss into view
                if boss.y < boss_entry_y:
                    boss.y += 4
                # Boss attacks
                if pygame.time.get_ticks() - boss_last_attack > boss_attack_cooldown:
                    # Fire a spread of bullets
                    for dx in [-40, -20, 0, 20, 40]:
                        boss_bullets.append({'rect': pygame.Rect(boss.centerx + dx - 5, boss.bottom, 10, 20), 'velocity': (dx//10, 8)})
                    boss_last_attack = pygame.time.get_ticks()
                # Move boss bullets
                for b in boss_bullets[:]:
                    b['rect'].x += b['velocity'][0]
                    b['rect'].y += b['velocity'][1]
                    if b['rect'].top > HEIGHT or b['rect'].left < 0 or b['rect'].right > WIDTH:
                        boss_bullets.remove(b)
                    elif b['rect'].colliderect(player):
                        boss_bullets.remove(b)
                        if not shield and not sprinting:
                            health -= 2
                        if health <= 0:
                            pygame.mixer.music.stop()
                            play_fx(game_over_sound, channel_fx_hit, hit_sound_volume)
                            game_state = "game_over"
                # Boss takes damage from player bullets
                for bullet in bullets[:]:
                    if boss.colliderect(bullet['rect']):
                        boss_health -= 2 if bullet['piercing'] else 1
                        if not bullet['piercing']:
                            bullets.remove(bullet)
                        play_fx(hit_sound, channel_fx_hit, hit_sound_volume)
                        if boss_health <= 0:
                            boss_active = False
                            boss = None
                            boss_bullets.clear()
                            # Reward player
                            score += 20
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
                            # Award points and trigger explosion for each enemy cleared
                            for enemy in enemies[:]:
                                score += 1
                                play_fx(hit_sound, channel_fx_hit, hit_sound_volume)
                                survival_explosions.append({
                                    "pieces": create_survival_enemy_pieces(enemy),
                                    "start_time": pygame.time.get_ticks()
                                })
                            enemies.clear()  # Clear all enemies from the screen
                            enemy_bullets.clear()  # Clear all enemy bullets from the screen
                            splash_active = True  # Activate the splash effect
                            splash_start_time = pygame.time.get_ticks()  # Record the start time
                            enemy_spawn_resume_time = pygame.time.get_ticks() + enemy_spawn_cooldown  # Set the cooldown timer
                        elif powerup["type"] == "double_gun":
                            gun_upgrades['double'] = pygame.time.get_ticks() + GUN_UPGRADE_DURATION
                        elif powerup["type"] == "triple_gun":
                            gun_upgrades['triple'] = pygame.time.get_ticks() + GUN_UPGRADE_DURATION
                        elif powerup["type"] == "rapid_gun":
                            gun_upgrades['rapid'] = pygame.time.get_ticks() + GUN_UPGRADE_DURATION
                        elif powerup["type"] == "piercing_gun":
                            gun_upgrades['piercing'] = pygame.time.get_ticks() + GUN_UPGRADE_DURATION

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
                enemy_speed += 0.2  # Increase speed more slowly per level
                enemy_spawn_time = max(400, enemy_spawn_time - 20)  # Decrease spawn time more slowly

            if score > high_score:
                high_score = score

        pygame.draw.rect(WIN, BLUE, player)

        # Draw sprinting effect (trail and glow)
        if 'sprint_trail' in globals() and sprint_trail:
            for i, (tx, ty) in enumerate(sprint_trail):
                alpha = int(80 * (1 - i / len(sprint_trail)))
                trail_surf = pygame.Surface((player.width, player.height), pygame.SRCALPHA)
                trail_surf.fill((0, 255, 0, alpha))
                WIN.blit(trail_surf, (tx, ty))
        if 'sprinting' in locals() and sprinting:
            # Draw a green glow around the player
            glow_size = 16
            glow_surf = pygame.Surface((player.width + glow_size, player.height + glow_size), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (0, 255, 0, 120), (glow_size//2, glow_size//2, player.width, player.height), border_radius=8)
            WIN.blit(glow_surf, (player.x - glow_size//2, player.y - glow_size//2))

        # Draw the shield animation
        if shield:
            pygame.draw.circle(WIN, BLUE, player.center, shield_animation_radius, 2)  # Draw a glowing circle

        # Draw smooth dash animation
        if dash_animation_active:
            elapsed_time = pygame.time.get_ticks() - dash_animation_start_time
            t = min(1.0, elapsed_time / dash_animation_duration)
            # Ease out: fast at first, slow at end
            t_eased = 1 - (1 - t) * (1 - t)
            outline_size = int(10 + (dash_animation_max_outline - 10) * (1 - t_eased))
            outline_alpha = int(dash_animation_max_alpha * (1 - t_eased))
            # Create a surface for alpha blending
            dash_surf = pygame.Surface((player.width + outline_size * 2, player.height + outline_size * 2), pygame.SRCALPHA)
            # Draw a glowing outline (yellow, fading out)
            pygame.draw.rect(
                dash_surf,
                (255, 255, 0, outline_alpha),
                pygame.Rect(outline_size//2, outline_size//2, player.width + outline_size, player.height + outline_size),
                outline_size
            )
            WIN.blit(dash_surf, (player.x - outline_size//2, player.y - outline_size//2))
            if elapsed_time >= dash_animation_duration:
                dash_animation_active = False  # Deactivate the dash animation

        # Draw health bar with smooth animation and blink
        pygame.draw.rect(WIN, WHITE, (WIDTH//2 - 100, 10, 200, 20))  # Background of health bar
        global display_health
        try:
            display_health
        except NameError:
            display_health = health
        # Smoothly interpolate displayed health
        display_health += (health - display_health) * 0.3
        bar_width = (display_health / max_health) * 200
        if health_blink_active:
            elapsed_time = pygame.time.get_ticks() - health_blink_start_time
            if elapsed_time < health_blink_duration:
                if (elapsed_time // 100) % 2 == 0:
                    pygame.draw.rect(WIN, RED, (WIDTH//2 - 100, 10, bar_width, 20))
            else:
                health_blink_active = False
                pygame.draw.rect(WIN, RED, (WIDTH//2 - 100, 10, bar_width, 20))
        else:
            pygame.draw.rect(WIN, RED, (WIDTH//2 - 100, 10, bar_width, 20))

        # Draw static energy bar under health bar
        pygame.draw.rect(WIN, WHITE, (WIDTH//2 - 100, 35, 200, 20))  # Background of energy bar
        energy_bar_width = (energy / max_energy) * 200
        # Show cooldown visually: if energy is 0 and cooldown is active, fill bar gray with countdown
        if energy == 0 and current_time - energy_depleted_time < energy_cooldown:
            cooldown_elapsed = current_time - energy_depleted_time
            cooldown_ratio = min(1.0, cooldown_elapsed / energy_cooldown)
            cooldown_bar_width = int(200 * cooldown_ratio)
            # Draw gray bar filling up to show countdown
            pygame.draw.rect(WIN, (100, 100, 100), (WIDTH//2 - 100, 35, cooldown_bar_width, 20))
        else:
            pygame.draw.rect(WIN, (0, 255, 0), (WIDTH//2 - 100, 35, energy_bar_width, 20))  # Green energy bar
        energy_label = font.render("Energy", True, WHITE)
        WIN.blit(energy_label, (WIDTH//2 - 100, 60))

        # Draw score and level
        WIN.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        WIN.blit(font.render(f"Level: {level}", True, WHITE), (WIDTH - 150, 10))
        WIN.blit(font.render(f"High Score: {high_score}", True, WHITE), (10, 40))


        for bullet in bullets:
            color = (0, 255, 255) if bullet['piercing'] else BLUE
            pygame.draw.rect(WIN, color, bullet['rect'])

        # Draw boss if active
        if boss_active and boss:
            pygame.draw.rect(WIN, (180, 0, 180), boss)
            # Boss health bar
            pygame.draw.rect(WIN, WHITE, (WIDTH//2 - 100, 70, 200, 20))
            boss_bar_width = (boss_health / boss_max_health) * 200
            pygame.draw.rect(WIN, (255, 0, 255), (WIDTH//2 - 100, 70, boss_bar_width, 20))
            boss_label = font.render("BOSS", True, (255, 0, 255))
            WIN.blit(boss_label, (WIDTH//2 - boss_label.get_width()//2, 45))
            # Draw boss bullets
            for b in boss_bullets:
                pygame.draw.rect(WIN, (255, 100, 255), b['rect'])

        for enemy in enemies:
            pygame.draw.rect(WIN, RED, enemy)


        for powerup in powerups:
            if powerup["type"] == "health":
                pygame.draw.rect(WIN, GREEN, powerup["rect"])  # Health power-up
            elif powerup["type"] == "shield":
                pygame.draw.rect(WIN, BLUE, powerup["rect"])  # Shield power-up
            elif powerup["type"] == "clear_enemies":
                pygame.draw.rect(WIN, YELLOW, powerup["rect"])  # Clear enemies power-up
            elif powerup["type"] == "double_gun":
                pygame.draw.rect(WIN, (0, 200, 255), powerup["rect"])  # Cyan for double gun
            elif powerup["type"] == "triple_gun":
                pygame.draw.rect(WIN, (255, 100, 0), powerup["rect"])  # Orange for triple gun
            elif powerup["type"] == "rapid_gun":
                pygame.draw.rect(WIN, (255, 0, 255), powerup["rect"])  # Magenta for rapid fire
            elif powerup["type"] == "piercing_gun":
                pygame.draw.rect(WIN, (255, 255, 255), powerup["rect"])  # White for piercing
        # Draw current gun upgrade indicator
        if gun_upgrades:
            upgrade_names = []
            if 'double' in gun_upgrades: upgrade_names.append('Double')
            if 'triple' in gun_upgrades: upgrade_names.append('Triple')
            if 'rapid' in gun_upgrades: upgrade_names.append('Rapid')
            if 'piercing' in gun_upgrades: upgrade_names.append('Piercing')
            if upgrade_names:
                upgrade_label = font.render(f"Gun: {' + '.join(upgrade_names)}", True, (0,255,255))
                WIN.blit(upgrade_label, (WIDTH//2 - upgrade_label.get_width()//2, 90))

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


            # Handle gun upgrade expiration (combinable, arena mode)
            now = pygame.time.get_ticks()
            expired = [k for k, v in gun_upgrades.items() if now > v]
            for k in expired:
                del gun_upgrades[k]

            # Shooting logic (combinable upgrades, arena mode)
            if keys[pygame.K_SPACE]:
                current_time = pygame.time.get_ticks()
                upgrades = set(gun_upgrades.keys())
                cooldown = rapid_fire_cooldown if 'rapid' in upgrades else shoot_cooldown
                if current_time - last_shot_time >= cooldown:
                    bullet_defs = []
                    if 'triple' in upgrades:
                        bullet_defs = [player.centerx - 15, player.centerx - 5, player.centerx + 5]
                    elif 'double' in upgrades:
                        bullet_defs = [player.centerx - 15, player.centerx + 5]
                    else:
                        bullet_defs = [player.centerx - 5]
                    for bx in bullet_defs:
                        bullet = {'rect': pygame.Rect(bx, player.y, 10, 20), 'piercing': 'piercing' in upgrades}
                        bullets.append(bullet)
                    play_fx(shoot_sound, channel_fx_shoot, shoot_sound_volume)
                    last_shot_time = current_time

            # Move bullets (arena mode, dict structure)
            for bullet in bullets[:]:
                bullet['rect'].y -= bullet_speed
                if bullet['rect'].bottom < 0:
                    bullets.remove(bullet)
                elif bullet['rect'].colliderect(arena_enemy):
                    if bullet['piercing']:
                        arena_enemy_health -= 1
                        play_fx(hit_sound, channel_fx_hit, hit_sound_volume)
                        # Do NOT remove bullet, allow it to keep going
                    else:
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


            # Draw bullets (arena mode, dict structure)
            for bullet in bullets:
                color = (0, 255, 255) if bullet['piercing'] else BLUE
                pygame.draw.rect(WIN, color, bullet['rect'])
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
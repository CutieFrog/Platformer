import pygame
import sys
from pytmx.util_pygame import load_pygame
from pytmx import TiledTileLayer
import json
import os

# --- Прогрес ---
def load_progress():
    if os.path.exists("progress.json"):
        with open("progress.json", "r") as f:
            return json.load(f)
    return {"unlocked_levels": 1}

def save_progress(unlocked_levels):
    with open("progress.json", "w") as f:
        json.dump({"unlocked_levels": unlocked_levels}, f)

# --- Плавна анімація ---
def fade_transition(surface, fade_in=True, speed=10):
    fade = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in (range(0, 256, speed) if fade_in else range(255, -1, -speed)):
        fade.set_alpha(alpha)
        scaled = pygame.transform.scale(surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))
        surface.blit(fade, (0, 0))
        screen.blit(pygame.transform.scale(surface, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)

# --- Ініціалізація ---
pygame.init()
pygame.mixer.init()

# --- Константи ---
GAME_WIDTH = 320
GAME_HEIGHT = 180
TILE_SIZE = 16
PLAYER_SPEED = 2
PLAYER_JUMP = -5
GRAVITY = 0.2

# --- Екран ---
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Platformer")

# --- Масштаб ---
scale_x = SCREEN_WIDTH // GAME_WIDTH
scale_y = SCREEN_HEIGHT // GAME_HEIGHT

# --- Завантаження карт ---
tmx_menu = load_pygame("Tails/Maps/menu.tmx")
tmx_level_select = None
tmx_level = None

# --- Музика ---
pygame.mixer.music.load("Music/Mystical/menu_music.wav")
pygame.mixer.music.play(-1)

# --- Стан ---
game_state = "menu"
current_level = 1

# --- Прогрес ---
progress = load_progress()
unlocked_levels = progress["unlocked_levels"]

# --- Гравець ---
player = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
velocity_y = 0
on_ground = False

# --- Завантаження спрайтів гравця ---
player_image = pygame.image.load("Player/Outline/player.png").convert_alpha()
player_frames = [player_image.subsurface(pygame.Rect(i * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)) for i in range(4)]
player_frame_index = 0
player_frame_timer = 0

clock = pygame.time.Clock()
running = True

# --- Цикл ---
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                game_x = mx * GAME_WIDTH // SCREEN_WIDTH
                game_y = my * GAME_HEIGHT // SCREEN_HEIGHT

                for obj in tmx_menu.objects:
                    obj_left = int(obj.x)
                    obj_top = int(obj.y)
                    obj_right = obj_left + int(obj.width)
                    obj_bottom = obj_top + int(obj.height)

                    if obj_left <= game_x < obj_right and obj_top <= game_y < obj_bottom:
                        if obj.name == "start":
                            print("▶️ START натиснуто!")
                            pygame.mixer.music.stop()

                            game_surface.fill((0, 0, 0))
                            for layer in tmx_menu.visible_layers:
                                if isinstance(layer, TiledTileLayer):
                                    for x, y, gid in layer:
                                        tile = tmx_menu.get_tile_image_by_gid(gid)
                                        if tile:
                                            game_surface.blit(tile, (x * TILE_SIZE, y * TILE_SIZE))
                            fade_transition(game_surface, fade_in=False)

                            tmx_level = load_pygame("Tails/Maps/level_1.tmx")
                            for obj in tmx_level.objects:
                                if obj.name == "spawn":
                                    player.x = int(obj.x)
                                    player.y = int(obj.y)

                            game_state = "playing"
                            fade_transition(game_surface, fade_in=True)

                        elif obj.name == "exit":
                            print("❌ EXIT натиснуто!")
                            pygame.quit()
                            sys.exit()

    # --- Ігрова логіка ---
    if game_state == "playing":
        if keys[pygame.K_LEFT]:
            player.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            player.x += PLAYER_SPEED
        if keys[pygame.K_SPACE] and on_ground:
            velocity_y = PLAYER_JUMP
            on_ground = False

        # Анімація гравця
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            player_frame_timer += 1
            if player_frame_timer >= 10:
                player_frame_index = (player_frame_index + 1) % len(player_frames)
                player_frame_timer = 0
        else:
            player_frame_index = 0

        velocity_y += GRAVITY
        player.y += velocity_y

        on_ground = False
        for layer in tmx_level.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, gid in layer:
                    if gid:
                        tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        if player.colliderect(tile_rect):
                            if velocity_y > 0:
                                player.bottom = tile_rect.top
                                on_ground = True
                                velocity_y = 0
                            elif velocity_y < 0:
                                player.top = tile_rect.bottom
                                velocity_y = 0

    # --- Малювання ---
    game_surface.fill((0, 0, 0))

    if game_state == "menu":
        for layer in tmx_menu.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, gid in layer:
                    tile = tmx_menu.get_tile_image_by_gid(gid)
                    if tile:
                        game_surface.blit(tile, (x * TILE_SIZE, y * TILE_SIZE))

    elif game_state == "playing" and tmx_level:
        for layer in tmx_level.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, gid in layer:
                    tile = tmx_level.get_tile_image_by_gid(gid)
                    if tile:
                        game_surface.blit(tile, (x * TILE_SIZE, y * TILE_SIZE))

        game_surface.blit(player_frames[int(player_frame_index)], (player.x, player.y))

    # --- Вивід ---
    scaled_surface = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()
    clock.tick(60)

# --- Завершення ---
pygame.quit()
sys.exit()


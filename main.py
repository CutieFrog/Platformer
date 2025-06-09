import pygame
import sys

# Ініціалізація Pygame
pygame.init()

# Отримання розмірів екрана
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h

# Створення повноекранного вікна
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Моя 2D гра")

# Основні кольори
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Основний цикл гри
running = True
while running:
    screen.fill(BLACK)  # Заповнюємо екран чорним кольором

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Вихід по натисканню ESC
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    pygame.display.flip()  # Оновлення екрана

# Завершення Pygame
pygame.quit()
sys.exit()


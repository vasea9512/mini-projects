# game.py
import pygame
import random
import math
import sys
from ranking import add_rank

pygame.init()

# ---------- Параметры окна ----------
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# ---------- Шрифты ----------
font_big = pygame.font.SysFont("consolas", 64)
font_med = pygame.font.SysFont("consolas", 32)
font_small = pygame.font.SysFont("consolas", 24)

# ---------- Цвета ----------
BLACK = (0, 0, 0)
BLUE = (0, 200, 255)
RED = (255, 60, 80)
PURPLE = (180, 0, 255)
YELLOW = (255, 220, 0)
GRID = (0, 60, 90)

# ---------- Функции ----------

def draw_grid():
    step = 40
    for x in range(0, WIDTH, step):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, step):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))

def menu():
    while True:
        screen.fill(BLACK)
        draw_grid()

        t = font_big.render("TRON SNAKE", True, BLUE)
        s = font_med.render("ENTER - PLAY | ESC - EXIT", True, YELLOW)

        screen.blit(t, (WIDTH//2 - 200, HEIGHT//3))
        screen.blit(s, (WIDTH//2 - 260, HEIGHT//2))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return True
                if e.key == pygame.K_ESCAPE:
                    return False

def game(name):
    x, y = WIDTH//2, HEIGHT//2
    dx, dy = 10, 0

    food_x = random.randint(100, WIDTH-100)
    food_y = random.randint(100, HEIGHT-100)

    score = 0
    ghosts = []

    while True:
        clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return score
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    dx, dy = -10, 0
                if e.key == pygame.K_RIGHT:
                    dx, dy = 10, 0
                if e.key == pygame.K_UP:
                    dx, dy = 0, -10
                if e.key == pygame.K_DOWN:
                    dx, dy = 0, 10

        x += dx
        y += dy
        x %= WIDTH
        y %= HEIGHT

        # еда
        if abs(x - food_x) < 15 and abs(y - food_y) < 15:
            score += 1
            food_x = random.randint(100, WIDTH-100)
            food_y = random.randint(100, HEIGHT-100)

        # призраки
        if score > 0 and len(ghosts) < score // 3 + 1:
            ghosts.append([random.randint(0, WIDTH), random.randint(0, HEIGHT)])

        for g in ghosts:
            dxg = x - g[0]
            dyg = y - g[1]
            d = math.hypot(dxg, dyg)
            if d:
                g[0] += dxg / d * 2
                g[1] += dyg / d * 2

        for g in ghosts:
            if math.hypot(x - g[0], y - g[1]) < 15:
                return score

        # отрисовка
        screen.fill(BLACK)
        draw_grid()

        pygame.draw.circle(screen, BLUE, (int(x), int(y)), 10)
        pygame.draw.circle(screen, RED, (food_x, food_y), 8)
        for g in ghosts:
            pygame.draw.circle(screen, PURPLE, (int(g[0]), int(g[1])), 10)

        hud = font_small.render(f"{name} Score: {score}", True, YELLOW)
        screen.blit(hud, (20, 20))

        pygame.display.flip()

def run_game():
    name = "PLAYER"

    if not menu():
        return

    score = game(name)
    add_rank(name, score)

    # Game Over экран
    screen.fill(BLACK)
    t = font_big.render(f"GAME OVER: {score}", True, RED)
    screen.blit(t, (WIDTH//2 - 250, HEIGHT//2))
    pygame.display.flip()
    pygame.time.wait(3000)

    pygame.quit()
    sys.exit()
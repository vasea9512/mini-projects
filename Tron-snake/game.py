import pygame
import random
import math
import sys
from ranking import add_rank, load_rank

pygame.init()

# ---------- Экран ----------
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
GRAY = (100, 100, 100)


# ---------- Сетка ----------
def draw_grid():
    step = 40
    for x in range(0, WIDTH, step):
        pygame.draw.line(screen, GRID, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, step):
        pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))


# ---------- Меню ----------
def menu():
    while True:
        screen.fill(BLACK)
        draw_grid()

        t = font_big.render("TRON SNAKE", True, BLUE)
        s = font_med.render("ENTER - PLAY | ESC - EXIT", True, YELLOW)

        screen.blit(t, (WIDTH // 2 - 200, HEIGHT // 3))
        screen.blit(s, (WIDTH // 2 - 260, HEIGHT // 2))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return True
                if e.key == pygame.K_ESCAPE:
                    return False


# ---------- Имя ----------
def get_name():
    name = ""
    while True:
        screen.fill(BLACK)
        draw_grid()

        title = font_big.render("ENTER NAME", True, BLUE)
        text = font_med.render(name, True, YELLOW)

        screen.blit(title, (WIDTH // 2 - 220, HEIGHT // 3))
        screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return name if name else "PLAYER"
                elif e.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 10:
                        name += e.unicode


# ---------- Пауза ----------
def level_pause(level):
    start = pygame.time.get_ticks()

    while True:
        elapsed = (pygame.time.get_ticks() - start) // 1000
        remain = 10 - elapsed

        if remain <= 0:
            return

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:  # пропуск
                    return

        screen.fill(BLACK)
        draw_grid()

        t = font_big.render(f"LEVEL {level}", True, BLUE)
        s = font_med.render(f"START IN: {remain}", True, YELLOW)
        skip = font_small.render("SPACE - SKIP", True, BLUE)

        screen.blit(t, (WIDTH // 2 - 200, HEIGHT // 2 - 50))
        screen.blit(s, (WIDTH // 2 - 150, HEIGHT // 2 + 40))
        screen.blit(skip, (WIDTH // 2 - 120, HEIGHT // 2 + 90))

        pygame.display.flip()


# ---------- Стены ----------
def create_walls(level):
    walls = []
    if level >= 6:
        for _ in range(level * 3):
            walls.append([random.randint(0, WIDTH), random.randint(0, HEIGHT)])
    return walls


# ---------- Игра ----------
def game(name):

    x, y = WIDTH // 2, HEIGHT // 2
    dx, dy = 10, 0

    food_x = random.randint(100, WIDTH - 100)
    food_y = random.randint(100, HEIGHT - 100)
    food_time = pygame.time.get_ticks()

    score = 0
    food_count = 0
    level = 1

    lives = 3
    safe_time = 0
    freeze_time = 0

    ghosts = []
    walls = []

    level_pause(level)
    freeze_time = pygame.time.get_ticks() + 3000

    # безопасный старт
    while True:
        x = random.randint(200, WIDTH - 200)
        y = random.randint(200, HEIGHT - 200)

        safe = True
        for g in ghosts:
            if math.hypot(x - g[0], y - g[1]) < 100:
                safe = False

        for w in walls:
            if math.hypot(x - w[0], y - w[1]) < 200:
                safe = False

        if safe:
            break
    dx, dy = 0, 0
    safe_time = pygame.time.get_ticks() + 2000

    while True:
        clock.tick(60)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return score
            if e.type == pygame.KEYDOWN:

                # движение
                if e.key == pygame.K_LEFT:
                    dx, dy = -10, 0
                if e.key == pygame.K_RIGHT:
                    dx, dy = 10, 0
                if e.key == pygame.K_UP:
                    dx, dy = 0, -10
                if e.key == pygame.K_DOWN:
                    dx, dy = 0, 10

                # выход из fullscreen
                if e.key == pygame.K_ESCAPE:
                    pygame.display.set_mode((WIDTH, HEIGHT))

        if pygame.time.get_ticks() > freeze_time:
            x += dx
            y += dy

        x %= WIDTH
        y %= HEIGHT

        # ---------- ЕДА ----------
        if abs(x - food_x) < 15 and abs(y - food_y) < 15:
            food_count += 1

            elapsed = (pygame.time.get_ticks() - food_time) / 1000

            if elapsed < 10:
                score += 50
            elif elapsed < 20:
                score += 25
            elif elapsed < 30:
                score += 10
            else:
                score += 5

            if food_count % 5 == 0:
                level += 1
                ghosts = []
                walls = create_walls(level)
                level_pause(level)

                # ✅ 3 секунды подготовки
                freeze_time = pygame.time.get_ticks() + 3000

            food_x = random.randint(100, WIDTH - 100)
            food_y = random.randint(100, HEIGHT - 100)
            food_time = pygame.time.get_ticks()

        # ---------- ПРИЗРАКИ ----------
        if level == 1:
            target = 0
        elif level == 2:
            target = 1
        elif level == 3:
            target = 2
        elif level == 4:
            target = 3 + (food_count // 2)
        elif level == 5:
            target = 5 + food_count
        else:
            cycle = (level - 1) % 5 + 1
            if cycle == 1:
                target = 0
            elif cycle == 2:
                target = 1
            elif cycle == 3:
                target = 2
            elif cycle == 4:
                target = 3 + (food_count // 2)
            else:
                target = 5 + food_count

        while len(ghosts) < target:
            ghosts.append([random.randint(0, WIDTH), random.randint(0, HEIGHT)])

        # движение + анти-слипание
        for i, g in enumerate(ghosts):
            dxg = x - g[0]
            dyg = y - g[1]
            d = math.hypot(dxg, dyg)

            if pygame.time.get_ticks() > freeze_time:
                if d:
                    g[0] += dxg / d * 2
                    g[1] += dyg / d * 2
            # анти-слипание
            for j, o in enumerate(ghosts):
                if i != j:
                    dist = math.hypot(g[0] - o[0], g[1] - o[1])
                    if dist < 40 and dist > 0:
                        g[0] += (g[0] - o[0]) / dist * 1.5
                        g[1] += (g[1] - o[1]) / dist * 1.5

        # столкновения
        for g in ghosts:

            if (
                math.hypot(x - g[0], y - g[1]) < 15
                and pygame.time.get_ticks() > safe_time
            ):
                lives -= 1
                safe_time = pygame.time.get_ticks() + 1500

                # ✅ ВАЖНО — телепорт игрока
                x = WIDTH // 2
                y = HEIGHT // 2

                # ✅ можно ещё остановить движение
                dx, dy = 0, 0

                if lives <= 0:

                    return score

        for w in walls:
            if (
                math.hypot(x - w[0], y - w[1]) < 15
                and pygame.time.get_ticks() > safe_time
            ):
                lives -= 1
                safe_time = pygame.time.get_ticks() + 1500

                x = random.randint(100, WIDTH - 100)
                y = random.randint(100, HEIGHT - 100)

                dx, dy = 0, 0

                if lives <= 0:
                    return score

                break  # ← важно, чтобы не проверять остальные стены после столкновения

        # ---------- РЕНДЕР ----------
        screen.fill(BLACK)
        draw_grid()

        pygame.draw.circle(screen, BLUE, (int(x), int(y)), 10)
        pygame.draw.circle(screen, RED, (food_x, food_y), 8)

        for g in ghosts:
            pygame.draw.circle(screen, PURPLE, (int(g[0]), int(g[1])), 10)

        for w in walls:
            pygame.draw.rect(screen, GRAY, (int(w[0]), int(w[1]), 20, 20))

        # ❤️ ЖИЗНИ
        for i in range(lives):
            pygame.draw.circle(screen, RED, (WIDTH - 30 - i * 30, 30), 10)

        # HUD
        hud = font_small.render(
            f"{name} | Score: {score} | Level: {level}", True, YELLOW
        )
        screen.blit(hud, (20, 20))

        # ✅ GET READY (ТОЖЕ ВНУТРИ ЦИКЛА)
        if pygame.time.get_ticks() < freeze_time:
            ready = font_big.render("GET READY!", True, BLUE)
            screen.blit(ready, (WIDTH // 2 - ready.get_width() // 2, HEIGHT // 2))

        # ✅ ВСЕГДА в конце
        pygame.display.flip()


# ---------- GAME OVER ----------
def run_game():

    if not menu():
        return

    name = get_name()
    score = game(name)

    add_rank(name, score)
    rank = load_rank()

    while True:
        screen.fill(BLACK)
        draw_grid()

        t = font_big.render(f"GAME OVER: {score}", True, RED)
        screen.blit(t, (WIDTH // 2 - 250, 80))

        y = 200
        for i, r in enumerate(rank):
            txt = font_small.render(f"{i+1}. {r['name']} - {r['score']}", True, YELLOW)
            screen.blit(txt, (WIDTH // 2 - 150, y))
            y += 30

        s = font_med.render("ENTER - RESTART | ESC - EXIT", True, BLUE)
        screen.blit(s, (WIDTH // 2 - 320, HEIGHT - 120))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    run_game()
                    return
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

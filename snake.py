import pygame
import random
import math
import os

pygame.init()

# ---------- НАСТРОЙКИ ОКНА ----------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRON Snake")

clock = pygame.time.Clock()
FPS = 60

# ---------- ЦВЕТА ----------
BLACK = (0, 0, 0)
NEON_BLUE = (0, 200, 255)
NEON_RED = (255, 60, 80)
NEON_PURPLE = (180, 0, 255)
NEON_GRID = (0, 80, 120)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)

# ---------- ШРИФТЫ ----------
font_small = pygame.font.SysFont("consolas", 22)
font_medium = pygame.font.SysFont("consolas", 32)
font_big = pygame.font.SysFont("consolas", 48)

# ---------- ПАРАМЕТРЫ ИГРЫ ----------
SNAKE_BLOCK = 10
SNAKE_SPEED = 12

TRAIL_MAX_LEN = 40          # длина следа
TRAIL_STEP = 2              # как часто добавлять точку в след
GLOW_LAYERS = 4             # слоёв свечения
GLOW_SPREAD = 6             # радиус свечения

GHOST_SPEED = 3
GHOST_SPAWN_SCORE_STEP = 25

HIGHSCORE_FILE = "highscore_tron.txt"


# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------

def load_highscore():
    if not os.path.exists(HIGHSCORE_FILE):
        return 0
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0


def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except:
        pass


def draw_text_center(text, font, color, surface, y):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(WIDTH // 2, y))
    surface.blit(render, rect)


def draw_grid():
    # неоновая сетка Tron
    step = 40
    for x in range(0, WIDTH, step):
        pygame.draw.line(screen, NEON_GRID, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, step):
        pygame.draw.line(screen, NEON_GRID, (0, y), (WIDTH, y), 1)


def draw_glow_point(x, y, color, base_size):
    # рисуем сильное свечение вокруг точки
    glow_surface = pygame.Surface((base_size * 4, base_size * 4), pygame.SRCALPHA)
    cx, cy = glow_surface.get_width() // 2, glow_surface.get_height() // 2

    r, g, b = color
    for i in range(GLOW_LAYERS, 0, -1):
        alpha = int(40 * i)  # чем дальше от центра, тем прозрачнее
        radius = base_size + (GLOW_SPREAD * i)
        pygame.draw.circle(glow_surface, (r, g, b, alpha), (cx, cy), radius)

    # центральная яркая точка
    pygame.draw.circle(glow_surface, (r, g, b, 255), (cx, cy), base_size)

    screen.blit(glow_surface, (x - cx, y - cy))


def draw_food(x, y):
    draw_glow_point(int(x + SNAKE_BLOCK / 2), int(y + SNAKE_BLOCK / 2), NEON_RED, 4)


def draw_ghost(ghost):
    gx, gy = ghost["x"], ghost["y"]
    draw_glow_point(int(gx), int(gy), NEON_PURPLE, 6)


def draw_trail(trail):
    # trail: список точек (x, y)
    length = len(trail)
    for i, (tx, ty) in enumerate(trail):
        # чем старее точка, тем меньше и прозрачнее
        t = i / max(1, length)
        size = int(6 * (1 - t)) + 2
        alpha = int(255 * (1 - t))
        glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        cx, cy = glow_surface.get_width() // 2, glow_surface.get_height() // 2
        r, g, b = NEON_BLUE
        for k in range(3, 0, -1):
            a = int(alpha * (k / 3) * 0.5)
            radius = size + k * 3
            pygame.draw.circle(glow_surface, (r, g, b, a), (cx, cy), radius)
        pygame.draw.circle(glow_surface, (r, g, b, alpha), (cx, cy), size)
        screen.blit(glow_surface, (tx - cx, ty - cy))


def draw_snake_head(x, y):
    draw_glow_point(int(x + SNAKE_BLOCK / 2), int(y + SNAKE_BLOCK / 2), NEON_BLUE, 6)


def move_ghost_towards(ghost, target_x, target_y):
    gx, gy = ghost["x"], ghost["y"]
    dx = target_x - gx
    dy = target_y - gy
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    vx = dx / dist * GHOST_SPEED
    vy = dy / dist * GHOST_SPEED
    ghost["x"] += vx
    ghost["y"] += vy

    # проход сквозь стены для призраков тоже
    if ghost["x"] < 0:
        ghost["x"] = WIDTH
    elif ghost["x"] > WIDTH:
        ghost["x"] = 0
    if ghost["y"] < 0:
        ghost["y"] = HEIGHT
    elif ghost["y"] > HEIGHT:
        ghost["y"] = 0


def check_collision_point_circle(px, py, cx, cy, radius):
    return math.hypot(px - cx, py - cy) < radius


# ---------- ГЛАВНОЕ МЕНЮ ----------

def main_menu():
    highscore = load_highscore()
    running = True
    glow_phase = 0

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

        glow_phase += 0.05
        screen.fill(BLACK)
        draw_grid()

        title_color = (
            0,
            150 + int(100 * abs(math.sin(glow_phase))),
            255
        )

        draw_text_center("TRON SNAKE", font_big, title_color, screen, HEIGHT // 2 - 80)
        draw_text_center("ENTER - Start", font_medium, NEON_BLUE, screen, HEIGHT // 2 + 10)
        draw_text_center("ESC - Exit", font_small, WHITE, screen, HEIGHT // 2 + 50)
        draw_text_center(f"Highscore: {highscore}", font_small, YELLOW, screen, HEIGHT - 40)

        pygame.display.flip()


# ---------- ОСНОВНАЯ ИГРА ----------

def game_loop():
    highscore = load_highscore()

    # начальное положение змейки
    x = WIDTH // 2
    y = HEIGHT // 2
    x_change = 0
    y_change = 0

    score = 0

    # еда
    food_x = random.randrange(0, WIDTH - SNAKE_BLOCK, SNAKE_BLOCK)
    food_y = random.randrange(0, HEIGHT - SNAKE_BLOCK, SNAKE_BLOCK)

    # призраки
    ghosts = []

    # след змейки (для Tron‑линии)
    trail = []
    trail_timer = 0

    game_over = False
    game_close = False

    while not game_over:
        clock.tick(FPS)

        while game_close:
            # экран Game Over
            screen.fill(BLACK)
            draw_grid()
            draw_text_center("GAME OVER", font_big, NEON_RED, screen, HEIGHT // 2 - 40)
            draw_text_center(f"Score: {score}", font_medium, WHITE, screen, HEIGHT // 2 + 10)
            draw_text_center(f"Highscore: {highscore}", font_small, YELLOW, screen, HEIGHT // 2 + 50)
            draw_text_center("Press C to play again or Q to quit", font_small, NEON_BLUE, screen, HEIGHT // 2 + 90)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        return True  # перезапуск игры

        # обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -SNAKE_BLOCK
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = SNAKE_BLOCK
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -SNAKE_BLOCK
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = SNAKE_BLOCK
                    x_change = 0

        # движение змейки
        x += x_change
        y += y_change

        # проход сквозь стены
        if x >= WIDTH:
            x = 0
        elif x < 0:
            x = WIDTH - SNAKE_BLOCK
        if y >= HEIGHT:
            y = 0
        elif y < 0:
            y = HEIGHT - SNAKE_BLOCK

        # обновление следа
        trail_timer += 1
        if trail_timer >= TRAIL_STEP:
            trail_timer = 0
            trail.append((x + SNAKE_BLOCK // 2, y + SNAKE_BLOCK // 2))
            if len(trail) > TRAIL_MAX_LEN:
                trail.pop(0)

        # логика призраков: спавн каждые 25 очков
        if score > 0 and score % GHOST_SPAWN_SCORE_STEP == 0:
            needed_ghosts = score // GHOST_SPAWN_SCORE_STEP
            if len(ghosts) < needed_ghosts:
                gx = random.randint(0, WIDTH)
                gy = random.randint(0, HEIGHT)
                ghosts.append({"x": gx, "y": gy})

        # движение призраков
        for ghost in ghosts:
            move_ghost_towards(ghost, x + SNAKE_BLOCK / 2, y + SNAKE_BLOCK / 2)

        # столкновение с призраками
        for ghost in ghosts:
            if check_collision_point_circle(
                x + SNAKE_BLOCK / 2,
                y + SNAKE_BLOCK / 2,
                ghost["x"],
                ghost["y"],
                10
            ):
                game_close = True

        # еда
        if abs(x - food_x) < SNAKE_BLOCK and abs(y - food_y) < SNAKE_BLOCK:
            score += 5
            food_x = random.randrange(0, WIDTH - SNAKE_BLOCK, SNAKE_BLOCK)
            food_y = random.randrange(0, HEIGHT - SNAKE_BLOCK, SNAKE_BLOCK)

        # обновление рекорда
        if score > highscore:
            highscore = score
            save_highscore(highscore)

        # ---------- ОТРИСОВКА ----------
        screen.fill(BLACK)
        draw_grid()

        # след
        draw_trail(trail)

        # еда
        draw_food(food_x, food_y)

        # призраки
        for ghost in ghosts:
            draw_ghost(ghost)

        # голова змейки
        draw_snake_head(x, y)

        # HUD
        score_text = font_small.render(f"Score: {score}", True, WHITE)
        hs_text = font_small.render(f"Highscore: {highscore}", True, YELLOW)
        screen.blit(score_text, (10, 10))
        screen.blit(hs_text, (10, 35))

        pygame.display.flip()

    return False


# ---------- ЗАПУСК ----------

def main():
    running = True
    while running:
        start = main_menu()
        if not start:
            break
        again = game_loop()
        if not again:
            break
    pygame.quit()


if __name__ == "__main__":
    main()

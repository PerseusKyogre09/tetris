import pygame
import random
import os

pygame.init()

#sizes
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
GAME_WIDTH = 300
BLOCK_SIZE = 30
GRID_WIDTH = GAME_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE
FPS = 60

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
DARK_GRAY = (50, 50, 50)
TETROMINO_COLORS = [CYAN, MAGENTA, YELLOW, ORANGE, GREEN]

TETROMINOES = [
    [[1, 1, 1, 1]],   
    [[1, 1, 1],
     [0, 1, 0]],
    [[1, 1, 0],
     [0, 1, 1]],
    [[0, 1, 1],
     [1, 1, 0]],
    [[1, 1],
     [1, 1]],
]

FONT = pygame.font.SysFont('comicsans', 30)

pygame.mixer.music.load('Assets/music.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(5.0)
rotate_sound = pygame.mixer.Sound('Assets/rotate.mp3')
lock_sound = pygame.mixer.Sound('Assets/lock.mp3')

# File to store the high score
HIGHSCORE_FILE = "highscore.txt"

# Helper function to load the high score
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r') as file:
            return int(file.read().strip())
    return 0

# Helper function to save the high score
def save_highscore(highscore):
    with open(HIGHSCORE_FILE, 'w') as file:
        file.write(str(highscore))

def create_grid():
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def draw_grid(screen, grid):
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if grid[row][col] == 0:
                color = DARK_GRAY
            else:
                color = TETROMINO_COLORS[grid[row][col] - 1]
            pygame.draw.rect(screen, color, pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
            pygame.draw.rect(screen, BLACK, pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = GRID_WIDTH // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        rotate_sound.play()

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

def check_collision(tetromino, grid, dx=0, dy=0):
    for row in range(len(tetromino.shape)):
        for col in range(len(tetromino.shape[row])):
            if tetromino.shape[row][col] == 1:
                new_x = tetromino.x + col + dx
                new_y = tetromino.y + row + dy
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or grid[new_y][new_x] != 0:
                    return True
    return False

def lock_tetromino(tetromino, grid):
    for row in range(len(tetromino.shape)):
        for col in range(len(tetromino.shape[row])):
            if tetromino.shape[row][col] == 1:
                grid[tetromino.y + row][tetromino.x + col] = tetromino.color + 1
    lock_sound.play()

def clear_rows(grid):
    full_rows = [i for i, row in enumerate(grid) if all(col != 0 for col in row)]
    for row in full_rows:
        del grid[row]
        grid.insert(0, [0] * GRID_WIDTH)
    return len(full_rows)

def draw_text(screen, text, position, color=WHITE):
    label = FONT.render(text, True, color)
    screen.blit(label, position)

def game_over(screen):
    pygame.mixer.music.stop()
    draw_text(screen, "Game Over!", (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 50), RED)
    draw_text(screen, "Press Enter to Play Again", (SCREEN_WIDTH // 4 - 30, SCREEN_HEIGHT // 2 + 10), RED)
    draw_text(screen, "Press Escape to Exit", (SCREEN_WIDTH // 4 - 30, SCREEN_HEIGHT // 2 + 50), RED)
    pygame.display.flip()

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    grid = create_grid()
    current_tetromino = Tetromino(random.choice(TETROMINOES), random.randint(0, len(TETROMINOES) - 1))
    fall_time = 0
    score = 0
    high_score = load_highscore()
    fall_speed = 500
    level = 1

    running = True
    game_over_state = False
    drop_speed = fall_speed
    last_fall_time = pygame.time.get_ticks()

    while running:
        screen.fill(DARK_GRAY)
        fall_time += clock.get_rawtime()
        clock.tick(FPS)

        if not game_over_state:
            if fall_time > drop_speed:
                if not check_collision(current_tetromino, grid, dy=1):
                    current_tetromino.move(0, 1)
                else:
                    if pygame.time.get_ticks() - last_fall_time > 500:  # Small delay before locking the tetromino
                        lock_tetromino(current_tetromino, grid)
                        cleared_rows = clear_rows(grid)
                        if cleared_rows:
                            score += cleared_rows * 10
                            level = score // 100 + 1
                            fall_speed = max(100, 500 - (level - 1) * 40)
                        current_tetromino = Tetromino(random.choice(TETROMINOES), random.randint(0, len(TETROMINOES) - 1))
                        if check_collision(current_tetromino, grid):
                            high_score = max(score, high_score)
                            save_highscore(high_score)
                            game_over(screen)
                            game_over_state = True
                    last_fall_time = pygame.time.get_ticks()

                fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game_over_state:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if not check_collision(current_tetromino, grid, dx=-1):
                            current_tetromino.move(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        if not check_collision(current_tetromino, grid, dx=1):
                            current_tetromino.move(1, 0)
                    if event.key == pygame.K_DOWN:
                        drop_speed = 50
                    if event.key == pygame.K_UP:
                        current_tetromino.rotate()
                        if check_collision(current_tetromino, grid):
                            current_tetromino.rotate()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        drop_speed = fall_speed
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game_over_state = False
                        grid = create_grid()
                        score = 0
                        current_tetromino = Tetromino(random.choice(TETROMINOES), random.randint(0, len(TETROMINOES) - 1))
                        pygame.mixer.music.play(-1)
                    if event.key == pygame.K_ESCAPE:
                        running = False

        draw_grid(screen, grid)

        for row in range(len(current_tetromino.shape)):
            for col in range(len(current_tetromino.shape[row])):
                if current_tetromino.shape[row][col] == 1:
                    pygame.draw.rect(screen, TETROMINO_COLORS[current_tetromino.color],
                                     pygame.Rect((current_tetromino.x + col) * BLOCK_SIZE,
                                                 (current_tetromino.y + row) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                    pygame.draw.rect(screen, BLACK, pygame.Rect((current_tetromino.x + col) * BLOCK_SIZE,
                                                                (current_tetromino.y + row) * BLOCK_SIZE, BLOCK_SIZE,
                                                                BLOCK_SIZE), 1)

        draw_text(screen, f"Score: {score}", (GAME_WIDTH + 10, 10))
        draw_text(screen, f"Highscore: {high_score}", (GAME_WIDTH + 10, 50))
        draw_text(screen, f"Level: {level}", (GAME_WIDTH + 10, 90))

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()

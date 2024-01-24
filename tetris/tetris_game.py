import pygame
import random

# Inicialização do Pygame
pygame.init()

# Configurações do jogo
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
FPS = 10

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Lista de peças possíveis
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()

        self.grid = [[0] * (WIDTH // BLOCK_SIZE) for _ in range(HEIGHT // BLOCK_SIZE)]
        self.current_piece = self.new_piece()

        self.score = 0 # TODO: não usar níveis, apenas pontos
        self.level = 1
        self.lines_cleared = 0
        self.speed = FPS

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.choice([RED, CYAN, MAGENTA, YELLOW, GREEN, BLUE, ORANGE])
        return {'shape': shape, 'color': color, 'x': WIDTH // BLOCK_SIZE // 2 - len(shape[0]) // 2, 'y': 0}

    def rotate_piece(self, shape, clockwise=True):
        if clockwise:
            return [[shape[j][i] for j in range(len(shape))] for i in range(len(shape[0]) - 1, -1, -1)]
        else:
            return [[shape[j][i] for j in range(len(shape) - 1, -1, -1)] for i in range(len(shape[0]))]

    def draw_score(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}  Level: {self.level}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

    def check_line_clear(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(row)]
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0] * (WIDTH // BLOCK_SIZE))

        lines_cleared = len(lines_to_clear)
        self.lines_cleared += lines_cleared

        # Atualiza a pontuação e o nível
        if lines_cleared > 0:
            self.score += lines_cleared * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            self.speed = FPS - (self.level - 1) * 2

    def draw_piece(self, piece):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, piece['color'],
                                     (piece['x'] * BLOCK_SIZE + j * BLOCK_SIZE,
                                      piece['y'] * BLOCK_SIZE + i * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))

    def draw_grid(self):
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, cell,
                                     (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def check_collision(self, piece):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell and (piece['y'] + i >= len(self.grid) or
                             piece['x'] + j < 0 or piece['x'] + j >= len(self.grid[0]) or
                             self.grid[piece['y'] + i][piece['x'] + j] != 0):
                    return True
        return False

    def merge_piece(self, piece):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[piece['y'] + i][piece['x'] + j] = piece['color']

    def check_line_clear(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(row)]
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0] * (WIDTH // BLOCK_SIZE))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and not self.check_collision({'shape': self.current_piece['shape'],
                                                                  'color': self.current_piece['color'],
                                                                  'x': self.current_piece['x'] - 1,
                                                                  'y': self.current_piece['y']}):
                self.current_piece['x'] -= 1

            if keys[pygame.K_RIGHT] and not self.check_collision({'shape': self.current_piece['shape'],
                                                                   'color': self.current_piece['color'],
                                                                   'x': self.current_piece['x'] + 1,
                                                                   'y': self.current_piece['y']}):
                self.current_piece['x'] += 1

            if keys[pygame.K_DOWN]:
                if not self.check_collision({'shape': self.current_piece['shape'],
                                             'color': self.current_piece['color'],
                                             'x': self.current_piece['x'],
                                             'y': self.current_piece['y'] + 1}):
                    self.current_piece['y'] += 1
                else:
                    self.merge_piece(self.current_piece)
                    self.check_line_clear()
                    self.current_piece = self.new_piece()

            if keys[pygame.K_SPACE]:
                # Tecla 'R' para girar a peça
                rotated_shape = self.rotate_piece(self.current_piece['shape'])
                if not self.check_collision({'shape': rotated_shape,
                                             'color': self.current_piece['color'],
                                             'x': self.current_piece['x'],
                                             'y': self.current_piece['y']}):
                    self.current_piece['shape'] = rotated_shape

            # Lógica para movimento automático para baixo
            if not self.check_collision({'shape': self.current_piece['shape'],
                                          'color': self.current_piece['color'],
                                          'x': self.current_piece['x'],
                                          'y': self.current_piece['y'] + 1}):
                self.current_piece['y'] += 1
            else:
                # Se houver colisão, a peça é fixada no tabuleiro e uma nova peça é gerada
                self.merge_piece(self.current_piece)
                self.check_line_clear()
                self.current_piece = self.new_piece()

                # Verifica se a nova peça colide imediatamente, indicando que o jogo terminou
                if self.check_collision(self.current_piece):
                    print("Game Over!")
                    pygame.quit()
                    quit()

            # Atualiza a tela
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_score()  # Adiciona a exibição da pontuação e do nível
            pygame.display.flip()

            # Limita a taxa de quadros
            self.clock.tick(self.speed)

if __name__ == "__main__":
    game = Tetris()
    game.run()
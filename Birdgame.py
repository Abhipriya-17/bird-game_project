# A simple Flappy Bird style game built with Pygame.
# To run this code, you'll need to have Pygame installed.
# You can install it by running: pip install pygame

import pygame
import random
import sys

# --- Constants ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
PIPE_WIDTH = 80
PIPE_GAP = 150
GRAVITY = 0.5
JUMP_STRENGTH = -10
FPS = 60

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 150, 0)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)

# --- Classes ---

class Bird:
    """Represents the bird player."""
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.size = 20
        self.velocity = 0

    def jump(self):
        """Applies an upward force (jump) to the bird."""
        self.velocity = JUMP_STRENGTH

    def move(self):
        """Applies gravity to the bird's velocity and updates its position."""
        self.velocity += GRAVITY
        self.y += self.velocity

    def get_rect(self):
        """Returns the bird's collision rectangle."""
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def draw(self, screen):
        """Draws the bird on the screen."""
        pygame.draw.circle(screen, YELLOW, (int(self.x + self.size/2), int(self.y + self.size/2)), self.size)
        pygame.draw.rect(screen, BLACK, self.get_rect(), 1) # border


class Pipe:
    """Represents a single pipe."""
    def __init__(self, x, gap_y):
        self.x = x
        self.gap_y = gap_y
        self.velocity = -4
        self.passed = False
        
    def move(self):
        """Moves the pipe horizontally."""
        self.x += self.velocity
        
    def off_screen(self):
        """Checks if the pipe is off the left side of the screen."""
        return self.x < -PIPE_WIDTH

    def get_upper_rect(self):
        """Returns the collision rectangle for the upper pipe."""
        return pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP // 2)

    def get_lower_rect(self):
        """Returns the collision rectangle for the lower pipe."""
        return pygame.Rect(self.x, self.gap_y + PIPE_GAP // 2, PIPE_WIDTH, SCREEN_HEIGHT)

    def draw(self, screen):
        """Draws the pipes on the screen."""
        # Draw upper pipe
        pygame.draw.rect(screen, GREEN, self.get_upper_rect())
        # Draw lower pipe
        pygame.draw.rect(screen, GREEN, self.get_lower_rect())


class Game:
    """Manages the main game loop and game state."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame Bird Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.reset_game()
        
    def reset_game(self):
        """Resets the game to its initial state."""
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.pipe_spawn_counter = 0

    def _handle_events(self):
        """Handles all Pygame events, including keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN and not self.game_over:
                if event.key == pygame.K_SPACE:
                    self.bird.jump()
            if event.type == pygame.KEYDOWN and self.game_over:
                if event.key == pygame.K_SPACE:
                    self.reset_game()

    def _check_collisions(self):
        """Checks for collisions between the bird and pipes or screen boundaries."""
        bird_rect = self.bird.get_rect()
        
        # Collision with pipes
        for pipe in self.pipes:
            if bird_rect.colliderect(pipe.get_upper_rect()) or \
               bird_rect.colliderect(pipe.get_lower_rect()):
                self.game_over = True
                
        # Collision with screen boundaries
        if bird_rect.top < 0 or bird_rect.bottom > SCREEN_HEIGHT:
            self.game_over = True

    def _manage_pipes(self):
        """Spawns new pipes and removes old ones."""
        self.pipe_spawn_counter += 1
        if self.pipe_spawn_counter > 90: # Spawn a new pipe every ~1.5 seconds at 60 FPS
            gap_y = random.randint(PIPE_GAP, SCREEN_HEIGHT - PIPE_GAP)
            self.pipes.append(Pipe(SCREEN_WIDTH, gap_y))
            self.pipe_spawn_counter = 0

        # Remove pipes that are off-screen and update score
        self.pipes = [pipe for pipe in self.pipes if not pipe.off_screen()]
        
        for pipe in self.pipes:
            if pipe.x + PIPE_WIDTH < self.bird.x and not pipe.passed:
                self.score += 1
                pipe.passed = True

    def _draw_elements(self):
        """Draws all game elements on the screen."""
        self.screen.fill(SKY_BLUE)
        self.bird.draw(self.screen)
        for pipe in self.pipes:
            pipe.draw(self.screen)
        self._draw_score()
        
    def _draw_score(self):
        """Draws the current score on the screen."""
        score_text = self.font.render(str(self.score), True, BLACK)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(score_text, score_rect)

    def _display_game_over(self):
        """Displays the game over message and waits for a restart."""
        game_over_text = self.font.render("Game Over!", True, BLACK)
        final_score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        restart_text = self.font.render("Press SPACE to Play Again", True, BLACK)

        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(final_score_text, final_score_rect)
        self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        
    def quit_game(self):
        """Quits the game and exits the application."""
        pygame.quit()
        sys.exit()

    def run(self):
        """The main game loop."""
        while True:
            self._handle_events()
            
            if not self.game_over:
                self.bird.move()
                for pipe in self.pipes:
                    pipe.move()
                self._manage_pipes()
                self._check_collisions()
                self._draw_elements()
            else:
                self._display_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)

# --- Main execution block ---
if __name__ == "__main__":
    game = Game()
    game.run()

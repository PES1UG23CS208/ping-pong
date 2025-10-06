import pygame
from .paddle import Paddle
from .ball import Ball

# Game Engine

WHITE = (255, 255, 255)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.paddle_sound = pygame.mixer.Sound("assets/paddle_hit.mp3")
        self.wall_sound = pygame.mixer.Sound("assets/wall_bounce.mp3")
        self.score_sound = pygame.mixer.Sound("assets/score.mp3")
        self.winning_score = 5  # Default winning score

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def update(self):
        prev_vx = self.ball.velocity_x
        prev_vy = self.ball.velocity_y

        # Move ball
        self.ball.move()

        # Paddle collision check (after moving the ball)
        if self.ball.rect().colliderect(self.player.rect()) or self.ball.rect().colliderect(self.ai.rect()):
            self.ball.velocity_x *= -1
            self.paddle_sound.play()

        # Wall collision (top/bottom)
        if self.ball.y <= 0 or self.ball.y + self.ball.height >= self.height:
            self.ball.velocity_y *= -1
            self.wall_sound.play()

        # Scoring
        if self.ball.x < 0:
            self.ai_score += 1
            self.score_sound.play()
            self.ball.reset()
        elif self.ball.x > self.width:
            self.player_score += 1
            self.score_sound.play()
            self.ball.reset()

        self.ai.auto_track(self.ball, self.height)

    def render(self, screen):
        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

        # Draw score
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width//4, 20))
        screen.blit(ai_text, (self.width * 3//4, 20))

    def show_replay_menu(self, screen):
        font = pygame.font.SysFont(None, 48)
        options = [
            "Press 3 for Best of 3",
            "Press 5 for Best of 5",
            "Press 7 for Best of 7",
            "Press ESC to Exit"
        ]
        screen.fill((0, 0, 0))
        for i, option in enumerate(options):
            text = font.render(option, True, (255, 255, 255))
            rect = text.get_rect(center=(self.width // 2, 200 + i * 60))
            screen.blit(text, rect)
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_3:
                        self.winning_score = 2  # Best of 3 (first to 2)
                        self.reset_game()
                        return
                    elif event.key == pygame.K_5:
                        self.winning_score = 3  # Best of 5 (first to 3)
                        self.reset_game()
                        return
                    elif event.key == pygame.K_7:
                        self.winning_score = 4  # Best of 7 (first to 4)
                        self.reset_game()
                        return
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

    def reset_game(self):
        self.player_score = 0
        self.ai_score = 0
        self.ball.reset()
        # Optionally reset paddle positions here

    def check_game_over(self, screen):
        font = pygame.font.SysFont(None, 72)
        winner = None
        if self.player_score >= getattr(self, 'winning_score', 5):
            winner = "Player Wins!"
        elif self.ai_score >= getattr(self, 'winning_score', 5):
            winner = "AI Wins!"

        if winner:
            text = font.render(winner, True, (255, 255, 255))
            rect = text.get_rect(center=(self.width // 2, self.height // 2))
            screen.blit(text, rect)
            pygame.display.flip()
            pygame.time.delay(1500)
            self.show_replay_menu(screen)

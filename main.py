import asyncio
import math
import random
import sys
import pygame

# Star Catcher - browser-ready Pygame project using Pygbag
# Controls:
# Desktop: LEFT / RIGHT arrows or A / D
# Mobile/browser: tap/click left or right side of the canvas
# Goal: catch falling stars, avoid red meteors, survive 60 seconds.

WIDTH, HEIGHT = 800, 450
FPS = 60

PLAYER_W, PLAYER_H = 80, 24
PLAYER_SPEED = 8

STAR_RADIUS = 12
METEOR_RADIUS = 16

GAME_SECONDS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Star Catcher")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 52, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 18)

BG = (15, 18, 35)
WHITE = (245, 245, 245)
YELLOW = (255, 222, 89)
BLUE = (85, 170, 255)
RED = (255, 85, 85)
GREEN = (98, 230, 140)
GRAY = (150, 160, 180)


def clamp(value, low, high):
    return max(low, min(high, value))


class FallingObject:
    def __init__(self, kind):
        self.kind = kind  # "star" or "meteor"
        self.x = random.randint(30, WIDTH - 30)
        self.y = -30
        self.speed = random.uniform(2.6, 5.8) if kind == "star" else random.uniform(3.8, 7.2)
        self.radius = STAR_RADIUS if kind == "star" else METEOR_RADIUS
        self.angle = random.random() * math.tau

    def update(self):
        self.y += self.speed
        self.angle += 0.08

    def draw(self, surface):
        if self.kind == "star":
            draw_star(surface, self.x, self.y, self.radius, YELLOW, self.angle)
        else:
            pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, (160, 40, 40), (int(self.x - 5), int(self.y - 5)), 5)

    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)


def draw_star(surface, x, y, radius, color, angle=0):
    points = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * 0.45
        a = angle + i * math.pi / 5
        points.append((x + math.cos(a) * r, y + math.sin(a) * r))
    pygame.draw.polygon(surface, color, points)


def draw_text(surface, text, font, color, x, y, center=False):
    label = font.render(text, True, color)
    rect = label.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(label, rect)


def reset_game():
    return {
        "player_x": WIDTH // 2 - PLAYER_W // 2,
        "objects": [],
        "score": 0,
        "lives": 3,
        "spawn_timer": 0,
        "start_ticks": pygame.time.get_ticks(),
        "state": "playing",
    }


def draw_background(surface):
    surface.fill(BG)
    # simple animated-looking star field based on time
    now = pygame.time.get_ticks() / 1000
    for i in range(45):
        x = (i * 97) % WIDTH
        y = (i * 53 + int(now * (10 + i % 4))) % HEIGHT
        brightness = 120 + (i * 23) % 100
        pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), 1)


def draw_hud(surface, score, lives, seconds_left):
    draw_text(surface, f"Score: {score}", FONT, WHITE, 16, 12)
    draw_text(surface, f"Lives: {lives}", FONT, WHITE, 16, 42)
    draw_text(surface, f"Time: {seconds_left}s", FONT, WHITE, WIDTH - 130, 12)
    draw_text(surface, "Catch stars. Avoid meteors.", SMALL_FONT, GRAY, WIDTH // 2, 18, center=True)


async def main():
    game = reset_game()
    running = True

    while running:
        dt = clock.tick(FPS)
        seconds_played = (pygame.time.get_ticks() - game["start_ticks"]) // 1000
        seconds_left = max(0, GAME_SECONDS - seconds_played)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game["state"] != "playing" and event.key == pygame.K_SPACE:
                    game = reset_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game["state"] != "playing":
                    game = reset_game()

        keys = pygame.key.get_pressed()

        if game["state"] == "playing":
            # Keyboard controls
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                game["player_x"] -= PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                game["player_x"] += PLAYER_SPEED

            # Mouse/touch controls for browser/mobile
            if pygame.mouse.get_pressed()[0]:
                mx, _ = pygame.mouse.get_pos()
                if mx < WIDTH / 2:
                    game["player_x"] -= PLAYER_SPEED
                else:
                    game["player_x"] += PLAYER_SPEED

            game["player_x"] = clamp(game["player_x"], 0, WIDTH - PLAYER_W)
            player_rect = pygame.Rect(game["player_x"], HEIGHT - 55, PLAYER_W, PLAYER_H)

            # Spawn objects
            game["spawn_timer"] += dt
            spawn_delay = max(430, 900 - game["score"] * 8)
            if game["spawn_timer"] > spawn_delay:
                kind = "meteor" if random.random() < 0.28 else "star"
                game["objects"].append(FallingObject(kind))
                game["spawn_timer"] = 0

            # Update objects
            for obj in list(game["objects"]):
                obj.update()

                if obj.rect().colliderect(player_rect):
                    if obj.kind == "star":
                        game["score"] += 1
                    else:
                        game["lives"] -= 1
                    game["objects"].remove(obj)

                elif obj.y > HEIGHT + 40:
                    game["objects"].remove(obj)

            if game["lives"] <= 0:
                game["state"] = "lost"

            if seconds_left <= 0:
                game["state"] = "won"

        draw_background(screen)

        for obj in game["objects"]:
            obj.draw(screen)

        # Player basket
        player_rect = pygame.Rect(game["player_x"], HEIGHT - 55, PLAYER_W, PLAYER_H)
        pygame.draw.rect(screen, BLUE, player_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, player_rect, 2, border_radius=10)

        draw_hud(screen, game["score"], game["lives"], seconds_left)

        if game["state"] == "won":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "You Win!", BIG_FONT, GREEN, WIDTH // 2, HEIGHT // 2 - 60, center=True)
            draw_text(screen, f"Final Score: {game['score']}", FONT, WHITE, WIDTH // 2, HEIGHT // 2, center=True)
            draw_text(screen, "Press SPACE or click to play again", FONT, WHITE, WIDTH // 2, HEIGHT // 2 + 45, center=True)

        elif game["state"] == "lost":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "Game Over", BIG_FONT, RED, WIDTH // 2, HEIGHT // 2 - 60, center=True)
            draw_text(screen, f"Final Score: {game['score']}", FONT, WHITE, WIDTH // 2, HEIGHT // 2, center=True)
            draw_text(screen, "Press SPACE or click to restart", FONT, WHITE, WIDTH // 2, HEIGHT // 2 + 45, center=True)

        pygame.display.flip()

        # Required by Pygbag/WebAssembly so the browser event loop stays responsive.
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())

import pygame
import random
import math
import json
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    LEVEL_UP = 3
    GAME_OVER = 4
    SHOP = 5

@dataclass
class PlayerStats:
    level: int = 1
    experience: int = 0
    health: int = 100
    max_health: int = 100
    damage: int = 10
    fire_rate: int = 5
    speed: int = 5
    coins: int = 0
    
    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.damage += 5
        self.experience = 0

class Bullet:
    def __init__(self, x, y, direction=(0, -1), speed=10, damage=10):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.rect = pygame.Rect(x-2, y-2, 4, 4)
    
    def update(self):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        self.rect.center = (self.x, self.y)
    
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 3)

class Mushroom:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 4
        self.max_health = 4
        self.rect = pygame.Rect(x, y, 20, 20)
        self.poisoned = False
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        color = PURPLE if self.poisoned else GREEN
        alpha = int(255 * (self.health / self.max_health))
        surface = pygame.Surface((20, 20))
        surface.set_alpha(alpha)
        surface.fill(color)
        screen.blit(surface, (self.x, self.y))

class CentipedeSegment:
    def __init__(self, x, y, is_head=False):
        self.x = x
        self.y = y
        self.is_head = is_head
        self.health = 2 if is_head else 1
        self.rect = pygame.Rect(x, y, 15, 15)
        self.speed = 2
        self.direction = 1  # 1 for right, -1 for left
        self.moving_down = False
    
    def update(self, mushrooms):
        if self.moving_down:
            self.y += self.speed
            if self.y % 20 == 0:  # Moved down one row
                self.moving_down = False
                self.direction *= -1
        else:
            self.x += self.direction * self.speed
            
            # Check boundaries and mushroom collisions
            if self.x <= 0 or self.x >= SCREEN_WIDTH - 15:
                self.moving_down = True
            else:
                # Check mushroom collision
                for mushroom in mushrooms:
                    if self.rect.colliderect(mushroom.rect):
                        self.moving_down = True
                        break
        
        self.rect.center = (self.x, self.y)
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        color = RED if self.is_head else ORANGE
        pygame.draw.rect(screen, color, self.rect)
        if self.is_head:
            pygame.draw.circle(screen, WHITE, (self.x + 7, self.y + 5), 2)

class Spider:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3
        self.health = 3
        self.rect = pygame.Rect(x, y, 12, 12)
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.change_direction_timer = 0
    
    def update(self, mushrooms):
        self.change_direction_timer += 1
        if self.change_direction_timer > 30:
            self.direction_x = random.choice([-1, 1])
            self.direction_y = random.choice([-1, 1])
            self.change_direction_timer = 0
        
        self.x += self.direction_x * self.speed
        self.y += self.direction_y * self.speed
        
        # Bounce off walls
        if self.x <= 0 or self.x >= SCREEN_WIDTH - 12:
            self.direction_x *= -1
        if self.y <= SCREEN_HEIGHT // 2 or self.y >= SCREEN_HEIGHT - 12:
            self.direction_y *= -1
        
        self.rect.center = (self.x, self.y)
        
        # Eat mushrooms
        for mushroom in mushrooms[:]:
            if self.rect.colliderect(mushroom.rect):
                mushrooms.remove(mushroom)
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), 6)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 20, 20)
        self.fire_timer = 0
        self.stats = PlayerStats()
    
    def update(self, keys):
        # Movement
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.stats.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - 20:
            self.x += self.stats.speed
        if keys[pygame.K_UP] and self.y > SCREEN_HEIGHT // 2:
            self.y -= self.stats.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - 20:
            self.y += self.stats.speed
        
        self.rect.center = (self.x, self.y)
        
        if self.fire_timer > 0:
            self.fire_timer -= 1
    
    def can_fire(self):
        return self.fire_timer <= 0
    
    def fire(self):
        if self.can_fire():
            self.fire_timer = max(1, 10 - self.stats.fire_rate)
            return Bullet(self.x, self.y - 10, damage=self.stats.damage)
        return None
    
    def take_damage(self, damage):
        self.stats.health -= damage
        return self.stats.health <= 0
    
    def gain_experience(self, exp):
        self.stats.experience += exp
        exp_needed = self.stats.level * 100
        if self.stats.experience >= exp_needed:
            self.stats.level_up()
            return True
        return False
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Centipede Roguelike")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.state = GameState.MENU
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.bullets = []
        self.mushrooms = []
        self.centipede_segments = []
        self.spiders = []
        
        self.level = 1
        self.score = 0
        self.wave_timer = 0
        self.spawn_timer = 0
        
        self.generate_level()
    
    def generate_level(self):
        """Generate a new level with procedural elements"""
        self.mushrooms.clear()
        self.centipede_segments.clear()
        self.spiders.clear()
        
        # Generate random mushroom field
        mushroom_count = 30 + (self.level * 5)
        for _ in range(mushroom_count):
            x = random.randint(0, SCREEN_WIDTH - 20)
            y = random.randint(50, SCREEN_HEIGHT // 2)
            # Snap to grid
            x = (x // 20) * 20
            y = (y // 20) * 20
            
            # Don't place mushrooms too close to player start
            if abs(x - SCREEN_WIDTH // 2) > 100 or abs(y - (SCREEN_HEIGHT - 50)) > 100:
                self.mushrooms.append(Mushroom(x, y))
        
        # Create centipede
        segment_count = 8 + (self.level // 2)
        for i in range(segment_count):
            x = 50 + (i * 20)
            y = 30
            is_head = (i == 0)
            self.centipede_segments.append(CentipedeSegment(x, y, is_head))
        
        # Spawn spiders based on level
        spider_count = min(3, 1 + (self.level // 3))
        for _ in range(spider_count):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - 100)
            self.spiders.append(Spider(x, y))
    
    def handle_collisions(self):
        # Bullet vs Mushroom
        for bullet in self.bullets[:]:
            for mushroom in self.mushrooms[:]:
                if bullet.rect.colliderect(mushroom.rect):
                    if mushroom.take_damage(bullet.damage):
                        self.mushrooms.remove(mushroom)
                        self.score += 10
                        self.player.stats.coins += 1
                    self.bullets.remove(bullet)
                    break
        
        # Bullet vs Centipede
        for bullet in self.bullets[:]:
            for segment in self.centipede_segments[:]:
                if bullet.rect.colliderect(segment.rect):
                    if segment.take_damage(bullet.damage):
                        self.centipede_segments.remove(segment)
                        exp_gain = 50 if segment.is_head else 25
                        self.score += exp_gain
                        self.player.stats.coins += 2 if segment.is_head else 1
                        if self.player.gain_experience(exp_gain):
                            self.state = GameState.LEVEL_UP
                        
                        # Create mushroom where segment died
                        mushroom_x = (segment.x // 20) * 20
                        mushroom_y = (segment.y // 20) * 20
                        self.mushrooms.append(Mushroom(mushroom_x, mushroom_y))
                    
                    self.bullets.remove(bullet)
                    break
        
        # Bullet vs Spider
        for bullet in self.bullets[:]:
            for spider in self.spiders[:]:
                if bullet.rect.colliderect(spider.rect):
                    if spider.take_damage(bullet.damage):
                        self.spiders.remove(spider)
                        self.score += 100
                        self.player.stats.coins += 3
                        if self.player.gain_experience(75):
                            self.state = GameState.LEVEL_UP
                    self.bullets.remove(bullet)
                    break
        
        # Player vs Centipede
        for segment in self.centipede_segments:
            if self.player.rect.colliderect(segment.rect):
                if self.player.take_damage(20):
                    self.state = GameState.GAME_OVER
        
        # Player vs Spider
        for spider in self.spiders:
            if self.player.rect.colliderect(spider.rect):
                if self.player.take_damage(15):
                    self.state = GameState.GAME_OVER
    
    def update_game(self, keys, events):
        if self.state == GameState.PLAYING:
            self.player.update(keys)
            
            # Shooting
            if keys[pygame.K_SPACE]:
                bullet = self.player.fire()
                if bullet:
                    self.bullets.append(bullet)
            
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.update()
                if bullet.y < 0 or bullet.y > SCREEN_HEIGHT:
                    self.bullets.remove(bullet)
            
            # Update centipede
            for segment in self.centipede_segments:
                segment.update(self.mushrooms)
            
            # Update spiders
            for spider in self.spiders:
                spider.update(self.mushrooms)
            
            self.handle_collisions()
            
            # Check win condition
            if not self.centipede_segments:
                self.level += 1
                self.generate_level()
            
            # Spawn new enemies periodically
            self.spawn_timer += 1
            if self.spawn_timer > 600:  # Every 10 seconds
                if len(self.spiders) < 3:
                    x = random.randint(50, SCREEN_WIDTH - 50)
                    y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - 100)
                    self.spiders.append(Spider(x, y))
                self.spawn_timer = 0
        
        elif self.state == GameState.LEVEL_UP:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.player.stats.max_health += 20
                        self.player.stats.health = self.player.stats.max_health
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_2:
                        self.player.stats.damage += 10
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_3:
                        self.player.stats.fire_rate += 2
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_4:
                        self.player.stats.speed += 2
                        self.state = GameState.PLAYING
        
        elif self.state == GameState.MENU:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_s:
                        self.state = GameState.SHOP
        
        elif self.state == GameState.SHOP:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                    elif event.key == pygame.K_1 and self.player.stats.coins >= 10:
                        self.player.stats.coins -= 10
                        self.player.stats.max_health += 25
                        self.player.stats.health = self.player.stats.max_health
                    elif event.key == pygame.K_2 and self.player.stats.coins >= 15:
                        self.player.stats.coins -= 15
                        self.player.stats.damage += 8
                    elif event.key == pygame.K_3 and self.player.stats.coins >= 12:
                        self.player.stats.coins -= 12
                        self.player.stats.fire_rate += 3
        
        elif self.state == GameState.GAME_OVER:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()  # Restart game
    
    def draw_hud(self):
        # Health bar
        health_ratio = self.player.stats.health / self.player.stats.max_health
        health_width = int(200 * health_ratio)
        pygame.draw.rect(self.screen, RED, (10, 10, 200, 20))
        pygame.draw.rect(self.screen, GREEN, (10, 10, health_width, 20))
        
        # Stats
        stats_text = [
            f"Level: {self.player.stats.level}",
            f"Score: {self.score}",
            f"Coins: {self.player.stats.coins}",
            f"Wave: {self.level}",
            f"HP: {self.player.stats.health}/{self.player.stats.max_health}"
        ]
        
        for i, text in enumerate(stats_text):
            surface = self.small_font.render(text, True, WHITE)
            self.screen.blit(surface, (10, 40 + i * 25))
        
        # Experience bar
        exp_needed = self.player.stats.level * 100
        exp_ratio = self.player.stats.experience / exp_needed
        exp_width = int(200 * exp_ratio)
        pygame.draw.rect(self.screen, GRAY, (10, 180, 200, 15))
        pygame.draw.rect(self.screen, BLUE, (10, 180, exp_width, 15))
    
    def draw_menu(self):
        title = self.font.render("CENTIPEDE ROGUELIKE", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        
        instructions = [
            "SPACE - Start Game",
            "S - Shop",
            "",
            "Controls:",
            "Arrow Keys - Move",
            "Space - Shoot"
        ]
        
        for i, text in enumerate(instructions):
            surface = self.small_font.render(text, True, WHITE)
            self.screen.blit(surface, (SCREEN_WIDTH//2 - surface.get_width()//2, 300 + i * 30))
    
    def draw_level_up(self):
        title = self.font.render("LEVEL UP!", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        
        options = [
            "1 - Increase Health (+20 HP)",
            "2 - Increase Damage (+10 DMG)",
            "3 - Increase Fire Rate (+2)",
            "4 - Increase Speed (+2)"
        ]
        
        for i, text in enumerate(options):
            surface = self.small_font.render(text, True, WHITE)
            self.screen.blit(surface, (SCREEN_WIDTH//2 - surface.get_width()//2, 300 + i * 40))
    
    def draw_shop(self):
        title = self.font.render("SHOP", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        coins_text = f"Coins: {self.player.stats.coins}"
        surface = self.small_font.render(coins_text, True, WHITE)
        self.screen.blit(surface, (SCREEN_WIDTH//2 - surface.get_width()//2, 150))
        
        items = [
            "1 - Health Boost (10 coins) - +25 HP",
            "2 - Damage Boost (15 coins) - +8 DMG",
            "3 - Fire Rate Boost (12 coins) - +3 Rate",
            "",
            "ESC - Back to Menu"
        ]
        
        for i, text in enumerate(items):
            color = WHITE
            if i < 3:  # Check if player can afford
                costs = [10, 15, 12]
                if self.player.stats.coins < costs[i]:
                    color = GRAY
            
            surface = self.small_font.render(text, True, color)
            self.screen.blit(surface, (SCREEN_WIDTH//2 - surface.get_width()//2, 200 + i * 40))
    
    def draw_game_over(self):
        title = self.font.render("GAME OVER", True, RED)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 300))
        
        score_text = f"Final Score: {self.score}"
        surface = self.small_font.render(score_text, True, WHITE)
        self.screen.blit(surface, (SCREEN_WIDTH//2 - surface.get_width()//2, 350))
        
        restart_text = "Press R to Restart"
        surface = self.small_font.render(restart_text, True, WHITE)
        self.screen.blit(surface, (SCREEN_WIDTH//2 - surface.get_width()//2, 400))
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == GameState.PLAYING:
            # Draw game objects
            for mushroom in self.mushrooms:
                mushroom.draw(self.screen)
            
            for segment in self.centipede_segments:
                segment.draw(self.screen)
            
            for spider in self.spiders:
                spider.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            self.player.draw(self.screen)
            self.draw_hud()
            
        elif self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.LEVEL_UP:
            self.draw_level_up()
        elif self.state == GameState.SHOP:
            self.draw_shop()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            
            keys = pygame.key.get_pressed()
            self.update_game(keys, events)
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

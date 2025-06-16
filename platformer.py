import pygame
  import asyncio
  import platform
  import random

  # Game constants
  WIDTH, HEIGHT = 800, 600
  FPS = 60
  PLAYER_SIZE = 40
  ENEMY_SIZE = 30
  COIN_SIZE = 20
  GRAVITY = 0.8
  JUMP_FORCE = -15
  PLAYER_SPEED = 5
  MAX_JUMPS = 2
  ENEMY_SPEED = 3
  BLUE = (0, 0, 255)
  GREEN = (0, 200, 0)
  RED = (255, 0, 0)
  YELLOW = (255, 255, 0)

  # Initialize pygame
  pygame.init()
  screen = pygame.display.set_mode((WIDTH, HEIGHT))
  pygame.display.set_caption("Ultimate Platformer")
  clock = pygame.time.Clock()
  font = pygame.font.SysFont("Arial", 24)

  # Player class
  class Player:
      def __init__(self, x, y):
          self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
          self.vy = 0
          self.on_ground = False
          self.jump_count = 0

      def update(self, keys, platforms):
          if keys[pygame.K_LEFT]:
              self.rect.x -= PLAYER_SPEED
          if keys[pygame.K_RIGHT]:
              self.rect.x += PLAYER_SPEED
          self.vy += GRAVITY
          self.rect.y += self.vy
          self.on_ground = False
          for platform in platforms:
              if self.rect.colliderect(platform.rect) and self.vy > 0:
                  self.rect.bottom = platform.rect.top
                  self.vy = 0
                  self.on_ground = True
                  self.jump_count = 0
          if keys[pygame.K_SPACE] and self.jump_count < MAX_JUMPS:
              self.vy = JUMP_FORCE
              self.on_ground = False
              self.jump_count += 1
          self.rect.x = max(0, min(self.rect.x, WIDTH - PLAYER_SIZE))

      def draw(self):
          pygame.draw.circle(screen, BLUE, self.rect.center, PLAYER_SIZE // 2)

  # Platform class
  class Platform:
      def __init__(self, x, y, width, height):
          self.rect = pygame.Rect(x, y, width, height)

      def draw(self):
          pygame.draw.rect(screen, GREEN, self.rect)

  # Enemy class
  class Enemy:
      def __init__(self, x, y, min_x, max_x, initial_vx):
          self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
          self.min_x = min_x
          self.max_x = max_x
          self.vx = initial_vx

      def update(self):
          self.rect.x += self.vx
          if self.rect.left < self.min_x or self.rect.right > self.max_x:
              self.vx = -self.vx

      def draw(self):
          pygame.draw.rect(screen, RED, self.rect)

  # Coin class
  class Coin:
      def __init__(self, x, y):
          self.rect = pygame.Rect(x, y, COIN_SIZE, COIN_SIZE)

      def draw(self):
          pygame.draw.circle(screen, YELLOW, self.rect.center, COIN_SIZE // 2)

  # Game setup
  def setup():
      global player, platforms, enemies, coins, game_over
      player = Player(100, HEIGHT - 100)
      platforms = [
          Platform(0, HEIGHT - 20, WIDTH, 20),
          Platform(200, HEIGHT - 150, 100, 20),
          Platform(400, HEIGHT - 250, 100, 20)
      ]
      enemies = [
          Enemy(250, HEIGHT - 50, 200, 300, ENEMY_SPEED),
          Enemy(450, HEIGHT - 280, 400, 500, -ENEMY_SPEED)
      ]
      coins = [
          Coin(250, HEIGHT - 200),
          Coin(450, HEIGHT - 300)
      ]
      game_over = False

  # Game loop
  def update_loop():
      global game_over, coins
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              return False
          if event.type == pygame.KEYDOWN and game_over and event.key == pygame.K_r:
              setup()
      if not game_over:
          keys = pygame.key.get_pressed()
          player.update(keys, platforms)
          for enemy in enemies:
              enemy.update()
              if player.rect.colliderect(enemy.rect):
                  game_over = True
          coins_to_remove = []
          for coin in coins:
              if player.rect.colliderect(coin.rect):
                  coins_to_remove.append(coin)
          for coin in coins_to_remove:
              coins.remove(coin)
          if not coins:
              game_over = True
      screen.fill((0, 0, 0))
      for platform in platforms:
          platform.draw()
      for enemy in enemies:
          enemy.draw()
      for coin in coins:
          coin.draw()
      player.draw()
      if game_over:
          if not coins:
              text = font.render("You Win! Press R to Restart", True, (255, 255, 255))
          else:
              text = font.render("Game Over! Press R to Restart", True, (255, 255, 255))
          screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))
      pygame.display.flip()
      clock.tick(FPS)
      return True

  # Main async loop
  async def main():
      setup()
      running = True
      while running:
          running = update_loop()
          await asyncio.sleep(1.0 / FPS)

  if platform.system() == "Emscripten":
      asyncio.ensure_future(main())
  else:
      if __name__ == "__main__":
          asyncio.run(main())
import pygame
  import asyncio
  import platform
  import numpy as np
  import math
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
  SPRINT_MULTIPLIER = 1.5
  MAX_JUMPS = 2
  ENEMY_SPEED = 3
  MAX_LIVES = 3
  WORLD_WIDTH = 2400
  SHAKE_DURATION = 10
  SHAKE_MAGNITUDE = 5
  SKY_TOP = (100, 150, 255)
  SKY_BOTTOM = (50, 100, 200)
  BLUE = (0, 0, 255)
  SPRINT_COLOR = (100, 100, 255)
  GREEN = (0, 200, 0)
  GLOW_GREEN = (50, 255, 50)
  RED = (255, 0, 0)
  FLASH_RED = (255, 100, 100)
  YELLOW = (255, 255, 0)
  WHITE = (255, 255, 255)

  # Initialize pygame
  pygame.init()
  screen = pygame.display.set_mode((WIDTH, HEIGHT))
  pygame.display.set_caption("Ultimate Platformer")
  clock = pygame.time.Clock()
  font = pygame.font.SysFont("arial", 24)

  # Sound generation
  def create_sound(frequency, duration, sample_rate=44100):
      t = np.linspace(0, duration, int(sample_rate * duration), False)
      wave = 0.1 * np.sin(2 * np.pi * frequency * t)
      wave += 0.05 * np.sin(2 * np.pi * (frequency * 1.5) * t)
      stereo_wave = np.array([wave, wave]).T
      return pygame.sndarray.make_sound((stereo_wave * 32767).astype(np.int16))

  coin_sound = create_sound(880, 0.2)

  # Player class
  class Player:
      def __init__(self, x, y):
          self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
          self.vy = 0
          self.on_ground = False
          self.jump_count = 0
          self.animation_time = 0
          self.trail = []
          self.color = BLUE

      def update(self, keys, platforms):
          speed = PLAYER_SPEED * (SPRINT_MULTIPLIER if keys[pygame.K_LSHIFT] else 1)
          self.color = SPRINT_COLOR if keys[pygame.K_LSHIFT] else BLUE
          if keys[pygame.K_LEFT]:
              self.rect.x -= speed
          if keys[pygame.K_RIGHT]:
              self.rect.x += speed
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
          self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - PLAYER_SIZE))
          if keys[pygame.K_LSHIFT]:
              self.trail.append((self.rect.center, self.animation_time))
              if len(self.trail) > 6:
                  self.trail.pop(0)
          self.animation_time += 1

      def draw(self, camera, offset):
          center = camera.apply(self).center
          center = (center[0] + offset[0], center[1] + offset[1])
          for pos, time in self.trail:
              age = (self.animation_time - time) / 20
              if age < 1:
                  alpha_size = int(PLAYER_SIZE * (1 - age) * 0.5)
                  trail_center = (pos[0] - camera.rect.x + offset[0], pos[1] + offset[1])
                  trail_color = (
                      min(255, int(self.color[0])),
                      min(255, int(self.color[1])),
                      min(255, int(self.color[2]))
                  )
                  pygame.draw.circle(screen, trail_color, trail_center, alpha_size // 2)
          pygame.draw.circle(screen, self.color, center, PLAYER_SIZE // 2)
          pygame.draw.circle(screen, (0, 0, 0), center, PLAYER_SIZE // 2, 2)

  # Platform class
  class Platform:
      def __init__(self, x, y, width, height):
          self.rect = pygame.Rect(x, y, width, height)
          self.animation_time = 0

      def draw(self, camera, offset):
          self.animation_time += 1
          t = 0.5 * (1 + math.sin(self.animation_time * 0.05))
          color = (
              int(GREEN[0] * (1 - t) + GLOW_GREEN[0] * t),
              int(GREEN[1] * (1 - t) + GLOW_GREEN[1] * t),
              int(GREEN[2] * (1 - t) + GLOW_GREEN[2] * t)
          )
          rect = camera.apply(self)
          rect.x += offset[0]
          rect.y += offset[1]
          pygame.draw.rect(screen, color, rect)
          pygame.draw.rect(screen, (0, 100, 0), rect, 1)

  # Enemy class
  class Enemy:
      def __init__(self, x, y, min_x, max_x, vx):
          self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
          self.min_x = min_x
          self.max_x = max_x
          self.vx = vx
          self.animation_time = 0

      def update(self):
          self.vx = self.vx
          self.rect.x += self.vx
          if self.rect.left < self.min_x or self.rect.right > self.max_x:
              self.vx = -self.vx
          self.animation_time += 1

      def draw(self, camera, offset, player):
          t = 0.5 * (1 + math.sin(self.animation_time * 0.2))
          size = int(ENEMY_SIZE * (1 + 0.05 * t))
          rect = camera.apply(self)
          rect.width = size
          rect.height = size
          rect.center = camera.apply(self).center
          rect.x += offset[0]
          rect.y += offset[1]
          dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
          color = FLASH_RED if dist < 150 else RED
          pygame.draw.rect(screen, color, rect)
          pygame.draw.rect(screen, (100, 0, 0), rect, 1)

  # Coin class
  class Coin:
      def __init__(self, x, y):
          self.rect = pygame.Rect(x, y, COIN_SIZE, COIN_SIZE)
          self.animation_time = 0

      def draw(self, camera, offset):
          self.animation_time += 1
          t = 0.5 * (1 + math.sin(self.animation_time * 0.3))
          size = int(COIN_SIZE * (0.8 + 0.2 * t))
          center = camera.apply(self).center
          center = (center[0] + offset[0], center[1] + offset[1])
          pygame.draw.circle(screen, YELLOW, center, size // 2)
          pygame.draw.circle(screen, (200, 200, 0), center, size // 2, 1)
          if self.animation_time % 30 < 15:
              for i in range(4):
                  angle = i * math.pi / 2 + self.animation_time * 0.1
                  sx = center[0] + math.cos(angle) * (size * 0.75)
                  sy = center[1] + math.sin(angle) * (size * 0.75)
                  pygame.draw.circle(screen, WHITE, (int(sx), int(sy)), 2)

  # Camera class
  class Camera:
      def __init__(self, width, height):
          self.rect = pygame.Rect(0, 0, width, height)

      def apply(self, entity):
          return pygame.Rect(entity.rect.x - self.rect.x, entity.rect.y, entity.rect.width, entity.rect.height)

      def update(self, target):
          self.rect.x = target.rect.centerx - WIDTH // 2
          self.rect.x = max(0, min(self.rect.x, WORLD_WIDTH - WIDTH))

  # Draw background
  def draw_background(t):
      for y in range(HEIGHT):
          r = y / HEIGHT
          color = (
              int(SKY_TOP[0] * (1 - r) + SKY_BOTTOM[0] * r),
              int(SKY_TOP[1] * (1 - r) + SKY_BOTTOM[1] * r),
              int(SKY_TOP[2] * (1 - r) + SKY_BOTTOM[2] * r)
          )
          pygame.draw.line(screen, color, (0, y), (WIDTH, y))
      random.seed(42)
      for _ in range(50):
          x = random.randrange(WIDTH)
          y = random.randrange(HEIGHT)
          b = random.uniform(0.6, 1.0)
          tw = 1 + 0.3 * math.sin(t * 0.02 + x * 0.01 + y * 0.01)
          c = int(255 * b * tw)
          c = max(0, min(255, c))
          pygame.draw.circle(screen, (c, c, c), (x, y), 1)

  # Generate level
  def generate_level():
      platforms = [Platform(0, HEIGHT - 50, WORLD_WIDTH, 50)]
      coins = []
      enemies = []
      num_platforms = random.randint(5, 10)
      for i in range(num_platforms):
          x = random.randint(200 + i * 200, 200 + (i + 1) * 200)
          y = random.randint(HEIGHT - 350, HEIGHT - 150)
          width = random.randint(100, 200)
          platforms.append(Platform(x, y, width, 20))
          if random.random() < 0.5:
              coins.append(Coin(x + width // 2 - COIN_SIZE // 2, y - COIN_SIZE - 30))
          if random.random() < 0.2 and i > 0:
              enemy_x = x + width // 2
              enemies.append(Enemy(enemy_x, y - ENEMY_SIZE, x, x + width, ENEMY_SPEED if random.choice([True, False]) else -ENEMY_SPEED))
      while len(coins) < 5:
          platform = random.choice(platforms[1:])
          x = random.randint(platform.rect.left, platform.rect.right - COIN_SIZE)
          coins.append(Coin(x, platform.rect.top - COIN_SIZE - 30))
      return platforms, coins, enemies

  # Game setup
  def setup():
      global player, platforms, enemies, coins, game_over, lives, score, animation_time, camera, shake_time, shake_offset
      player = Player(50, HEIGHT - 50)
      platforms, coins, enemies = generate_level()
      game_over = False
      lives = MAX_LIVES
      score = 0
      animation_time = 0
      camera = Camera(WIDTH, HEIGHT)
      shake_time = 0
      shake_offset = (0, 0)

  # Game loop
  def update_loop():
      global game_over, coins, lives, animation_time, score, shake_time, shake_offset
      for e in pygame.event.get():
          if e.type == pygame.QUIT:
              return False
          if e.type == pygame.KEYDOWN and game_over and e.key == pygame.K_r:
              setup()
      if not game_over:
          keys = pygame.key.get_pressed()
          player.update(keys, platforms)
          for enemy in enemies:
              enemy.update()
              if player.rect.colliderect(enemy.rect):
                  lives -= 1
                  player.rect.center = (50, HEIGHT - 50)
                  player.vy = 0
                  player.jump_count = 0
                  shake_time = SHAKE_DURATION
                  if lives <= 0:
                      game_over = True
          to_remove = []
          for coin in coins:
              if player.rect.colliderect(coin.rect):
                  to_remove.append(coin)
                  coin_sound.play()
                  score += 50
          for coin in to_remove:
              coins.remove(coin)
          if not coins:
              game_over = True
          camera.update(player)
      animation_time += 1
      if shake_time > 0:
          shake_offset = (random.randint(-SHAKE_MAGNITUDE, SHAKE_MAGNITUDE), random.randint(-SHAKE_MAGNITUDE, SHAKE_MAGNITUDE))
          shake_time -= 1
      else:
          shake_offset = (0, 0)
      draw_background(animation_time)
      for platform in platforms:
          platform.draw(camera, shake_offset)
      for enemy Игор in enemies:
          enemy.draw(camera, shake_offset, player)
      for coin in coins:
          coin.draw(camera, shake_offset)
      player.draw(camera, shake_offset)
      lives_text = font.render(f"Lives: {lives}", True, WHITE)
      score_text = font.render(f"Score: {score}", True, WHITE)
      screen.blit(lives_text, (10, 10))
      screen.blit(score_text, (10, 40))
      if game_over:
          if not coins:
              text = font.render("You Win! Press R to Restart", True, WHITE)
          else:
              text = font.render("Game Over! Press R to Restart", True, WHITE)
          screen.blit(text, (WIDTH//2 - 150, HEIGHT//2))
      pygame.display.flip()
      clock.tick(FPS)
      return True

  # Main async loop
  async def main():
      setup()
      running = True
      while running:
          running = await update_loop()
          await asyncio.sleep(1.0 / FPS)

  if platform.system() == "Emscripten":
      asyncio.ensure_future(main())
  else:
      if __name__ == "__main__":
          asyncio.run(main())
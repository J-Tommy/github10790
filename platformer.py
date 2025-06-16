import pygame
  import asyncio
  import platform

  # Game constants
  WIDTH, HEIGHT = 800, 600
  FPS = 60
  PLAYER_SIZE = 40
  GRAVITY = 0.8
  JUMP_FORCE = -15
  PLAYER_SPEED = 5
  MAX_JUMPS = 2
  BLUE = (0, 0, 255)
  GREEN = (0, 200, 0)

  # Initialize pygame
  pygame.init()
  screen = pygame.display.set_mode((WIDTH, HEIGHT))
  pygame.display.set_caption("Ultimate Platformer")
  clock = pygame.time.Clock()

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

  # Game setup
  def setup():
      global player, platforms
      player = Player(100, HEIGHT - 100)
      platforms = [
          Platform(0, HEIGHT - 20, WIDTH, 20),  # Ground
          Platform(200, HEIGHT - 150, 100, 20),
          Platform(400, HEIGHT - 250, 100, 20)
      ]

  # Game loop
  def update_loop():
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              return False
      keys = pygame.key.get_pressed()
      player.update(keys, platforms)
      screen.fill((0, 0, 0))
      for platform in platforms:
          platform.draw()
      player.draw()
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
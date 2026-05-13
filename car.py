import pygame

class Car:
    DEFAULT_SPEED = 5
    MIN_SPEED = 2
    MAX_SPEED = 15

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.direction = "up"
        self.speed = 0

        # Car image
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_car_shape()

    def _draw_car_shape(self):
        self.image.fill((0, 0, 0, 0))
        # Body
        pygame.draw.rect(self.image, (200, 0, 0), (0, 0, self.width, self.height))
        # Windows
        pygame.draw.rect(self.image, (100, 100, 200), (5, 5, 30, 15))
        # Wheels
        for x in [5, self.width-5]:
            for y in [5, self.height-5]:
                pygame.draw.circle(self.image, (50, 50, 50), (x, y), 8)

    def update(self, screen_width, screen_height):
        if self.speed == 0:
            return
        dx = dy = 0
        if self.direction == "up":
            dy = -self.speed
        elif self.direction == "down":
            dy = self.speed
        elif self.direction == "left":
            dx = -self.speed
        elif self.direction == "right":
            dx = self.speed

        new_x = self.x + dx
        new_y = self.y + dy
        self.x = max(0, min(screen_width - self.width, new_x))
        self.y = max(0, min(screen_height - self.height, new_y))

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
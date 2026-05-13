import pygame
import sys
import threading
from car import Car
from server import app, get_command, command_lock, current_command

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (40, 40, 40)
ROAD_COLOR = (80, 80, 80)
LANE_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)

def draw_road(screen):
    pygame.draw.rect(screen, ROAD_COLOR, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    # Dashed center line
    dash_len = 30
    gap = 20
    y = 0
    while y < SCREEN_HEIGHT:
        pygame.draw.rect(screen, LANE_COLOR, (SCREEN_WIDTH//2 - 5, y, 10, dash_len))
        y += dash_len + gap
    pygame.draw.line(screen, LANE_COLOR, (50, 0), (50, SCREEN_HEIGHT), 5)
    pygame.draw.line(screen, LANE_COLOR, (SCREEN_WIDTH-50, 0), (SCREEN_WIDTH-50, SCREEN_HEIGHT), 5)

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mobile Voice-Controlled Car")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    car = Car(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    last_command = "None"
    score = 0
    last_pos = (car.x, car.y)

    running = True
    while running:
        # Handle quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read command from Flask server (non-blocking)
        cmd = get_command()
        if cmd:
            last_command = cmd
            # Process movement commands
            if cmd == "forward":
                car.direction = "up"
                if car.speed == 0:
                    car.speed = Car.DEFAULT_SPEED
            elif cmd == "backward":
                car.direction = "down"
                if car.speed == 0:
                    car.speed = Car.DEFAULT_SPEED
            elif cmd == "left":
                car.direction = "left"
                if car.speed == 0:
                    car.speed = Car.DEFAULT_SPEED
            elif cmd == "right":
                car.direction = "right"
                if car.speed == 0:
                    car.speed = Car.DEFAULT_SPEED
            elif cmd == "stop":
                car.speed = 0
            elif cmd == "faster":
                car.speed = min(Car.MAX_SPEED, car.speed + 1)
            elif cmd == "slower":
                car.speed = max(Car.MIN_SPEED, car.speed - 1)
            # Clear command after processing to avoid repeat
            with command_lock:
                current_command["action"] = None

        # Update car
        car.update(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Update score (distance traveled)
        dx = car.x - last_pos[0]
        dy = car.y - last_pos[1]
        score += int((dx**2 + dy**2)**0.5)
        last_pos = (car.x, car.y)

        # Draw everything
        draw_road(screen)
        car.draw(screen)

        # UI
        speed_text = font.render(f"Speed: {car.speed}", True, TEXT_COLOR)
        cmd_text = font.render(f"Command: {last_command}", True, TEXT_COLOR)
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        hint = small_font.render("Connect mobile → http://<PC-IP>:5000", True, (200,200,200))
        screen.blit(speed_text, (10, 10))
        screen.blit(cmd_text, (10, 50))
        screen.blit(score_text, (10, 90))
        screen.blit(hint, (10, SCREEN_HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Start Flask server in a background thread
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000, 'threaded': True, 'debug': False}, daemon=True)
    flask_thread.start()
    print("Flask server started on port 5000. Mobile app can connect now.")
    # Run the game loop (main thread)
    run_game()
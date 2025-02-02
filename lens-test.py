import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()
width, height = 600, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Realistic DSLR Lens Model")
clock = pygame.time.Clock()

# Center of the lens
center = (width // 2, height // 2)

# Parameters for the iris (aperture) and focus.
# Both vary between 0.0 and 1.0:
#   - For iris_param, 1.0 = fully open (almost a perfect circle),
#     0.0 = nearly closed (more polygonal with rounded indents).
#   - For focus_param, 0.5 is centered; moving away simulates focus shift.
iris_param = 1.0
focus_param = 0.5

# Random target values and timing for smooth animations.
target_iris = random.uniform(0, 1)
target_focus = random.uniform(0, 1)
next_target_time = pygame.time.get_ticks() + random.randint(1500, 3000)

# Iris rotation (for a subtle mechanical spin)
iris_rotation = 0.0

# Constants for the iris shape
R_max = 240   # Radius when fully open
R_min = 150   # Effective radius when fully closed
num_blades = 7  # Simulated number of blades

def lerp(a, b, t):
    """Linearly interpolate between a and b by t."""
    return a + (b - a) * t

def draw_lens(screen, center, iris_param, focus_param, iris_rotation):
    # Draw the outer lens barrel.
    pygame.draw.circle(screen, (80, 80, 80), center, 250, 5)

    # Compute the base radius of the iris.
    # Fully open (iris_param = 1) yields a radius of R_max,
    # while fully closed (iris_param = 0) yields R_min.
    base_radius = lerp(R_max, R_min, 1 - iris_param)
    # Modulation amplitude increases as the iris closes.
    mod_ampl = lerp(0, 20, 1 - iris_param)

    # Build the smooth, modulated curve.
    points = []
    steps = 100
    for i in range(steps):
        # Compute angle around the circle (adding a rotation for dynamics).
        angle = 2 * math.pi * i / steps + iris_rotation
        # Modulate the radius: use a sinusoid with num_blades cycles.
        r = base_radius + mod_ampl * math.sin(num_blades * angle)
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(screen, (150, 150, 150), points)

    # Draw the focusing element.
    max_offset = 20  # Maximum horizontal shift (in pixels)
    offset_x = (focus_param - 0.5) * 2 * max_offset
    focus_center = (center[0] + offset_x, center[1])
    pygame.draw.circle(screen, (100, 100, 255), focus_center, 50)
    pygame.draw.circle(screen, (0, 0, 0), focus_center, 50, 3)

def draw_info(screen, iris_param, focus_param):
    """Display parameter values for visual feedback."""
    font = pygame.font.SysFont("Arial", 20)
    text1 = font.render(f"Aperture: {iris_param:.2f}", True, (255, 255, 255))
    text2 = font.render(f"Focus: {focus_param:.2f}", True, (255, 255, 255))
    screen.blit(text1, (10, 10))
    screen.blit(text2, (10, 35))

def update_parameters():
    """Smoothly update iris and focus parameters toward random targets."""
    global iris_param, focus_param, target_iris, target_focus, next_target_time
    current_time = pygame.time.get_ticks()
    iris_param += (target_iris - iris_param) * 0.02
    focus_param += (target_focus - focus_param) * 0.02
    if current_time >= next_target_time:
        target_iris = random.uniform(0, 1)
        target_focus = random.uniform(0, 1)
        next_target_time = current_time + random.randint(1500, 3000)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_parameters()
    iris_rotation += 0.01  # Update rotation for a subtle spin.

    screen.fill((0, 0, 0))
    draw_lens(screen, center, iris_param, focus_param, iris_rotation)
    draw_info(screen, iris_param, focus_param)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

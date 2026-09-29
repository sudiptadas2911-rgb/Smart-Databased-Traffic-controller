import pygame
import numpy as np
import sys

# --- 1. Traffic Logic & Backend Setup ---
YELLOW_TIME = 8.0
ALL_RED_TIME = 12.0
roads = np.array(['Road_A', 'Road_B', 'Road_C', 'Road_D'])

def get_priority_index(density, emergency_status):
    priority_score = density.astype(float)
    priority_score[emergency_status] = 9999.0  
    return np.argsort(priority_score)[::-1]

def calculate_green_times(density, total_traffic, threshold):
    if total_traffic == 0:
        return np.array([30.0, 30.0, 30.0, 30.0])
    return np.where(density >= threshold, 120.0, (density / threshold) * 120.0)

# --- 2. Pygame Configuration ---
pygame.init()
WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Traffic Controller - Corrected")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Trebuchet MS", 15, bold=True)
title_font = pygame.font.SysFont("Trebuchet MS", 20, bold=True)

COLOR_GRASS = (40, 115, 45)
COLOR_ROAD = (40, 40, 43)
COLOR_SIDEWALK = (150, 150, 150)
COLOR_SIDEWALK_EDGE = (100, 100, 100)
COLOR_LINE = (240, 240, 240)
COLOR_YELLOW_LINE = (241, 196, 15)
COLOR_RED = (231, 76, 60)
COLOR_YELLOW = (241, 196, 15)
COLOR_GREEN = (46, 204, 113)

CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
ROAD_WIDTH = 160
HALF_RW = ROAD_WIDTH // 2
STOP_MARGIN = HALF_RW + 15

SKIN_TONES = [(240, 200, 160), (220, 160, 120), (180, 120, 80), (120, 70, 40)]
SHIRT_COLORS = [(155, 89, 182), (52, 152, 219), (230, 126, 34), (26, 188, 156), (241, 196, 15), (231, 76, 60)]
HAIR_COLORS = [(20, 20, 20), (60, 40, 20), (120, 80, 30), (200, 170, 100)]

# --- 3. Stationary Sidewalk Pedestrians ---
class Pedestrian:
    def __init__(self, corner_zone, grid_x, grid_y):
        self.corner_zone = corner_zone
        self.speed = np.random.uniform(1.2, 1.8)
        self.walk_cycle = 0
        
        self.skin_color = SKIN_TONES[np.random.randint(0, len(SKIN_TONES))]
        self.shirt_color = SHIRT_COLORS[np.random.randint(0, len(SHIRT_COLORS))]
        self.hair_color = HAIR_COLORS[np.random.randint(0, len(HAIR_COLORS))]

        jitter_x = np.random.uniform(-8, 8)
        jitter_y = np.random.uniform(-8, 8)

        # Sidewalk zones
        if corner_zone == 0: # Top-Left
            self.base_pos = (CENTER_X - HALF_RW - 110 + (grid_x * 22) + jitter_x, CENTER_Y - HALF_RW - 110 + (grid_y * 22) + jitter_y)
            self.target_pos = (CENTER_X + HALF_RW + 30 + (grid_x * 22), CENTER_Y - HALF_RW - 110 + (grid_y * 22))
            self.direction = "HORIZONTAL"
        elif corner_zone == 1: # Top-Right
            self.base_pos = (CENTER_X + HALF_RW + 30 + (grid_x * 22) + jitter_x, CENTER_Y - HALF_RW - 110 + (grid_y * 22) + jitter_y)
            self.target_pos = (CENTER_X + HALF_RW + 30 + (grid_x * 22), CENTER_Y + HALF_RW + 30 + (grid_y * 22))
            self.direction = "VERTICAL"
        elif corner_zone == 2: # Bottom-Right
            self.base_pos = (CENTER_X + HALF_RW + 30 + (grid_x * 22) + jitter_x, CENTER_Y + HALF_RW + 30 + (grid_y * 22) + jitter_y)
            self.target_pos = (CENTER_X - HALF_RW - 110 + (grid_x * 22), CENTER_Y + HALF_RW + 30 + (grid_y * 22))
            self.direction = "HORIZONTAL"
        elif corner_zone == 3: # Bottom-Left
            self.base_pos = (CENTER_X - HALF_RW - 110 + (grid_x * 22) + jitter_x, CENTER_Y + HALF_RW + 30 + (grid_y * 22) + jitter_y)
            self.target_pos = (CENTER_X - HALF_RW - 110 + (grid_x * 22), CENTER_Y - HALF_RW - 110 + (grid_y * 22))
            self.direction = "VERTICAL"

        self.x, self.y = self.base_pos
        self.curr_target = self.target_pos

    def update(self, signal_phase):
        if signal_phase == "ALL_RED":
            # Walk across only during ALL_RED signal phase
            self.walk_cycle += 0.2
            if self.direction == "HORIZONTAL":
                step = self.speed if self.curr_target[0] > self.x else -self.speed
                self.x += step
                if (step > 0 and self.x >= self.curr_target[0]) or (step < 0 and self.x <= self.curr_target[0]):
                    self.curr_target = self.base_pos if self.curr_target == self.target_pos else self.target_pos
            elif self.direction == "VERTICAL":
                step = self.speed if self.curr_target[1] > self.y else -self.speed
                self.y += step
                if (step > 0 and self.y >= self.curr_target[1]) or (step < 0 and self.y <= self.curr_target[1]):
                    self.curr_target = self.base_pos if self.curr_target == self.target_pos else self.target_pos
        else:
            # Strictly stay put in place on sidewalk during regular traffic phases
            self.x, self.y = self.base_pos
            self.walk_cycle = 0

    def draw(self, surface):
        px, py = int(self.x), int(self.y)
        swing = np.sin(self.walk_cycle) * 4 if self.walk_cycle > 0 else 0

        if self.direction == "HORIZONTAL":
            pygame.draw.circle(surface, (20, 20, 20), (px + int(swing), py - 5), 2)
            pygame.draw.circle(surface, (20, 20, 20), (px - int(swing), py + 5), 2)
            pygame.draw.ellipse(surface, self.shirt_color, (px - 5, py - 7, 10, 14))
        else:
            pygame.draw.circle(surface, (20, 20, 20), (px - 5, py + int(swing)), 2)
            pygame.draw.circle(surface, (20, 20, 20), (px + 5, py - int(swing)), 2)
            pygame.draw.ellipse(surface, self.shirt_color, (px - 7, py - 5, 14, 10))

        pygame.draw.circle(surface, self.skin_color, (px, py), 4)
        pygame.draw.circle(surface, self.hair_color, (px, py), 3)

# --- 4. Car Class (Only Emergency Vehicle Blinks) ---
class Car:
    def __init__(self, lane, is_emergency=False, spawn_offset=0):
        self.lane = lane 
        self.max_speed = 3.5 if not is_emergency else 5.5
        self.speed = 0.0
        self.accel = 0.18
        self.decel = 0.35
        self.is_emergency = is_emergency
        
        offset = 35
        if lane == 0:   # Road A
            self.x, self.y = CENTER_X + offset, HEIGHT + 20 + spawn_offset
        elif lane == 1: # Road B
            self.x, self.y = WIDTH + 20 + spawn_offset, CENTER_Y + offset
        elif lane == 2: # Road C
            self.x, self.y = CENTER_X - offset, -20 - spawn_offset
        elif lane == 3: # Road D
            self.x, self.y = -20 - spawn_offset, CENTER_Y - offset

    def update(self, signal_state, is_active_road, cars_ahead):
        must_stop = False
        if not is_active_road or signal_state in ["YELLOW", "ALL_RED"]:
            if self.lane == 0 and self.y > CENTER_Y + STOP_MARGIN: must_stop = True
            elif self.lane == 1 and self.x > CENTER_X + STOP_MARGIN: must_stop = True
            elif self.lane == 2 and self.y < CENTER_Y - STOP_MARGIN: must_stop = True
            elif self.lane == 3 and self.x < CENTER_X - STOP_MARGIN: must_stop = True

        if self.is_emergency and is_active_road:
            must_stop = False

        closest_car_dist = 999
        for other in cars_ahead:
            if other is self: continue
            if self.lane == 0 and other.y < self.y: closest_car_dist = min(closest_car_dist, self.y - other.y)
            elif self.lane == 1 and other.x < self.x: closest_car_dist = min(closest_car_dist, self.x - other.x)
            elif self.lane == 2 and other.y > self.y: closest_car_dist = min(closest_car_dist, other.y - self.y)
            elif self.lane == 3 and other.x > self.x: closest_car_dist = min(closest_car_dist, other.x - self.x)

        if closest_car_dist < 42:
            must_stop = True

        if must_stop:
            self.speed = max(0.0, self.speed - self.decel)
        else:
            self.speed = min(self.max_speed, self.speed + self.accel)

        if self.lane == 0: self.y -= self.speed
        elif self.lane == 1: self.x -= self.speed
        elif self.lane == 2: self.y += self.speed
        elif self.lane == 3: self.x += self.speed

    def is_offscreen(self):
        return (self.x < -300 or self.x > WIDTH + 300 or self.y < -300 or self.y > HEIGHT + 300)

    def draw(self, surface):
        px, py = int(self.x), int(self.y)
        
        if self.is_emergency:
            body_color = (245, 245, 245)
            w, h = (20, 36) if self.lane in [0, 2] else (36, 20)
            pygame.draw.rect(surface, body_color, (px - w//2, py - h//2, w, h), border_radius=4)
            # Only emergency vehicle blinks blue/red light
            light_c = (0, 120, 255) if (pygame.time.get_ticks() // 150) % 2 == 0 else (255, 0, 0)
            pygame.draw.circle(surface, light_c, (px, py), 6)
        else:
            # Standard cars stay solid red, no blinking
            body_color = (220, 50, 50)
            if self.lane in [0, 2]:
                pygame.draw.rect(surface, body_color, (px - 10, py - 18, 20, 36), border_radius=4)
            else:
                pygame.draw.rect(surface, body_color, (px - 18, py - 10, 36, 20), border_radius=4)

# --- 5. Environment & Signal Setup ---
def draw_environment(surface):
    surface.fill(COLOR_GRASS)
    pygame.draw.rect(surface, COLOR_ROAD, (CENTER_X - HALF_RW, 0, ROAD_WIDTH, HEIGHT))
    pygame.draw.rect(surface, COLOR_ROAD, (0, CENTER_Y - HALF_RW, WIDTH, ROAD_WIDTH))
    pygame.draw.rect(surface, (35, 35, 38), (CENTER_X - HALF_RW, CENTER_Y - HALF_RW, ROAD_WIDTH, ROAD_WIDTH))

    fp_size = 140
    for cx, cy in [(CENTER_X - HALF_RW - fp_size, CENTER_Y - HALF_RW - fp_size),
                   (CENTER_X + HALF_RW, CENTER_Y - HALF_RW - fp_size),
                   (CENTER_X - HALF_RW - fp_size, CENTER_Y + HALF_RW),
                   (CENTER_X + HALF_RW, CENTER_Y + HALF_RW)]:
        pygame.draw.rect(surface, COLOR_SIDEWALK, (cx, cy, fp_size, fp_size))
        pygame.draw.rect(surface, COLOR_SIDEWALK_EDGE, (cx, cy, fp_size, fp_size), 3)

    pygame.draw.line(surface, COLOR_YELLOW_LINE, (CENTER_X, 0), (CENTER_X, CENTER_Y - HALF_RW), 3)
    pygame.draw.line(surface, COLOR_YELLOW_LINE, (CENTER_X, CENTER_Y + HALF_RW), (CENTER_X, HEIGHT), 3)
    pygame.draw.line(surface, COLOR_YELLOW_LINE, (0, CENTER_Y), (CENTER_X - HALF_RW, CENTER_Y), 3)
    pygame.draw.line(surface, COLOR_YELLOW_LINE, (CENTER_X + HALF_RW, CENTER_Y), (WIDTH, CENTER_Y), 3)

    for offset in range(-HALF_RW + 10, HALF_RW - 10, 20):
        pygame.draw.rect(surface, (230, 230, 230), (CENTER_X + offset, CENTER_Y + HALF_RW + 5, 10, 20))
        pygame.draw.rect(surface, (230, 230, 230), (CENTER_X + offset, CENTER_Y - HALF_RW - 25, 10, 20))
        pygame.draw.rect(surface, (230, 230, 230), (CENTER_X + HALF_RW + 5, CENTER_Y + offset, 20, 10))
        pygame.draw.rect(surface, (230, 230, 230), (CENTER_X - HALF_RW - 25, CENTER_Y + offset, 20, 10))

def draw_traffic_light(surface, x, y, active_state):
    pygame.draw.rect(surface, (10, 10, 10), (x - 12, y - 30, 24, 60), border_radius=5)
    pygame.draw.rect(surface, (241, 196, 15), (x - 12, y - 30, 24, 60), 2, border_radius=5)

    r_color = COLOR_RED if active_state == "RED" else (40, 10, 10)
    y_color = COLOR_YELLOW if active_state == "YELLOW" else (40, 40, 10)
    g_color = COLOR_GREEN if active_state in ["GREEN", "EMERGENCY"] else (10, 40, 10)

    pygame.draw.circle(surface, r_color, (x, y - 18), 7)
    pygame.draw.circle(surface, y_color, (x, y), 7)
    pygame.draw.circle(surface, g_color, (x, y + 18), 7)

# --- 6. Main Execution Loop ---
def main():
    traffic_density = np.random.randint(60, 120, 4)
    is_emergency = np.random.choice([True, False], size=4, p=[0.25, 0.75])
    
    total_traffic = np.sum(traffic_density)
    threshold = np.mean(traffic_density) * 1.1
    green_times = calculate_green_times(traffic_density, total_traffic, threshold)
    priority_queue = list(get_priority_index(traffic_density, is_emergency))
    
    active_idx = 0
    active_road = priority_queue[active_idx]
    
    signal_phase = "GREEN"
    phase_timer = green_times[active_road]
    
    cars = []
    for lane in range(4):
        num_cars = max(8, traffic_density[lane] // 8)
        has_em = is_emergency[lane]
        for i in range(num_cars):
            spawn_emergency = True if (has_em and i == 0) else False
            cars.append(Car(lane, is_emergency=spawn_emergency, spawn_offset=i * 48))

    pedestrians = [Pedestrian(corner_zone=c, grid_x=gx, grid_y=gy) for c in range(4) for gx in range(4) for gy in range(4)]
    dt_last = pygame.time.get_ticks()

    while True:
        now = pygame.time.get_ticks()
        dt = (now - dt_last) / 1000.0
        dt_last = now
        
        phase_timer -= dt

        if phase_timer <= 0:
            if signal_phase == "GREEN":
                signal_phase = "YELLOW"
                phase_timer = YELLOW_TIME
            elif signal_phase == "YELLOW":
                signal_phase = "ALL_RED"
                phase_timer = ALL_RED_TIME
            elif signal_phase == "ALL_RED":
                active_idx = (active_idx + 1) % 4
                
                if active_idx == 0:
                    traffic_density = np.random.randint(60, 120, 4)
                    is_emergency = np.random.choice([True, False], size=4, p=[0.25, 0.75])
                    total_traffic = np.sum(traffic_density)
                    threshold = np.mean(traffic_density) * 1.1
                    green_times = calculate_green_times(traffic_density, total_traffic, threshold)
                    priority_queue = list(get_priority_index(traffic_density, is_emergency))

                active_road = priority_queue[active_idx]
                signal_phase = "GREEN"
                phase_timer = green_times[active_road]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_environment(screen)

        # EXACT SIGNAL POSITION MAPPING PER ARROW DIRECTIONS:
        # Index 0: Road A (Northbound) -> Top-Left Signal
        # Index 1: Road B (Westbound)  -> Top-Right Signal
        # Index 2: Road C (Southbound) -> Bottom-Right Signal
        # Index 3: Road D (Eastbound)  -> Bottom-Left Signal
        light_coords = [
            (CENTER_X - HALF_RW - 25, CENTER_Y - HALF_RW - 25), # Top-Left
            (CENTER_X + HALF_RW + 25, CENTER_Y - HALF_RW - 25), # Top-Right
            (CENTER_X + HALF_RW + 25, CENTER_Y + HALF_RW + 25), # Bottom-Right
            (CENTER_X - HALF_RW - 25, CENTER_Y + HALF_RW + 25)  # Bottom-Left
        ]

        for i in range(4):
            state = "RED"
            if signal_phase != "ALL_RED" and i == active_road:
                state = "EMERGENCY" if is_emergency[i] and signal_phase == "GREEN" else signal_phase

            draw_traffic_light(screen, light_coords[i][0], light_coords[i][1], state)

        for car in cars[:]:
            cars_in_same_lane = [c for c in cars if c.lane == car.lane]
            car.update(signal_phase, (car.lane == active_road), cars_in_same_lane)
            car.draw(screen)

            if car.is_offscreen():
                cars.remove(car)
                cars.append(Car(car.lane, is_emergency=is_emergency[car.lane], spawn_offset=np.random.randint(0, 50)))

        for ped in pedestrians:
            ped.update(signal_phase)
            ped.draw(screen)

        # HUD Panel Overlay
        panel = pygame.Surface((380, 250))
        panel.set_alpha(235)
        panel.fill((10, 10, 14))
        screen.blit(panel, (20, 20))

        screen.blit(title_font.render("TRAFFIC CONTROLLER HUD", True, (255, 255, 255)), (30, 30))
        phase_color = COLOR_GREEN if signal_phase == "GREEN" else (COLOR_YELLOW if signal_phase == "YELLOW" else COLOR_RED)
        screen.blit(font.render(f"PHASE: {signal_phase} ({max(0.0, phase_timer):.1f}s)", True, phase_color), (30, 60))

        ped_text = "CROSSING ACTIVE" if signal_phase == "ALL_RED" else "WAITING ON SIDEWALK"
        screen.blit(font.render(f"PEDESTRIAN: {ped_text}", True, COLOR_GREEN if signal_phase == "ALL_RED" else COLOR_YELLOW), (30, 85))

        for i, name in enumerate(roads):
            is_cur = (i == active_road)
            txt_color = COLOR_GREEN if is_cur and signal_phase == "GREEN" else (180, 180, 180)
            
            em_label = " [EMERGENCY VEHICLE]" if is_emergency[i] else ""
            status_label = f"GREEN ({green_times[i]:.0f}s)" if is_cur else "RED"
            
            line = f"{name}: Density {traffic_density[i]:2d} | Signal: {status_label}{em_label}"
            screen.blit(font.render(line, True, txt_color), (30, 115 + (i * 26)))

        screen.blit(font.render(f"Active Queue Priority: {roads[active_road]}", True, COLOR_YELLOW), (30, 222))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

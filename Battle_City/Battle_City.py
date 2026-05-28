from pygame import *
from random import randint

win_width = 1280
win_height = 720
window = display.set_mode((win_width, win_height))
window.fill((0, 0, 0))
display.set_caption("Battle_City")
clock = time.Clock()

bullets = []
objects = []

score_player1 = 0
score_player2 = 0
font.init()
score_font = font.Font(None, 36)
win_font = font.Font(None, 72)
hp_font = font.Font(None, 26)

game_over = False
winner = None
draw_timer_start = None
draw_active = False

ammo_player1 = 25
ammo_player2 = 25
last_shot_time_player1 = 0
last_shot_time_player2 = 0
shot_delay = 500

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.original_image = transform.scale(image.load(player_image), (size_x, size_y))
        self.image = self.original_image.copy()
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.direct = 0
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        objects.append(self)

    def reset(self):
        if self.alive:
            window.blit(self.image, (self.rect.x, self.rect.y))
    
    def draw(self):
        self.reset()

    def damage(self, value, attacker=None):
        global score_player1, score_player2, game_over, winner, ammo_player1, ammo_player2
        self.hp -= value
        if self.hp <= 0:
            if attacker == 1:
                score_player1 += 1
                ammo_player1 += 5
                if score_player1 >= 5:
                    game_over = True
                    winner = 1
            elif attacker == 2:
                score_player2 += 1
                ammo_player2 += 5
                if score_player2 >= 5:
                    game_over = True
                    winner = 2
            
            self.alive = False
            while True:
                self.rect.x = randint(0, (win_width - 50) // 50) * 50
                self.rect.y = randint(1, (win_height - 50) // 50) * 50
                collision = False
                for obj in objects:
                    if obj != self and obj.rect.colliderect(self.rect):
                        collision = True
                        break
                if not collision:
                    self.hp = 100
                    self.max_hp = 100
                    self.alive = True
                    self.image = self.original_image.copy()
                    self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
                    break

class Bullet:
    def __init__(self, starting, x, y, b_x, b_y, owner):
        self.starting = starting
        self.x = x
        self.y = y
        self.b_x = b_x
        self.b_y = b_y
        self.owner = owner
        bullets.append(self)

    def update(self):
        self.x += self.b_x
        self.y += self.b_y

        if self.x < 0 or self.x > win_width or self.y < 0 or self.y > win_height:
            if self in bullets:
                bullets.remove(self)
            return

        for obj in objects:
            if obj != self.starting and obj.rect.collidepoint(self.x, self.y):
                obj.damage(20, self.owner)
                if self in bullets:
                    bullets.remove(self)
                return

    def draw(self):
        draw.circle(window, 'yellow', (int(self.x), int(self.y)), 5)

class Player(GameSprite):
    def update_1(self):
        global game_over, ammo_player1, last_shot_time_player1
        if game_over:
            return
            
        keys = key.get_pressed()
        old_x, old_y = self.rect.x, self.rect.y

        if keys[K_w] and self.rect.y > 5:
            self.rect.y -= self.speed
            self.direct = 0
        if keys[K_s] and self.rect.y < win_height - 55:
            self.rect.y += self.speed
            self.direct = 2
        if keys[K_d] and self.rect.x < win_width - 55:
            self.rect.x += self.speed
            self.direct = 1
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
            self.direct = 3

        if keys[K_w] or keys[K_s] or keys[K_d] or keys[K_a]:
            self.image = transform.rotate(self.original_image, -self.direct * 90)
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center

        for obj in objects:
            if obj != self and self.rect.colliderect(obj.rect):
                self.rect.x, self.rect.y = old_x, old_y
                if keys[K_w] or keys[K_s] or keys[K_d] or keys[K_a]:
                    self.image = transform.rotate(self.original_image, -self.direct * 90)
                    center = self.rect.center
                    self.rect = self.image.get_rect()
                    self.rect.center = center

        current_time = time.get_ticks()
        if keys[K_r] and current_time - last_shot_time_player1 >= shot_delay and ammo_player1 > 0:
            if self.direct == 0:
                b_x = 0
                b_y = -5
            elif self.direct == 1:
                b_x = 5
                b_y = 0
            elif self.direct == 2:
                b_x = 0
                b_y = 5
            else:
                b_x = -5
                b_y = 0
            Bullet(self, self.rect.centerx, self.rect.centery, b_x, b_y, 1)
            ammo_player1 -= 1
            last_shot_time_player1 = current_time

    def update_2(self):
        global game_over, ammo_player2, last_shot_time_player2
        if game_over or not self.alive:
            return

        keys = key.get_pressed()
        old_x, old_y = self.rect.x, self.rect.y

        if keys[K_i] and self.rect.y > 5:
            self.rect.y -= self.speed
            self.direct = 0
        if keys[K_k] and self.rect.y < win_height - 55:
            self.rect.y += self.speed
            self.direct = 2
        if keys[K_l] and self.rect.x < win_width - 55:
            self.rect.x += self.speed
            self.direct = 1
        if keys[K_j] and self.rect.x > 5:
            self.rect.x -= self.speed
            self.direct = 3

        if keys[K_i] or keys[K_k] or keys[K_l] or keys[K_j]:
            self.image = transform.rotate(self.original_image, -self.direct * 90)
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center

        for obj in objects:
            if obj != self and self.rect.colliderect(obj.rect):
                self.rect.x, self.rect.y = old_x, old_y
                if keys[K_i] or keys[K_k] or keys[K_l] or keys[K_j]:
                    self.image = transform.rotate(self.original_image, -self.direct * 90)
                    center = self.rect.center
                    self.rect = self.image.get_rect()
                    self.rect.center = center

        current_time = time.get_ticks()
        if keys[K_h] and current_time - last_shot_time_player2 >= shot_delay and ammo_player2 > 0:
            if self.direct == 0:
                b_x = 0
                b_y = -5
            elif self.direct == 1:
                b_x = 5
                b_y = 0
            elif self.direct == 2:
                b_x = 0
                b_y = 5
            else:
                b_x = -5
                b_y = 0
            Bullet(self, self.rect.centerx, self.rect.centery, b_x, b_y, 2)
            ammo_player2 -= 1
            last_shot_time_player2 = current_time

class Block:
    def __init__(self, x, y):
        objects.append(self)
        self.original_image = transform.scale(image.load("стена.png"), (50, 50))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = 60

    def draw(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

    def damage(self, value, attacker=None):
        self.hp -= value
        if self.hp <= 0:
            objects.remove(self)

player_1 = Player("main_tank.png", 560, 200, 48, 48, 3)
player_2 = Player("second_tank_1.png", 20, 200, 48, 48, 3)

block_size = 50
tank_size = 50
min_gap = tank_size + 10

grid_width = win_width // block_size
grid_height = win_height // block_size
grid = [[False for _ in range(grid_height)] for _ in range(grid_width)]

for obj in objects:
    if isinstance(obj, Player):
        grid[obj.rect.x // block_size][obj.rect.y // block_size] = True

blocks_placed = 0
max_blocks = 40

while blocks_placed < max_blocks:
    x = randint(0, grid_width - 1) * block_size
    y = randint(1, grid_height - 1) * block_size
    grid_x = x // block_size
    grid_y = y // block_size
    
    if grid[grid_x][grid_y]:
        continue
    
    has_neighbor = False
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = grid_x + dx, grid_y + dy
        if 0 <= nx < grid_width and 0 <= ny < grid_height:
            if grid[nx][ny]:
                has_neighbor = True
                break
    
    if not has_neighbor or randint(0, 2) == 0:
        rect = Rect(x, y, block_size, block_size)
        collision = False
        
        for obj in objects:
            if isinstance(obj, Player) and rect.colliderect(obj.rect):
                collision = True
                break
        
        if not collision:
            free_paths = 0
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = grid_x + dx * 2, grid_y + dy * 2
                if 0 <= nx < grid_width and 0 <= ny < grid_height:
                    if not grid[nx][ny]:
                        free_paths += 1
            
            if free_paths > 0 or blocks_placed < 20:
                Block(x, y)
                grid[grid_x][grid_y] = True
                blocks_placed += 1

game = True
while game:
    window.fill((0, 0, 0))

    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            game = False
        if game_over and e.type == KEYDOWN and e.key == K_SPACE:
            game_over = False
            winner = None
            draw_timer_start = None
            draw_active = False
            score_player1 = 0
            score_player2 = 0
            ammo_player1 = 20
            ammo_player2 = 20
            last_shot_time_player1 = 0
            last_shot_time_player2 = 0
            bullets.clear()
            objects.clear()
            player_1 = Player("main_tank.png", 560, 200, 50, 50, 3)
            player_2 = Player("second_tank_1.png", 20, 200, 50, 50, 3)
            
            grid = [[False for _ in range(grid_height)] for _ in range(grid_width)]
            for obj in objects:
                if isinstance(obj, Player):
                    grid[obj.rect.x // block_size][obj.rect.y // block_size] = True
            
            blocks_placed = 0
            while blocks_placed < max_blocks:
                x = randint(0, grid_width - 1) * block_size
                y = randint(1, grid_height - 1) * block_size
                grid_x = x // block_size
                grid_y = y // block_size
                
                if grid[grid_x][grid_y]:
                    continue
                
                has_neighbor = False
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = grid_x + dx, grid_y + dy
                    if 0 <= nx < grid_width and 0 <= ny < grid_height:
                        if grid[nx][ny]:
                            has_neighbor = True
                            break
                
                if not has_neighbor or randint(0, 2) == 0:
                    rect = Rect(x, y, block_size, block_size)
                    collision = False
                    
                    for obj in objects:
                        if isinstance(obj, Player) and rect.colliderect(obj.rect):
                            collision = True
                            break
                    
                    if not collision:
                        free_paths = 0
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = grid_x + dx * 2, grid_y + dy * 2
                            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                                if not grid[nx][ny]:
                                    free_paths += 1
                        
                        if free_paths > 0 or blocks_placed < 20:
                            Block(x, y)
                            grid[grid_x][grid_y] = True
                            blocks_placed += 1
            continue

    if not game_over:
        if ammo_player1 == 0 and ammo_player2 == 0 and not draw_active:
            draw_active = True
            draw_timer_start = time.get_ticks()
        
        if draw_active and time.get_ticks() - draw_timer_start >= 5000:
            game_over = True
            winner = None
        
        for bullet in bullets[:]:
            bullet.update()
            bullet.draw()

        player_1.update_1()
        player_1.draw()
        player_2.update_2()
        player_2.draw()

        for obj in objects:
            obj.draw()

        score1_text = score_font.render(f"Player 1", True, (255, 255, 255))
        score1_score = score_font.render(f"Score: {score_player1}", True, (255, 255, 255))
        ammo1_text = score_font.render(f"Ammo: {ammo_player1}", True, (255, 255, 255))
        hp1_text = hp_font.render(f"HP: {player_1.hp}", True, (255, 255, 255))
        
        window.blit(score1_text, (10, 10))
        window.blit(score1_score, (10, 45))
        window.blit(ammo1_text, (10, 80))
        window.blit(hp1_text, (10, 110))
        
        score2_text = score_font.render(f"Player 2", True, (255, 255, 255))
        score2_score = score_font.render(f"Score: {score_player2}", True, (255, 255, 255))
        ammo2_text = score_font.render(f"Ammo: {ammo_player2}", True, (255, 255, 255))
        hp2_text = hp_font.render(f"HP: {player_2.hp}", True, (255, 255, 255))
        
        window.blit(score2_text, (win_width - 150, 10))
        window.blit(score2_score, (win_width - 150, 45))
        window.blit(ammo2_text, (win_width - 150, 80))
        window.blit(hp2_text, (win_width - 150, 110))
        
        if draw_active:
            remaining_time = 5 - (time.get_ticks() - draw_timer_start) / 1000
            if remaining_time > 0:
                timer_text = hp_font.render(f"Нет боезапаса! Ничья через: {remaining_time:.1f}", True, (255, 0, 0))
                window.blit(timer_text, (win_width // 2 - 150, 50))
    else:
        if winner == 1:
            win_text = win_font.render("Игрок 1 победил!", True, (255, 255, 255))
            restart_text = score_font.render("Нажмите SPACE для реванша", True, (255, 255, 255))
            window.blit(win_text, (win_width // 2 - win_text.get_width() // 2, win_height // 2 - 50))
            window.blit(restart_text, (win_width // 2 - restart_text.get_width() // 2, win_height // 2 + 20))
        elif winner == 2:
            win_text = win_font.render("Игрок 2 победил!", True, (255, 255, 255))
            restart_text = score_font.render("Нажмите SPACE для реванша", True, (255, 255, 255))
            window.blit(win_text, (win_width // 2 - win_text.get_width() // 2, win_height // 2 - 50))
            window.blit(restart_text, (win_width // 2 - restart_text.get_width() // 2, win_height // 2 + 20))
        else:
            draw_text = win_font.render("Ничья!", True, (255, 255, 255))
            restart_text = score_font.render("Нажмите SPACE для реванша", True, (255, 255, 255))
            window.blit(draw_text, (win_width // 2 - draw_text.get_width() // 2, win_height // 2 - 50))
            window.blit(restart_text, (win_width // 2 - restart_text.get_width() // 2, win_height // 2 + 20))

    display.update()
    clock.tick(60)

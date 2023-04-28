import pygame
from pygame import mixer
import os
import time
import random

pygame.font.init()
pygame.init()
WIDTH, HEIGHT = 600, 750
SIZE = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bảo vệ trái đất")
mixer.music.load('assets/Jojo.mp3')
mixer.music.play(-1)
mixer.music.set_volume(0.7)
# Load images
RED_UFO = pygame.image.load(os.path.join("assets", "red_ufo.png"))
BLUE_UFO = pygame.image.load(os.path.join("assets", "blue_ufo.png"))
GREEN_UFO = pygame.image.load(os.path.join("assets", "green_ufo.png"))

# Player rocket
SPACE_ROCKET = pygame.image.load(os.path.join("assets", "pixel_rocket.png"))

# Bullet
YELLOW_BULLET = pygame.image.load(os.path.join("assets", "pixel_yellow_bullet.png"))

RED_BOOM = pygame.image.load(os.path.join("assets", "red_boom.png"))
BLUE_BOOM = pygame.image.load(os.path.join("assets", "blue_boom.png"))
GREEN_BOOM = pygame.image.load(os.path.join("assets", "green_boom.png"))

# Background
BACKGROUND = pygame.image.load(os.path.join("assets", "b.gif"))
BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))
BACKGROUND1 = pygame.image.load(os.path.join("assets", "b1.jpg"))
BACKGROUND1 = pygame.transform.scale(BACKGROUND1, (WIDTH, HEIGHT))
BACKGROUND2 = pygame.image.load(os.path.join("assets", "b2.jpg"))
BACKGROUND2 = pygame.transform.scale(BACKGROUND2, (WIDTH, HEIGHT))
BACKGROUND3 = pygame.image.load(os.path.join("assets", "b3.jpg"))
BACKGROUND3 = pygame.transform.scale(BACKGROUND3, (WIDTH, HEIGHT))
BACKGROUND4 = pygame.image.load(os.path.join("assets", "b4.jpeg"))
BACKGROUND4 = pygame.transform.scale(BACKGROUND4, (WIDTH, HEIGHT))
ENTER_BR = pygame.image.load(os.path.join("assets", "enter.png"))
ENTER_BR = pygame.transform.scale(ENTER_BR, (WIDTH, HEIGHT))
FAILED_BR = pygame.image.load(os.path.join("assets", "failed.gif"))
FAILED_BR = pygame.transform.scale(FAILED_BR, (WIDTH, HEIGHT))
PASSED_BR = pygame.image.load(os.path.join("assets", "pass.jpg"))
PASSED_BR = pygame.transform.scale(PASSED_BR, (WIDTH, HEIGHT))


class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Character:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.bullets = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def move_bullets(self, vel, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                obj.health -= 10
                self.bullets.remove(bullet)

    def shoot(self):
        if self.cool_down_counter == 0:
            bullet = Bullet(self.x, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Character):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = SPACE_ROCKET
        self.bullet_img = YELLOW_BULLET
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_bullets(self, vel, objs):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        objs.remove(obj)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)

    def draw(self, window):
        super().draw(window)
        self.healthBar(window)

    def healthBar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
        self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health),
        10))


class Enemy(Character):
    COLOR_MAP = {
        "red": (RED_UFO, RED_BOOM),
        "blue": (BLUE_UFO, BLUE_BOOM),
        "green": (GREEN_UFO, GREEN_BOOM)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.bullet_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            bullet = Bullet(self.x + 20, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offsett_x = obj2.x - obj1.x
    offsett_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offsett_x, offsett_y)) != None


def main():
    run = True
    # FPS = frames per second
    FPS = 100
    level = 0
    main_font = pygame.font.SysFont("bahnschrift", 40)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    bullet_vel = 4

    player = Player(300, 650)

    clock = pygame.time.Clock()

    lost = False
    win = False
    lost_count = 0
    win_count = 0

    def redraw_window(level):
        if level == 1:
            SIZE.blit(BACKGROUND, (0, 0))
        elif level == 2:
            SIZE.blit(BACKGROUND1, (0, 0))
        elif level == 3:
            SIZE.blit(BACKGROUND2, (0, 0))
        elif level == 4:
            SIZE.blit(BACKGROUND3, (0, 0))
        elif level == 5:
            SIZE.blit(BACKGROUND4, (0, 0))
        # Draw text
        health_label = main_font.render(f"HP: {player.health}%", 1, (255, 255, 255))
        level_label = main_font.render(f"Đợt tấn công: {level}", 1, (255, 255, 255))

        SIZE.blit(health_label, (10, 18))
        SIZE.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(SIZE)

        player.draw(SIZE)

        if lost:
            SIZE.blit(FAILED_BR, (0, 0))

        if win:
            SIZE.blit(PASSED_BR, (0, 0))

        pygame.display.update()

    while run:
        clock.tick(FPS)

        redraw_window(level)

        if player.health <= 0:
            lost = True
            lost_count += 1

            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if level > 5:
            win = True
            win_count += 1

            if win_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                # random vi tri cua enemy, toa do x, toa do y
                enemy = Enemy(random.randrange(100, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_height() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_width() + 15 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            Shoot_Sound = mixer.Sound('assets/shoot.wav')
            Shoot_Sound.play()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_bullets(bullet_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                player.health -= 10
                enemies.remove(enemy)
        player.move_bullets(-bullet_vel, enemies)


def main_menu():
    run = True
    while run:
        SIZE.blit(ENTER_BR, (0, 0))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


main_menu()
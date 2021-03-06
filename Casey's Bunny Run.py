#!/usr/bin/env python3

import json
import pygame
import sys
import time

pygame.mixer.pre_init()
pygame.init()

# Window settings
TITLE = "Bunny Run"
WIDTH = 1280
HEIGHT = 640
FPS = 60
GRID_SIZE = 64

# Options
sound_on = True

# Controls
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT
JUMP = pygame.K_SPACE

# Levels
levels = ["levels/world-1.json",
          "levels/world-2.json",
          "levels/world-3.json",
          "levels/world-4.json"]

# Colors
TRANSPARENT = (0, 0, 0, 0)
DARK_BLUE = (16, 86, 103)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (197, 122, 255)

# Fonts
Bubblegum_Font = pygame.font.Font("assets/fonts/Bubblegum.ttf", 32)
Chocolate_Bar_Font = pygame.font.Font("assets/fonts/Chocolate Bar.otf", 72)

# Helper functions
def load_image(file_path):
    img = pygame.image.load(file_path)
    img = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))

    return img

def play_sound(sound, loops=0, maxtime=0, fade_ms=0):
    if sound_on:
        if maxtime == 0:
            sound.play(loops, maxtime, fade_ms)
        else:
            sound.play(loops, maxtime, fade_ms)

def play_music():
    if sound_on:
        pygame.mixer.music.play(-1)

# Images
bunny_walk1 = load_image("assets/Players/bunny2_walk1.png")
bunny_walk2 = load_image("assets/Players/bunny2_walk2.png")
bunny_jump = load_image("assets/Players/bunny2_jump.png")
bunny_idle = load_image("assets/Players/bunny2_stand.png")
bunny_images = {"run": [bunny_walk1, bunny_walk2],
               "jump": bunny_jump,
               "idle": bunny_idle}

block_images = {"G": load_image("assets/Environment/ground_grass.png"),
                "GB": load_image("assets/Environment/ground_grass_broken.png"),
                "GS": load_image("assets/Environment/ground_grass_small.png"),
                "GSB": load_image("assets/Environment/ground_grass_small_broken.png"),
                "C": load_image("assets/Environment/ground_cake.png"),
                "CB": load_image("assets/Environment/ground_cake_broken.png"),
                "CS": load_image("assets/Environment/ground_cake_small.png"),
                "CSB": load_image("assets/Environment/ground_cake_small_broken.png"),
                "S": load_image("assets/Environment/ground_sand.png"),
                "SB": load_image("assets/Environment/ground_sand_broken.png"),
                "SS": load_image("assets/Environment/ground_sand_small.png"),
                "SSB": load_image("assets/Environment/ground_sand_small_broken.png"),
                "SN": load_image("assets/Environment/ground_snow.png"),
                "SNB": load_image("assets/Environment/ground_snow_broken.png"),
                "SNS": load_image("assets/Environment/ground_snow_small.png"),
                "SNSB": load_image("assets/Environment/ground_snow_small_broken.png"),
                "ST": load_image("assets/Environment/ground_stone.png"),
                "STB": load_image("assets/Environment/ground_stone_broken.png"),
                "STS": load_image("assets/Environment/ground_stone_small.png"),
                "STSB": load_image("assets/Environment/ground_stone_small_broken.png"),
                "W": load_image("assets/Environment/ground_wood.png"),
                "WB": load_image("assets/Environment/ground_wood_broken.png"),
                "WS": load_image("assets/Environment/ground_wood_small.png"),
                "WSB": load_image("assets/Environment/ground_wood_small_broken.png")}

coin_img = load_image("assets/Items/gold_1.png")
powerup_img = load_image("assets/Items/powerup_bunny.png")
carrot_img = load_image("assets/Items/carrot.png")
portal_img = load_image("assets/Items/portal_yellow.png")
gold_carrot_img = load_image("assets/Items/carrot_gold.png")
bubble_img = load_image("assets/Items/bubble.png")
bolt_img = load_image("assets/Particles/lighting_blue.png")
jetpack_img = load_image("assets/Items/jetpack.png")

spikeball_img1 = load_image("assets/Enemies/spikeBall1.png")
spikeball_img2 = load_image("assets/Enemies/spikeBall2.png")
spikeball_images = [spikeball_img1, spikeball_img2]

spikeman_img = load_image("assets/Enemies/spikeMan_stand.png")
spikeman_walk1 = load_image("assets/Enemies/spikeMan_walk1.png")
spikeman_walk2 = load_image("assets/Enemies/spikeMan_walk2.png")
spikeman_images = [spikeman_walk1, spikeman_walk2]

flyman_img1 = load_image("assets/Enemies/flyMan_stand.png")
flyman_img2 = load_image("assets/Enemies/flyMan_fly.png")
flyman_images = [flyman_img1, flyman_img2]

# Sounds
JUMP_SOUND = pygame.mixer.Sound("assets/sounds/jump.wav")
COIN_SOUND = pygame.mixer.Sound("assets/sounds/pickup_coin.wav")
POWERUP_SOUND = pygame.mixer.Sound("assets/sounds/powerup.wav")
HURT_SOUND = pygame.mixer.Sound("assets/sounds/hurt.ogg")
DIE_SOUND = pygame.mixer.Sound("assets/sounds/death.wav")
LEVELUP_SOUND = pygame.mixer.Sound("assets/sounds/level_up.wav")
GAMEOVER_SOUND = pygame.mixer.Sound("assets/sounds/game_over.wav")

class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vy = 0
        self.vx = 0

    def apply_gravity(self, level):
        self.vy += level.gravity
        self.vy = min(self.vy, level.terminal_velocity)

class Block(Entity):

    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Character(Entity):

    def __init__(self, images):
        super().__init__(0, 0, images['idle'])

        self.image_idle = images['idle']
        self.images_run_right = images['run']
        self.images_run_left = [pygame.transform.flip(img, 1, 0) for img in self.images_run_right]
        self.image_jump_right = images['jump']
        self.image_jump_left = pygame.transform.flip(self.image_jump_right, 1, 0)

        self.running_images = self.images_run_right
        self.image_index = 0
        self.steps = 0

        self.speed = 5
        self.jump_power = 20

        self.vx = 0
        self.vy = 0
        self.facing_right = True
        self.on_ground = True
        self.jetpack_on = False

        self.score = 0
        self.lives = 3
        self.hearts = 3
        self.max_hearts = 3
        self.invincibility = 0
        self.jetpack_time = 0
        self.coins = 0

    def move_left(self):
        self.vx = -self.speed
        self.facing_right = False

    def move_right(self):
        self.vx = self.speed
        self.facing_right = True

    def stop(self):
        self.vx = 0

    def jump(self, blocks):
        self.rect.y += 1

        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        if len(hit_list) > 0:
            self.vy = -1 * self.jump_power
            play_sound(JUMP_SOUND)

        self.rect.y -= 1

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level.width:
            self.rect.right = level.width

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0

        self.on_ground = False
        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def process_coins(self, coins):
        hit_list = pygame.sprite.spritecollide(self, coins, True)

        for coin in hit_list:
            play_sound(COIN_SOUND)
            self.score += coin.value
            self.coins += 1
            if self.coins == 10:
                self.lives += 1
                self.coins = 0

    def process_enemies(self, enemies):
        hit_list = pygame.sprite.spritecollide(self, enemies, False)

        if len(hit_list) > 0 and self.invincibility == 0:
            play_sound(HURT_SOUND)
            self.hearts -= 1
            self.invincibility = int(0.75 * FPS)

    def process_powerups(self, powerups):
        hit_list = pygame.sprite.spritecollide(self, powerups, True)

        for p in hit_list:
            play_sound(POWERUP_SOUND)
            p.apply(self)

    def check_flag(self, level):
        hit_list = pygame.sprite.spritecollide(self, level.flag, False)

        if len(hit_list) > 0:
            level.completed = True
            play_sound(LEVELUP_SOUND)

    def set_image(self):
        if self.on_ground:
            if self.vx != 0:
                if self.facing_right:
                    self.running_images = self.images_run_right
                else:
                    self.running_images = self.images_run_left

                self.steps = (self.steps + 1) % self.speed # Works well with 2 images, try lower number if more frames are in animation

                if self.steps == 0:
                    self.image_index = (self.image_index + 1) % len(self.running_images)
                    self.image = self.running_images[self.image_index]
            else:
                self.image = self.image_idle
        else:
            if self.facing_right:
                self.image = self.image_jump_right
            else:
                self.image = self.image_jump_left

    def die(self):
        self.lives -= 1

        if self.lives > 0:
            play_sound(DIE_SOUND)
        else:
            play_sound(GAMEOVER_SOUND)

    def respawn(self, level):
        self.rect.x = level.start_x
        self.rect.y = level.start_y
        self.hearts = self.max_hearts
        self.invincibility = 0

    def calculate_jetpack_time(self):
        if self.jetpack_time <= 0:
            self.jetpack_on = False
        else:
            self.jetpack_time -= 1

    def update(self, level):
        self.process_enemies(level.enemies)
        if self.jetpack_on == True:
            pass
        else:
            self.apply_gravity(level)
        self.move_and_process_blocks(level.blocks)
        self.check_world_boundaries(level)
        self.set_image()

        if self.hearts > 0:
            self.process_coins(level.coins)
            self.process_powerups(level.powerups)
            self.check_flag(level)

            if self.invincibility > 0:
                self.invincibility -= 1
        else:
            self.die()

class Coin(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.value = 10

class Enemy(Entity):
    def __init__(self, x, y, images):
        super().__init__(x, y, images[0])

        self.images_right = images
        self.images_left = [pygame.transform.flip(img, 1, 0) for img in images]
        self.current_images = self.images_left
        self.image_index = 0
        self.steps = 0

    def reverse(self):
        self.vx *= -1

        if self.vx < 0:
            self.current_images = self.images_left
        else:
            self.current_images = self.images_right

        self.image = self.current_images[self.image_index]

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.reverse()
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.reverse()

    def move_and_process_blocks(self):
        pass

    def set_images(self):
        if self.steps == 0:
            self.image = self.current_images[self.image_index]
            self.image_index = (self.image_index + 1) % len(self.current_images)

        self.steps = (self.steps + 1) % 20 # Nothing significant about 20. It just seems to work okay.

    def is_near(self, hero):
        return abs(self.rect.x - hero.rect.x) < 2 * WIDTH


    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vx = self.start_vx
        self.vy = self.start_vy
        self.image = self.images_left[0]
        self.steps = 0

class Bear(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def update(self, level, hero):
        if self.is_near(hero):
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.set_images()

class Monster(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

    def move_and_process_blocks(self, blocks):
        reverse = False

        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        reverse = True

        for block in hit_list:
            if self.vy >= 0:
                self.rect.bottom = block.rect.top
                self.vy = 0

                if self.vx > 0 and self.rect.right <= block.rect.right:
                    reverse = False

                elif self.vx < 0 and self.rect.left >= block.rect.left:
                    reverse = False

            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

        if reverse:
            self.reverse()

    def update(self, level, hero):
        if self.is_near(hero):
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.set_images()

class FlyMan(Enemy):
    
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def update(self, level, hero):
        if self.is_near(hero):
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.set_images()

class OneUp(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.lives += 1

class Heart(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.hearts += 1
        character.hearts = max(character.hearts, character.max_hearts)

class Powerup(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.score += 100

class Bolt(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.score -= 200
        if character.score < 0:
            character.score = 0

class Jetpack(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        
    def apply(self, character):
        character.jetpack_on = True
        character.jetpack_time = 3 * FPS
        character.vy = 0
        character.vx = 15
        game.hero.rect.y = 64
       
class Bubble(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.invincibility = int(3 * FPS)

class Flag(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Level():

    def __init__(self, file_path):
        self.starting_blocks = []
        self.starting_enemies = []
        self.starting_coins = []
        self.starting_powerups = []
        self.starting_flag = []

        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.flag = pygame.sprite.Group()
        self.active_sprites = pygame.sprite.Group()
        self.inactive_sprites = pygame.sprite.Group()

        with open(file_path, 'r') as f:
            data = f.read()

        map_data = json.loads(data)

        self.width = map_data['width'] * GRID_SIZE
        self.height = map_data['height'] * GRID_SIZE
        self.time = map_data['time'] * FPS

        self.start_x = map_data['start'][0] * GRID_SIZE
        self.start_y = map_data['start'][1] * GRID_SIZE

        for item in map_data['blocks']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            img = block_images[item[2]]
            self.starting_blocks.append(Block(x, y, img))

        for item in map_data['bears']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Bear(x, y, spikeman_images))

        for item in map_data['monsters']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Monster(x, y, spikeball_images))

        for item in map_data['flyman']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(FlyMan(x, y, flyman_images))

        for item in map_data['coins']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_coins.append(Coin(x, y, coin_img))

        for item in map_data['oneups']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(OneUp(x, y, carrot_img))

        for item in map_data['hearts']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Heart(x, y, powerup_img))

        for item in map_data['powerup']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Powerup(x, y, gold_carrot_img))

        for item in map_data['bolt']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Bolt(x, y, bolt_img))

        for item in map_data['jetpack']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Jetpack(x, y, jetpack_img))

        for item in map_data['bubble']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Bubble(x, y, bubble_img))

        for item in map_data['flag']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_flag.append(Flag(x, y, portal_img))

        self.background_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.scenery_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.inactive_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.active_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)

        if map_data['background-color'] != "":
            self.background_layer.fill(map_data['background-color'])

        if map_data['background-img'] != "":
            background_img = pygame.image.load(map_data['background-img'])

            if map_data['background-fill-y']:
                h = background_img.get_height()
                w = int(background_img.get_width() * HEIGHT / h)
                background_img = pygame.transform.scale(background_img, (w, HEIGHT))

            if "top" in map_data['background-position']:
                start_y = 0
            elif "bottom" in map_data['background-position']:
                start_y = self.height - background_img.get_height()

            if map_data['background-repeat-x']:
                for x in range(0, self.width, background_img.get_width()):
                    self.background_layer.blit(background_img, [x, start_y])
            else:
                self.background_layer.blit(background_img, [0, start_y])

        if map_data['scenery-img'] != "":
            scenery_img = pygame.image.load(map_data['scenery-img'])

            if map_data['scenery-fill-y']:
                h = scenery_img.get_height()
                w = int(scenery_img.get_width() * HEIGHT / h)
                scenery_img = pygame.transform.scale(scenery_img, (w, HEIGHT))

            if "top" in map_data['scenery-position']:
                start_y = 0
            elif "bottom" in map_data['scenery-position']:
                start_y = self.height - scenery_img.get_height()

            if map_data['scenery-repeat-x']:
                for x in range(0, self.width, scenery_img.get_width()):
                    self.scenery_layer.blit(scenery_img, [x, start_y])
            else:
                self.scenery_layer.blit(scenery_img, [0, start_y])

        pygame.mixer.music.load(map_data['music'])

        self.gravity = map_data['gravity']
        self.terminal_velocity = map_data['terminal-velocity']

        self.completed = False

        self.blocks.add(self.starting_blocks)
        self.enemies.add(self.starting_enemies)
        self.coins.add(self.starting_coins)
        self.powerups.add(self.starting_powerups)
        self.flag.add(self.starting_flag)

        self.active_sprites.add(self.coins, self.enemies, self.powerups)
        self.inactive_sprites.add(self.blocks, self.flag)

        self.inactive_sprites.draw(self.inactive_layer)

    def calculate_time(self):
        self.time -= 1
        if self.time <= 0:
            self.time = 0

    def reset(self):
        self.enemies.add(self.starting_enemies)
        self.coins.add(self.starting_coins)
        self.powerups.add(self.starting_powerups)

        self.active_sprites.add(self.coins, self.enemies, self.powerups)

        for e in self.enemies:
            e.reset()

class Game():

    SPLASH = 0
    START = 1
    PLAYING = 2
    PAUSED = 3
    LEVEL_COMPLETED = 4
    GAME_OVER = 5
    VICTORY = 6

    def __init__(self):
        self.window = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.done = False

        self.reset()

    def start(self):
        self.level = Level(levels[self.current_level])
        self.level.reset()
        self.hero.respawn(self.level)

    def advance(self):
        self.current_level += 1
        self.start()
        self.stage = Game.START
        self.hero.score += (self.level.time * 5)

    def reset(self):
        self.hero = Character(bunny_images)
        self.current_level = 0
        self.start()
        self.stage = Game.SPLASH

    def display_splash(self, surface):
        line1 = Chocolate_Bar_Font.render(TITLE, 1, DARK_BLUE)
        line2 = Chocolate_Bar_Font.render("Are you up to the challenge?", 1, WHITE)
        line3 = Chocolate_Bar_Font.render("PRESS ANY KEY TO START", 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;

        x3 = WIDTH / 2 - line3.get_width() / 2;
        y3 = HEIGHT - line3.get_height() - 64;

        bun_x1 = 64
        bun_y1 = 64
        bun_x2 = WIDTH - 128
        bun_y2 = HEIGHT - 128

        pygame.draw.rect(surface, PURPLE, [0, 0, WIDTH, HEIGHT])
        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))
        surface.blit(line3, (x3, y3))
        surface.blit(bunny_idle, (bun_x1, bun_y1))
        surface.blit(bunny_idle, (bun_x1, bun_y2))
        surface.blit(bunny_idle, (bun_x2, bun_y1))
        surface.blit(bunny_idle, (bun_x2, bun_y2))

    def display_message(self, surface, primary_text, secondary_text):
        line1 = Chocolate_Bar_Font.render(primary_text, 1, WHITE)
        line2 = Chocolate_Bar_Font.render(secondary_text, 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;

        box_x = WIDTH / 2 - line2.get_width() / 2;
        box_y = HEIGHT / 3 - line1.get_height() / 2;
        box_w = line2.get_width()
        box_h = line1.get_height() + line2.get_height() + 16;

        pygame.draw.rect(surface, PURPLE, [box_x, box_y, box_w, box_h])
        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))

    def display_stats(self, surface):
        hearts_text = Bubblegum_Font.render("Hearts: " + str(self.hero.hearts)+ "/" + str(self.hero.max_hearts), 1, WHITE)
        lives_text = Bubblegum_Font.render("x  " + str(self.hero.lives), 1, WHITE)
        score_text = Bubblegum_Font.render("Score: " + str(self.hero.score), 1, WHITE)
        level_text = Bubblegum_Font.render("Level: " + str(self.current_level + 1), 1, WHITE)
        coins_text = Bubblegum_Font.render("Coins: " + str(self.hero.coins), 1, WHITE)
        time_text = Bubblegum_Font.render("Time Remaining: " + str(self.level.time//60), 1, WHITE)

        surface.blit(score_text, (WIDTH - score_text.get_width() - 32, 32))
        surface.blit(hearts_text, (32, 32))
        surface.blit(bunny_idle, (32, 64))
        surface.blit(lives_text, (128, 80))
        surface.blit(level_text, (32, 128))
        surface.blit(coins_text, (32, 160))
        surface.blit(time_text, (32, 192))
        if self.hero.jetpack_on == True:
            jetpack_text = Bubblegum_Font.render("Jetpack Time: " + str(self.hero.jetpack_time//60), 1, WHITE)
            surface.blit(jetpack_text, (32, 224))
        else:
            pass
        
    def display_credits(self, surface):
        line1 = Chocolate_Bar_Font.render("CONGRATULATIONS!", 1, WHITE)
        line2 = Chocolate_Bar_Font.render("You are the ultImate bunny runner", 1, WHITE)
        line3 = Chocolate_Bar_Font.render("Score: " + str(self.hero.score), 1, WHITE)
        line4 = Chocolate_Bar_Font.render("Press R to Run AgaIn", 1, WHITE)
        line5 = Bubblegum_Font.render("Bunny Run created by: Casey Groves", 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 5;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line2.get_height() + 16;

        x3 = WIDTH / 2 - line3.get_width() / 2;
        y3 = y2 + line3.get_height() + 16;

        x4 = WIDTH / 2 - line4.get_width() / 2;
        y4 = y3 + line4.get_height() + 16;

        x5 = WIDTH / 2 - line5.get_width() / 2;
        y5 = y4 + line5.get_height() + 64;

        pygame.draw.rect(surface, PURPLE, [0, 0, WIDTH, HEIGHT])
        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))
        surface.blit(line3, (x3, y3))
        surface.blit(line4, (x4, y4))
        surface.blit(line5, (x5, y5))

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            elif event.type == pygame.KEYDOWN:
                if self.stage == Game.SPLASH or self.stage == Game.START:
                    self.stage = Game.PLAYING
                    play_music()

                elif self.stage == Game.PLAYING:
                    if event.key == JUMP:
                        self.hero.jump(self.level.blocks)
                    if event.key == pygame.K_f:
                        self.hero.speed = 10
                    elif event.key != pygame.K_f:
                        self.hero.speed = 5

                elif self.stage == Game.PAUSED:
                    pass

                elif self.stage == Game.LEVEL_COMPLETED:
                    self.advance()

                elif self.stage == Game.VICTORY or self.stage == Game.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset()

        pressed = pygame.key.get_pressed()

        if self.stage == Game.PLAYING:
            if self.hero.jetpack_on == False:
                if pressed[LEFT]:
                    self.hero.move_left()
                elif pressed[RIGHT]:
                    self.hero.move_right()
                else:
                    self.hero.stop()
            else:
                pass

    def update(self):
        if self.stage == Game.PLAYING:
            self.hero.update(self.level)
            self.level.enemies.update(self.level, self.hero)
            self.level.calculate_time()
            if self.hero.jetpack_on == True:
                self.hero.calculate_jetpack_time()
            else:
                pass

        if self.level.completed:
            if self.current_level < len(levels) - 1:
                self.stage = Game.LEVEL_COMPLETED
            else:
                self.stage = Game.VICTORY
            pygame.mixer.music.stop()

        elif self.hero.lives == 0 or self.level.time == 0:
            self.stage = Game.GAME_OVER
            pygame.mixer.music.stop()

        elif self.hero.hearts == 0:
            self.level.reset()
            self.hero.respawn(self.level)

    def calculate_offset(self):
        x = -1 * self.hero.rect.centerx + WIDTH / 2

        if self.hero.rect.centerx < WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - WIDTH / 2:
            x = -1 * self.level.width + WIDTH

        return x, 0

    def draw(self):
        offset_x, offset_y = self.calculate_offset()

        self.level.active_layer.fill(TRANSPARENT)
        self.level.active_sprites.draw(self.level.active_layer)

        if self.hero.invincibility % 3 < 2:
            self.level.active_layer.blit(self.hero.image, [self.hero.rect.x, self.hero.rect.y])

        self.window.blit(self.level.background_layer, [offset_x / 3, offset_y])
        self.window.blit(self.level.scenery_layer, [offset_x / 2, offset_y])
        self.window.blit(self.level.inactive_layer, [offset_x, offset_y])
        self.window.blit(self.level.active_layer, [offset_x, offset_y])

        self.display_stats(self.window)

        if self.stage == Game.SPLASH:
            self.display_splash(self.window)
        elif self.stage == Game.START:
            self.display_message(self.window, "Ready?!!!", "Press any key to start")
        elif self.stage == Game.PAUSED:
            pass
        elif self.stage == Game.LEVEL_COMPLETED:
            self.display_message(self.window, "Level Complete", "Press any key to continue")
        elif self.stage == Game.VICTORY:
            self.display_credits(self.window)
        elif self.stage == Game.GAME_OVER:
            self.display_message(self.window, "Game Over", "Press 'R' to restart")

        pygame.display.flip()

    def loop(self):
        while not self.done:
            self.process_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.start()
    game.loop()
    pygame.quit()
    sys.exit()

import pygame
import os
from pygame import mixer
import button
import time
import csv
import subprocess

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('PROJECT QUASART')

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75
start_game = False
start_intro = False
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
level = 0
deaths = 0
coins_score = 0
SCROLL_THRESH = 200
screen_scroll = 0
bg_scroll = 0
root = 'tiles/TILES TOWN'
TILE_TYPES = len(os.listdir(root))
# define player action variables
moving_left = False
moving_right = False
font= pygame.font.Font('font/Early GameBoy.ttf', 20)
fontcoin= pygame.font.Font('font/Early GameBoy.ttf', 29)
#music
pygame.mixer.music.load('music/town.mp3')
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1, 0, 0)
Coin_sound = pygame.mixer.Sound('music/coin.mp3')
Coin_sound.set_volume(0.05)
Death_sound = pygame.mixer.Sound('music/death.mp3')
Death_sound.set_volume(0.35)
Jump_sound = pygame.mixer.Sound('music/jump.mp3')
Jump_sound.set_volume(0.1)
Select_sound = pygame.mixer.Sound('music/select.mp3')
Select_sound.set_volume(0.3)

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    if x >= 16 and x <= 18:
        img = pygame.image.load(f'{root}/{x}.png').convert_alpha()
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)
    elif x == 2:
        img = pygame.image.load(f'{root}/{x}.png').convert_alpha()
        img = pygame.transform.scale(img, (TILE_SIZE, 2 * TILE_SIZE))
        img_list.append(img)
    elif x == 4:
        img = pygame.image.load(f'{root}/{x}.png').convert_alpha()
        img = pygame.transform.scale(img, (2 * TILE_SIZE, TILE_SIZE))
        img_list.append(img)
    elif x == 11:
        img = pygame.image.load(f'{root}/{x}.png').convert_alpha()
        img_list.append(img)
    elif x >= 24:
        img = pygame.image.load(f'{root}/{x}.png').convert_alpha()
        img_list.append(img)
    else:
        img = pygame.image.load(f'{root}/{x}.png').convert_alpha()
        img_list.append(img)

#group of sprites
#create sprite groups
decoration_group = pygame.sprite.Group()
ladder_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()
house_group = pygame.sprite.Group()
npc_group = pygame.sprite.AbstractGroup()
door_group = pygame.sprite.Group()

#menu
menu0 = pygame.image.load('img/mainmenu/menu.png').convert_alpha()
menu = pygame.transform.scale(menu0,(950,650))
start_img = pygame.image.load('img/mainmenu/start_img.png').convert_alpha()
exit_img = pygame.image.load('img/mainmenu/exit_img.png').convert_alpha()

#define colours
BG = (80, 187, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)



class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0


    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:#whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2:#vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True

        return fade_complete

# create screen fades
intro_fade = ScreenFade(1, BLACK, 15)
npc_fade = ScreenFade(1, BLACK, 15)
death_fade = ScreenFade(2, PINK, 50)


def draw_bg():
    b_img = pygame.image.load(f'img/background/town.png').convert_alpha()
    b1_img = pygame.transform.scale(b_img, (800, 650))
    screen.blit(b1_img,(0,0))



#function to reset level
def reset_level():
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    coins_group.empty()

    #create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data
#player
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.in_stairs = False
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Attack', 'Death', 'stairs']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.in_air == False:
            Jump_sound.play()
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y



        # check collision with tails
        for tile in world.obstacle_list:
            # check for collition in x
            if tile[1].colliderect(self.rect.x + dx, self.rect.y , self.width, self.height):
                dx=0

            #check for collition in y
            if tile[1].colliderect(self.rect.x,self.rect.y + dy, self.width, self.height):
                #check if below the ground
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                # check if above the ground
                elif self.vel_y > 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False
        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy
        #void
        if self.rect.y > SCREEN_HEIGHT:
            player.alive= False
        #update scroll
        if self.char_type == 'player':
            if self.rect.right > SCREEN_WIDTH - SCROLL_THRESH or self.rect.left < SCROLL_THRESH:
                self.rect.x -= dx
                screen_scroll = -dx
        return screen_scroll


    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def restart(self):
        self.alive = True
        self.rect.x = 100
        self.rect.y = 600
        start_intro = True
        bg_scroll = 0

    def draw(self):
        if self.flip == False and self.action == 1:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 20, self.rect.y))
        else:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


#GRID

def draw_grid():
    for line in range(0, 20):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))

#coins
class coin(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # load all images for the players
        animation_types = ['Coins']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    def update(self):
        if player.alive == True:
            self.update_animation()
            self.update_action(0)
            self.rect.x += screen_scroll
        else:
            self.rect.x += screen_scroll
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 15:
                        decoration = Decoration(img, x, y)
                        decoration_group.add(decoration)
                    elif tile >= 16 and tile <= 18:
                        self.obstacle_list.append(tile_data)
                    elif tile == 19 or tile == 32:
                        ladder = Ladder(img, x, y)
                        ladder_group.add(ladder)
                    elif tile >= 20 and tile <= 24:
                        decoration = Decoration(img, x, y)
                        decoration_group.add(decoration)
                    elif tile == 25:
                        decoration = Decoration(img, x, y)
                        door_group.add(decoration)
                    elif tile >= 26 and tile <= 31:
                        decoration = Decoration(img, x, y)
                        decoration_group.add(decoration)

        return player

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE )

    def update(self):
        self.rect.x += screen_scroll
class Door(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE)

    def update(self):
        self.rect.x += screen_scroll
class Chest(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Ladder(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE)

    def update(self):
        self.rect.x += screen_scroll

class house(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    def update(self):
        self.rect.x += screen_scroll
class npc(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # load all images for the players
        animation_types = ['Idle']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'{self.char_type}/{animation}/{i}.gif')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.npctalk = False

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def update(self):
        if player.alive == True:
            self.update_animation()
            self.update_action(0)
            self.rect.x += screen_scroll
        else:
            self.rect.x += screen_scroll
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

#player
player = Soldier('player', 200, 600, 2.65, 5)
player_group = pygame.sprite.Group()
player_group.add(player)


#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'leveldata/town.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player = world.process_data(world_data)

# COIN POSITION

#create buttons
start_button = button.Button(300,300, start_img, 0.3)
exit_button = button.Button(300,415, exit_img, 0.3)

#levels update

def stairsup():
    if pygame.sprite.groupcollide(player_group, ladder_group, False, False):
        player.jump = False
        return True
    else:
        player.in_stairs = False
        return False

def Initializate():
    draw_bg()
    ladder_group.draw(screen)
    ladder_group.update()
    decoration_group.draw(screen)
    decoration_group.update()
    door_group.draw(screen)
    door_group.update()
    house_group.draw(screen)
    house_group.update()
    world.draw()
    player.update_animation()
    coins_group.update()
    coins_group.draw(screen)
    npc_group.draw(screen)
    npc_group.update()
    player.draw()

fontext= pygame.font.Font('font/Fortnite.ttf', 140)

def textfade(str,speed,pos,color):
    text_iterator = iter(str)
    text = ''
    while len(text) < len(str):
        text += next(text_iterator)
        text1 = fontext.render(text, 1, color)
        text2 = fontext.render(text, 1, (0,0,0))
        screen.blit(text2, (pos[0] + 2, pos[1] + 2))
        screen.blit(text1, pos)

        pygame.display.flip()
        clock.tick(speed)
counter_text = 0

AUDIOIMG = pygame.image.load('img/DIALOGO.png')
fontdiag= pygame.font.Font('font/Fortnite.ttf', 28)
def dialog(str,speed,pos,color):
    text_iterator = iter(str)
    text = ''
    while len(text) < len(str):
        text += next(text_iterator)
        text1 = fontdiag.render(text, 1, color)
        text2 = fontdiag.render(text, 1, (0,0,0))
        screen.blit(text2, (pos[0] + 2, pos[1] + 2))
        screen.blit(text1, pos)

        pygame.display.flip()
        clock.tick(speed)
counter_dialog = 0
dialog1 = pygame.mixer.Sound('music/AUDIOS FINAL/TOWN.mp3')
dialog2 = pygame.mixer.Sound('music/AUDIOS FINAL/TOWN1.mp3')
dialog3 = pygame.mixer.Sound('music/AUDIOS FINAL/TOWN2.mp3')
dialog4 = pygame.mixer.Sound('music/AUDIOS FINAL/TOWN3.mp3')
dialog5 = pygame.mixer.Sound('music/AUDIOS FINAL/TOWN4.mp3')
dialog6 = pygame.mixer.Sound('music/AUDIOS FINAL/TOWN5.mp3')

#run loop
run = True
while run:
    
    clock.tick(FPS)
    start_game = True
    if start_game == False:
        # add buttons

        #main menu
        num_of_frames = len(os.listdir(f'img/mainmenu/intro'))
        for i in range(1, num_of_frames):
            if start_button.draw(screen):
                cinematics('intro')
                start_game = True
                start_intro = True
            if exit_button.draw(screen):
                run = False
            # gif background
            img = pygame.image.load(f'img/mainmenu/intro/c ({i}).png')
            img1 = pygame.transform.scale(img, (800, 640))
            screen.blit(img1, (0, 0))
            pygame.display.update()


    else:
        Initializate()
        pygame.mixer.music.set_volume(0.2)
        if counter_text == 0:
            textfade('??? *#¿', 8, (200, 250),
                     (255, 255, 255))
            counter_text += 1
        if counter_dialog == 0:
            pygame.mixer.music.set_volume(0.1)
            screen.blit(AUDIOIMG, (0, 0))
            dialog1.play()
            time.sleep(1)
            dialog('OHH DEBES ESTAR BROMEANDO, INTERRUPCIONES TEMPORALES', 10, (200, 450), (255, 255, 255))
            dialog('DE NUEVO, SE HAN COMBINADO DIFERENTES EPOCAS DE LA', 11, (200, 500), (255, 255, 255))
            dialog('HISTORIA, NO IMPORTA, EL MEDIDOR ME INDICA QUE ', 12, (200, 550), (255, 255, 255))
            dialog('ACA SE ENCUENTRA EL CONOCIMIENTO QUE BUSCAMOS', 12, (200, 600), (255, 255, 255))
            screen.blit(AUDIOIMG, (0, 0))
            dialog('VE A BUSCAR EN ESTOS COFRES TE IRE EXPLICANDO', 12, (200, 450), (255, 255, 255))
            counter_dialog += 1
        # update player actions
        if stairsup() == False:
            GRAVITY = 0.75
        if player.alive:
            if player.in_air:
                player.update_action(2)  # 2: jump
                if pygame.sprite.groupcollide(player_group, coins_group, False, True):
                    coins_score += 1
                    Coin_sound.play()
                if pygame.sprite.groupcollide(player_group, ladder_group, False, False):
                    player.in_air = False
                    player.update_action(5)
                    player.update_animation()
            elif player.in_stairs:
                player.update_action(5)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.update_action(3)
            elif moving_left or moving_right:
                player.update_action(1)  # 1: run
            #coins eraser
            elif pygame.sprite.groupcollide(player_group, coins_group, False, True):
                coins_score += 1
                Coin_sound.play()
            elif pygame.sprite.groupcollide(player_group, npc_group, False, False):
                player.update_action(0)
                num_of_frames = len(os.listdir(f'img/tecla'))
                img = pygame.image.load(f'img/tecla/{0}.png')
                img1 = pygame.transform.scale(img, (50, 50))
                screen.blit(img1, (150, 450))
                pygame.display.update()
                text1 = fontcoin.render(str('Push to talk').zfill(3), 1, (0, 0, 0))
                screen.blit(text1, (208, 460))
                text = fontcoin.render(str('Push to talk').zfill(3), 1, (255, 255, 255))
                screen.blit(text, (210, 460))
            elif pygame.sprite.groupcollide(player_group, door_group, False, False):
                player.update_action(0)
                num_of_frames = len(os.listdir(f'img/tecla'))
                img = pygame.image.load(f'img/tecla/{0}.png')
                img1 = pygame.transform.scale(img, (50, 50))
                screen.blit(img1, (150, 450))
                pygame.display.update()
                text1 = fontcoin.render(str('Push to open').zfill(3), 1, (0, 0, 0))
                screen.blit(text1, (208, 460))
                text = fontcoin.render(str('Push to open').zfill(3), 1, (255, 255, 255))
                screen.blit(text, (210, 460))



            else:
                player.update_action(0)  # 0: idle
            screen_scroll= player.move(moving_left, moving_right)
        else:
            pygame.mixer.music.pause()
            coins_group.update()
            if death_fade.fade():
                Death_sound.play()
                death_fade.fade_counter = 0
                death_fade.fade_counter= SCREEN_HEIGHT
                for i in range(5):
                    b_img = pygame.image.load(f'img/player/Death/{i}.png').convert_alpha()
                    b1_img = pygame.transform.scale(b_img, (400, 350))
                    b_img2 = pygame.image.load(f'img/background/4.png').convert_alpha()
                    screen.blit(b_img2,(-320,0))
                    screen.blit(b1_img, (250, 250))
                    time.sleep(0.2)
                    pygame.display.update()
                time.sleep(0.5)
                coins_score = 0
                player.restart()
                coins_group.empty()
                decoration_group.empty()
                ladder_group.empty()
                door_group.empty()
                # create empty tile list
                world_data = []
                for row in range(ROWS):
                    r = [-1] * COLS
                    world_data.append(r)
                # load in level data and create world
                with open(f'leveldata/town.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player = world.process_data(world_data)
            pygame.mixer.music.unpause()


    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and stairsup() == True:
                player.vel_y = -1
                GRAVITY = 0
                player.in_stairs = True
            if event.key == pygame.K_x and pygame.sprite.groupcollide(player_group, npc_group, False, False):
                print('talking')
            if event.key == pygame.K_x and pygame.sprite.groupcollide(player_group, door_group, False, False):
                if counter_dialog == 1:
                    pygame.mixer.music.set_volume(0.1)
                    screen.blit(AUDIOIMG, (0, 0))
                    dialog2.play()
                    time.sleep(1)
                    dialog('BIEN, ESTAMOS EN BUSCA DE EINSTEIN, UNA DE LAS ', 10, (200, 450), (255, 255, 255))
                    dialog('MENTES BRILLANTES DE LA HISTORIA, CON MUCHOS', 11, (200, 500), (255, 255, 255))
                    dialog('ERRORES Y ACIERTOS, SU DESCUBRIMIENTO ESTRELLA', 12, (200, 550), (255, 255, 255))
                    dialog('LA TEORIA DE LA RELATIVIDAD, LA CUAL RELACIONA', 12, (200, 600), (255, 255, 255))
                    screen.blit(AUDIOIMG, (0, 0))
                    dialog('EL ESPACIO Y TIEMPO DE UNA FORMA MAGNIFICA', 12, (200, 450), (255, 255, 255))
                if counter_dialog == 2:
                    pygame.mixer.music.set_volume(0.1)
                    screen.blit(AUDIOIMG, (0, 0))
                    dialog3.play()
                    time.sleep(1)
                    dialog('PARECE QUE TE INTERESO LA RELATIVIDAD, BIEN ES', 10, (200, 450), (255, 255, 255))
                    dialog('INCREIBLE, AL JUNTAR LOS CONCEPTOS DE ESPACIO Y', 11, (200, 500), (255, 255, 255))
                    dialog('TIEMPO, ESTE SE COMPORTA COMO UNA TELA, QUE SE', 12, (200, 550), (255, 255, 255))
                    dialog('PUEDE DEFORMAR, NO SOLO CON MASA SI NO CON', 12, (200, 600), (255, 255, 255))
                    screen.blit(AUDIOIMG, (0, 0))
                    dialog('ENERGIA Y CON MUCHAS MAS COSAS, ENTRE MAS', 10, (200, 450), (255, 255, 255))
                    dialog('DEFORMADO ESTA, EL TIEMPO TENDRA REPERCUCIONES', 11, (200, 500), (255, 255, 255))
                    dialog('PUEDE IR MUCHISIMO MAS RAPIDO O', 12, (200, 550), (255, 255, 255))
                    dialog('MUCHISIMO MAS LENTO', 12, (200, 600), (255, 255, 255))
                    screen.blit(AUDIOIMG, (0, 0))
                if counter_dialog == 3:
                    pygame.mixer.music.set_volume(0.1)
                    screen.blit(AUDIOIMG, (0, 0))
                    dialog4.play()
                    time.sleep(1)
                    dialog('¿OYE RECUERDAS LO DEL ESPACIO TIEMPO? ¿QUE PASARIA', 10, (200, 450), (255, 255, 255))
                    dialog('SI UN OBJETO CON DEMASIADA ENERGIA O MASA LO', 11, (200, 500), (255, 255, 255))
                    dialog('DEFORMA?¿LO DEFORMARIA INFINITAMENTE? BIEN PUES', 12, (200, 550), (255, 255, 255))
                    dialog('ESTAMOS ANTE LA CREACION DE UN AGUJERO NEGRO', 12, (200, 600), (255, 255, 255))
                    screen.blit(AUDIOIMG, (0, 0))
                    dialog('EINSTEIN NO LO SABRIA, PERO CAMBIARIA LA HISTORIA ', 12, (200, 450), (255, 255, 255))
                    dialog('DEL MUNDO MODERNO', 11, (200, 500), (255, 255, 255))
                if counter_dialog == 4:
                    pygame.mixer.music.set_volume(0.1)
                    screen.blit(AUDIOIMG, (0, 0))
                    dialog5.play()
                    time.sleep(1)
                    dialog('EN ESTA EPOCA SE LLEVO A CABO UNA REVOLUCION MUY', 10, (200, 450), (255, 255, 255))
                    dialog('IMPORTANTE, LA CUANTICA, UNA TEORIA ANTIINTUITIVA', 11, (200, 500), (255, 255, 255))
                    dialog('A MAS NO PODER, SUPERPOSICIONES, OBJETOS QUE ', 12, (200, 550), (255, 255, 255))
                    dialog('TRASPASAN COSAS IMPOSIBLES, EINSTEIN POR SUPUESTO', 12, (200, 600), (255, 255, 255))
                    screen.blit(AUDIOIMG, (0, 0))
                    dialog('NUNCA LO APOYARIA, PERO NUNCA SABRIA SU IMPORTANCIA', 12, (200, 450), (255, 255, 255))
                    dialog('Y SU FORMA EQUIVOCADA DE VERLA', 11, (200, 500), (255, 255, 255))
                if counter_dialog == 5:
                    pygame.mixer.music.set_volume(0.1)
                    screen.blit(AUDIOIMG, (0, 0))
                    dialog6.play()
                    time.sleep(1)
                    dialog('UN INVIERNO NUCLEAR, ESO ES LO QUE DESATARIA UNA', 10, (200, 450), (255, 255, 255))
                    dialog('DE LAS MAS GENIALES IDEAS DE EINSTEIN, SU', 11, (200, 500), (255, 255, 255))
                    dialog('FAMOSA ECUACION E=MC^2', 12, (200, 550), (255, 255, 255))
                    time.sleep(3)
                    pygame.quit()
                    subprocess.call(["python", "DARK.py"])
                counter_dialog += 1

            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True



            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_RIGHT:
                if level == 3:
                    level = 3
                else:
                    level += 1
            if event.key == pygame.K_LEFT:
                if level == 0 :
                    level=0
                else:
                    level-=1
        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                GRAVITY = 0.75

    pygame.display.update()

pygame.quit()

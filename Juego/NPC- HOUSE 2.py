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
TILE_TYPES = 28

# define player action variables
moving_left = False
moving_right = False
font= pygame.font.Font('font/Early GameBoy.ttf', 20)
fontcoin= pygame.font.Font('font/Fortnite.ttf', 35)
#music
pygame.mixer.music.load('music/themes/greece.mp3')
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1, 0, 0)
Coin_sound = pygame.mixer.Sound('music/coin.mp3')
Coin_sound.set_volume(0.05)
Death_sound = pygame.mixer.Sound('music/death.mp3')
Death_sound.set_volume(0.35)
Jump_sound = pygame.mixer.Sound('music/jump.mp3')
Jump_sound.set_volume(0.1)
Select_sound = pygame.mixer.Sound('music/select.mp3')
Select_sound.set_volume(0.3)

#npc
talking = False

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    if x >= 24:
        img = pygame.image.load(f'tiles/NPC- CASA/tile/{x}.png')
        img_list.append(img)
    elif x == 16:
        img = pygame.image.load(f'tiles/NPC- CASA/tile/{x}.png')
        img = pygame.transform.scale(img, (200, 200))
        img_list.append(img)


    else:
        img = pygame.image.load(f'tiles/NPC- CASA/tile/{x}.png')
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
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
    b_img = pygame.image.load(f'img/Background/{level}.png').convert_alpha()
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
                    if tile == 0:
                        self.obstacle_list.append(tile_data)
                    elif tile == 1:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile >= 2 and tile <= 7:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 8 and tile <= 11:
                        ladder = Ladder(img, x * TILE_SIZE, y * TILE_SIZE)
                        ladder_group.add(ladder)
                    elif tile == 16:
                         npsc= npc('npc', x * TILE_SIZE+50, y * TILE_SIZE+50, 0.5)
                         npc_group.add(npsc)
                    elif tile == 14:
                        self.obstacle_list.append(tile_data)

                    elif tile == 17:
                        coins = coin('icons', x * TILE_SIZE + 20, y * TILE_SIZE + 12, 3)
                        coins_group.add(coins)
                    elif tile == 19:
                        door = Door(img, x * TILE_SIZE, y * TILE_SIZE)
                        door_group.add(door)
                    elif tile >= 21 and tile <= 23:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile >= 24:
                        door = house(img, x * TILE_SIZE, y * TILE_SIZE)
                        house_group.add(door)

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
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
class Door(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

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
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

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
player = Soldier('player', 200, 600, 2.92, 5)
player_group = pygame.sprite.Group()
player_group.add(player)


#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'leveldata/npc.csv', newline='') as csvfile:
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
    door_group.draw(screen)
    door_group.update()
    house_group.draw(screen)
    house_group.update()
    world.draw()
    player.update_animation()
    coins_group.update()
    coins_group.draw(screen)
    decoration_group.draw(screen)
    decoration_group.update()
    ladder_group.draw(screen)
    ladder_group.update()
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
counter_text = 1
AUDIOIMG = pygame.image.load('img/DIALOGO.png')
AUDIOIMG2 = pygame.image.load('img/npctalk.png')
fontdiag= pygame.font.Font('font/Fortnite.ttf', 27)
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
counter_dialog = 5
counter_dialog1 = 1
counter_dialog2 = 0
#dialogs
dialog1 = pygame.mixer.Sound('music/AUDIOS FINAL/CABAÑA ANTIGUA GRECIA.mp3')
dialog2 = pygame.mixer.Sound('music/AUDIOS FINAL/NPC QUEST.mp3')
dialog3 = pygame.mixer.Sound('music/AUDIOS FINAL/NPC FINISH.mp3')
dialog4 = pygame.mixer.Sound('music/AUDIOS FINAL/QUEST FINAL.mp3')


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
        pygame.mixer.music.set_volume(0.5)
        # update player actions
        if stairsup() == False:
            GRAVITY = 0.75
        if counter_text == 0:
            textfade('BACK TO GREECE', 8, (0, 250),
                     (255, 255, 255))
            counter_text += 1
        if player.alive:
            if counter_dialog == 0:
                pygame.mixer.music.set_volume(0.1)
                screen.blit(AUDIOIMG, (0, 0))
                dialog1.play()
                time.sleep(1)
                dialog('UNA PEQUENA CABANA EN LA ANTIGUA GRECIA, HAY ALGO MUY', 13, (200, 450), (255, 255, 255))
                dialog('MAL CON TODO ESTO, CREO QUE TENEMOS PROBLEMAS CON LA ', 13, (200, 500), (255, 255, 255))
                dialog('SIMULACION ESPACIOTEMPORAL, EXPLORA UN POCO EL LUGAR,', 13, (200, 550), (255, 255, 255))
                dialog('LOS DATOS HISTORICOS PARECEN ESTAR CORRECTOS, INVESTIGA', 13, (200, 600), (255, 255, 255))
                screen.blit(AUDIOIMG, (0, 0))
                dialog('UN POCO Y AGREGALOS A LA ENCICLOPEDIA, TE INFORMARE', 13, (200, 450), (255, 255, 255))
                dialog('DEL ESTATUS DE LA MISION SI HAY CUALQUIER NOVEDAD', 13, (200, 500),(255, 255, 255))

                counter_dialog += 1
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
                text1 = fontcoin.render(str('PUSH TO TALK').zfill(3), 1, (0, 0, 0))
                screen.blit(text1, (208, 460))
                text = fontcoin.render(str('PUSH TO TALK').zfill(3), 1, (255, 255, 255))
                screen.blit(text, (210, 460))
            elif pygame.sprite.groupcollide(player_group, door_group, False, False):
                player.update_action(0)
                num_of_frames = len(os.listdir(f'img/tecla'))
                img = pygame.image.load(f'img/tecla/{0}.png')
                img1 = pygame.transform.scale(img, (50, 50))
                screen.blit(img1, (150, 450))
                pygame.display.update()
                text1 = fontcoin.render(str('Push to enter').zfill(3), 1, (0, 0, 0))
                screen.blit(text1, (208, 460))
                text = fontcoin.render(str('Push to enter').zfill(3), 1, (255, 255, 255))
                screen.blit(text, (210, 460))
            else:
                player.update_action(0)  # 0: idle

            screen_scroll= player.move(moving_left, moving_right)
        else:
            if counter_dialog1 == 2:
                pygame.quit()
                subprocess.call(["python", "RPGS.py"])
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
                # create empty tile list
                world_data = []
                for row in range(ROWS):
                    r = [-1] * COLS
                    world_data.append(r)
                # load in level data and create world
                with open(f'level{level}_data.csv', newline='') as csvfile:
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
                if counter_dialog1 == 0:
                    pygame.mixer.music.set_volume(0.1)
                    screen.blit(AUDIOIMG, (0, 0))
                    dialog2.play()
                    dialog('PARECES PERDIDO CHICO, ESTAS BUSCANDO ALGO PARTICULAR', 13, (200, 450), (255, 255, 255))
                    dialog('DE HECHO, CREO QUE ME PUEDES SER DE AYUDA. PODRIAS ', 13, (200, 500), (255, 255, 255))
                    dialog('BUSCAR EN LAS CASAS, UNAS ESCRITURAS, ESTOY TRABAJANDO', 13, (200, 550), (255, 255, 255))
                    dialog('EN ALGO QUE PODRIA CAMBIAR EL CURSO DE LA HISTORIA', 13, (200, 600), (255, 255, 255))
                    screen.blit(AUDIOIMG, (0, 0))
                    counter_dialog1 += 1
                elif counter_dialog1 == 1:
                    pygame.mixer.music.set_volume(0.1)
                    screen.blit(AUDIOIMG2, (0, 0))
                    dialog3.play()
                    dialog('UFF ME HAS SALVADO DE UNA, ESTAS ESCRITURAS SERAN', 13, (200, 450), (255, 255, 255))
                    dialog('PRESERVADAS EN LA BIBLIOTECA DE ALEJANDRIA ', 13, (200, 500), (255, 255, 255))
                    screen.blit(AUDIOIMG, (0, 0))
                    dialog4.play()
                    dialog('OYE TENEMOS UNA INTERRUPCION TEMPORAL MUY GRAVE', 13, (200, 450), (255, 255, 255))
                    dialog('TIENES QUE DESHACERTE DE ESE PAPEL, NO PUEDES', 13, (200, 500), (255, 255, 255))
                    dialog('INTERVENIR EN LA HISTORIA, DESTRUYE ESE OBJETO', 13, (200, 550), (255, 255, 255))
                    dialog('DE INMEDIATO', 13, (200, 600), (255, 255, 255))
                    counter_dialog1 += 1
                    if counter_dialog2 == 0:
                        textfade('TIRATE DEL MAPA', 8, (0, 250),
                                 (255, 255, 255))
                        counter_dialog2 += 1
            if event.key == pygame.K_x and pygame.sprite.groupcollide(player_group, door_group, False, False):
                subprocess.call(["python", "INSIDE.py"])

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
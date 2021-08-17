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
root = 'tiles/darktiles'
TILE_TYPES = len(os.listdir(root))

# define player action variables
moving_left = False
moving_right = False
font= pygame.font.Font('font/Early GameBoy.ttf', 20)
fontcoin= pygame.font.Font('font/Early GameBoy.ttf', 29)
#music
pygame.mixer.music.load('music/themes/dark.mp3')
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1, 0, 0)
Coin_sound = pygame.mixer.Sound('music/acid.mp3')
Coin_sound.set_volume(0.5)
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
for x in range(1, TILE_TYPES):
    if x >= 5 and x <= 7:
        img = pygame.image.load(f'{root}/{x}.png').convert_alpha()
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)
    elif x >= 9 and x <= 10:
        img = pygame.image.load(f'{root}/{x}.png').convert_alpha()
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
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
death_fade = ScreenFade(2, BLACK, 50)
#img
mountain_img1 = pygame.image.load('img/Background/BackGround01.png').convert_alpha()
mountain_img = pygame.transform.scale(mountain_img1, (800, 200))
mountain_img2 = pygame.image.load('img/Background/BackGround02.png').convert_alpha()
mountain_img3 = pygame.transform.scale(mountain_img2, (400, 640))
mountain_img5 = pygame.image.load('img/Background/Mist.png').convert_alpha()
mountain_img4 = pygame.transform.scale(mountain_img5, (800, 200))

def draw_bg():
    screen.fill((128,128,128))
    screen.blit(mountain_img4, (0, 400))
    screen.blit(mountain_img, (0, 500))



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
        if self.char_type == 'darkplayer':
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
        if self.char_type == 'moon':
            if player.alive == True:
                self.update_animation()
                self.update_action(0)
        else:
            if player.alive == True:
                self.update_animation()
                self.update_action(0)
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
                    if tile >= 4 and tile <= 6:
                        self.obstacle_list.append(tile_data)
                    elif tile == 3 or tile ==8:
                        ladder = Ladder(img, x * TILE_SIZE, y * TILE_SIZE)
                        ladder_group.add(ladder)
                    elif tile == 9:
                        coins = coin('Fire', x * TILE_SIZE, y * TILE_SIZE + 40, 1)
                        coins_group.add(coins)
                    else:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
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
        self.rect.topleft = (x, y)

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
        self.rect.topleft = (x , y)

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
player = Soldier('darkplayer', 200, 600, 2.92, 5)
moon = coin('moon',500,50,1)
fire = coin('fire', 100, 595, 1)
coins_group.add(fire)
player_group = pygame.sprite.Group()
player_group.add(player)


#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'leveldata/dark.csv', newline='') as csvfile:
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
    moon.draw()
    moon.update()
    house_group.draw(screen)
    house_group.update()
    decoration_group.draw(screen)
    decoration_group.update()
    world.draw()
    player.update_animation()
    coins_group.update()
    coins_group.draw(screen)

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
dialog1 = pygame.mixer.Sound('music/AUDIOS FINAL/DARK.mp3')
dialog2 = pygame.mixer.Sound('music/AUDIOS FINAL/DARK2.mp3')
dialog3 = pygame.mixer.Sound('music/AUDIOS FINAL/EINSTEIN BOSS.mp3')


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
        pygame.mixer.music.set_volume(0.4)
        if counter_text == 0:
            textfade('COLLECT ALL ', 8, (120, 150), (255, 255, 255))
            textfade('TOXICS ', 8, (250, 275), (57, 255, 20))
            counter_text += 1
        if stairsup() == False:
            GRAVITY = 0.75
        if player.alive:
            if counter_dialog == 0:
                pygame.mixer.music.set_volume(0.1)
                screen.blit(AUDIOIMG, (0, 0))
                dialog1.play()
                time.sleep(1)
                dialog('OHH ESPERA, OTRA INTERRUPCION TEMPORAL, MIRA MIRA,', 10, (200, 450), (255, 255, 255))
                dialog('EL APOCALIPSIS QUE HUBIERA CAUSADO EL MAL USO DE', 11, (200, 500), (255, 255, 255))
                dialog('LA CIENCIA, PARECE DE CIENCIA FICCION, RECOGE LOS ', 12, (200, 550), (255, 255, 255))
                dialog('RESTOS DE RADIACION TAL VEZ NOS AYUDE A SALIR DE AQUI', 12, (200, 600), (255, 255, 255))
                screen.blit(AUDIOIMG, (0, 0))
                counter_dialog += 1
            if coins_score == 8 and counter_dialog == 1:
                pygame.mixer.music.set_volume(0.1)
                screen.blit(AUDIOIMG, (0, 0))
                dialog2.play()
                time.sleep(1)
                dialog('NO TODO LO QUE TIENE QUE VER CON FISICA NUCLEAR ES', 10, (200, 450), (255, 255, 255))
                dialog('MALO, MIRA NOS REGALO UNA FORMA DE OBTENER ENERGIA', 11, (200, 500), (255, 255, 255))
                dialog('DE FORMA LIMPIA, LA ENERGIA NUCLEAR NOS HA LLEVADO', 12, (200, 550), (255, 255, 255))
                dialog('LEJOS, INCLUSO A INTENTAR HACER UN SOL EN LA TIERRA', 12, (200, 600), (255, 255, 255))
                screen.blit(AUDIOIMG, (0, 0))
                dialog('LOS HUMANOS NO TIENEN LIMITES', 10, (200, 450), (255, 255, 255))
                counter_dialog += 1
            if coins_score == 11 and counter_dialog == 2:
                pygame.mixer.music.set_volume(0.1)
                screen.blit(AUDIOIMG, (0, 0))
                dialog3.play()
                time.sleep(1)
                dialog('OYE RECUERDA, NO TE LA PONDRA FACIL, DOMINA EL', 10, (200, 450), (255, 255, 255))
                dialog('ESPACIO TIEMPO MEJOR QUE NADIE, TRAE LOS', 11, (200, 500), (255, 255, 255))
                dialog('CONOCIMIENTOS DE EINSTEIN A LA HISTORIA MODERNA', 12, (200, 550), (255, 255, 255))
                pygame.quit()
                subprocess.call(["python", "BOSS BATTLE 3.py"])

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
                text1 = fontcoin.render(str('Push to enter').zfill(3), 1, (0, 0, 0))
                screen.blit(text1, (208, 460))
                text = fontcoin.render(str('Push to enter').zfill(3), 1, (255, 255, 255))
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
                    b_img = pygame.image.load(f'img/darkplayer/Death/{i}.png').convert_alpha()
                    b1_img = pygame.transform.scale(b_img, (400, 350))
                    b_img2 = pygame.image.load(f'img/background/4 - copia.png').convert_alpha()
                    screen.blit(b_img2,(-320,0))
                    screen.blit(b1_img, (250, 250))
                    time.sleep(0.2)
                    pygame.display.update()
                time.sleep(0.5)
                coins_score = 0
                player.restart()
                decoration_group.empty()
                ladder_group.empty()
                death_fade.fade_counter = 0
                # create empty tile list
                world_data = []
                for row in range(ROWS):
                    r = [-1] * COLS
                    world_data.append(r)
                # load in level data and create world
                with open(f'leveldata/dark.csv', newline='') as csvfile:
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
                mixer.music.pause()
                pygame.quit()
                subprocess.call(["python", "TOWN.py"])

            if event.key == pygame.K_x and pygame.sprite.groupcollide(player_group, door_group, False, False):
                print('entering')

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

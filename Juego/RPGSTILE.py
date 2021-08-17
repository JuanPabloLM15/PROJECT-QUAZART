import pygame
import button
import csv
import os
import time
import subprocess

pygame.init()

clock = pygame.time.Clock()
FPS = 60

#game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 0
SIDE_MARGIN = 0

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')


#define game variables
ROWS = 150
MAX_COLS = 150
TILE_SIZE = 40
root = 'img/RPG MEJOR'
TILE_TYPES = len(os.listdir(root))
level = 7
current_tile = 0
scroll_left = False
scroll_right = False
scroll_up = False
scroll_down = False
scroll = 0
vscroll = 0
scroll_speed = 0.25
player_speed = 1
scale = 2

pygame.mixer.music.load('music/themes/rpgs2.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1, 0, 0)

#load images

#store tiles in a list
img_list = []
for x in range(1, TILE_TYPES+1):
	if x >= 76 and x <= 153:
		img = pygame.image.load(f'{root}/c ({x}).png').convert_alpha()
		img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
		img_list.append(img)
	else:
		img = pygame.image.load(f'{root}/c ({x}).png').convert_alpha()
		img1 = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
		img_list.append(img1)

#define colours
GREEN = (109, 247, 177)
WHITE = (255, 255, 255)
RED = (200, 25, 25)


#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)

#create function for drawing background
def draw_bg():
    screen.fill(GREEN)

#function for drawing the world tiles
def draw_world():
    with open('leveldata/rpg2.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE - vscroll))

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, vspeed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.vspeed = vspeed
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Attack', 'Death']
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
        self.rect.center = (x+ scroll, y + vscroll)
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
        self.vel_y += 0
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

    def pos_update(self):
        self.rect.x += self.speed
        self.rect.y += self.vspeed
    def draw(self):
        if self.flip == False and self.action == 1:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x- 14,  self.rect.y))
            pygame.display.update()
        else:
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

fontdiag= pygame.font.Font('font/Fortnite.ttf', 30)
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
counter_dialog1 = 0

#dialogs
AUDIOIMG = pygame.image.load('img/DIALOGO.png')
MARIEDIAG = pygame.image.load('img/mariediag.png')
dialog1 = pygame.mixer.Sound('music/AUDIOS FINAL/EINSTEIN.mp3')
dialog2 = pygame.mixer.Sound('music/LADRON.mp3')

player = Soldier('player', 100, 350, 3, 0, 0)
run = True
while run:
    pygame.mixer.music.set_volume(0.3)
    clock.tick(FPS)
    draw_bg()
    draw_world()
    player.draw()
    player.update_animation()
    player.pos_update()
    if counter_dialog == 0:
        pygame.mixer.music.set_volume(0.1)
        screen.blit(AUDIOIMG, (0, 0))
        dialog1.play()
        time.sleep(1)
        dialog('¿QUE PASA NO RECONOCES ESTA EPOCA?, DEBES ESTAR ', 10, (200, 450), (255, 255, 255))
        dialog('BROMEANDO, EL ANO MILAGROSO, EN ESTA EPOCA APARECERA', 11, (200, 500), (255, 255, 255))
        dialog('UNO DE LAS REVOLUCIONES MAS IMPORTANTE DE LA FISICA', 12, (200, 550), (255, 255, 255))
        dialog('PERO PRIMERO TENEMOS QUE BUSCAR UN NUEVO ELEMENTO', 12, (200, 600), (255, 255, 255))
        screen.blit(AUDIOIMG, (0, 0))
        dialog('PARA ESTA FECHA, NUESTRO MEDIDOR NECESITA RADIO', 12, (200, 450), (255, 255, 255))
        dialog('POSIBLEMENTE SABES A QUIEN TIENES QUE BUSCAR', 12, (200, 500), (255, 255, 255))
        dialog('ENCUENTRA AL MATRIMONIO CURRIE Y TRAE EL RADIO', 12, (200, 550), (255, 255, 255))

        counter_dialog += 1
    #scroll the map
    if scroll_left == True and scroll > 0:
        scroll -= player_speed
    if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += player_speed
    if scroll_up == True and vscroll > 0:
        vscroll -= player_speed
    if scroll_down == True and vscroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        vscroll += player_speed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.update_action(1)
                player.vspeed = -player_speed
                scroll_up = True
            if event.key == pygame.K_s:
                player.update_action(1)
                player.vspeed = player_speed
                scroll_down = True
            if event.key == pygame.K_a:
                player.flip = True
                player.update_action(1)
                player.speed = -player_speed
                scroll_left = True
            if event.key == pygame.K_d:
                player.flip = False
                player.update_action(1)
                player.speed = player_speed
                scroll_right = True
            if event.key == pygame.K_x:
                pygame.mixer.music.set_volume(0.1)
                if counter_dialog1 == 0:
                    screen.blit(MARIEDIAG, (0, 0))
                    dialog2.play()
                    time.sleep(1)
                    dialog('OYE TU LADRON QUE ES LO QUE', 10, (400, 450), (255, 255, 255))
                    dialog('INTENTAS HACER, DEVUELVE MI', 11, (400, 500), (255, 255, 255))
                    dialog('EXPERIMENTO DE INMEDIATO', 12, (400, 550), (255, 255, 255))
                time.sleep(1)
                pygame.quit()
                subprocess.call(["python", "BOSS BATTLE 2.py"])

            if event.key == pygame.K_UP:
                scroll_up = True
                player.vspeed = player_speed
            if event.key == pygame.K_DOWN:
                scroll_down = True
                player.vspeed = -player_speed
            if event.key == pygame.K_LEFT:
                scroll_left = True
                player.speed = player_speed
            if event.key == pygame.K_RIGHT:
                scroll_right = True
                player.speed = -player_speed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                player.update_action(0)
                player.speed = 0
                scroll_left = False
            if event.key == pygame.K_d:
                player.speed = 0
                scroll_right = False
                player.update_action(0)
            if event.key == pygame.K_w:
                player.update_action(0)
                player.vspeed = 0
                scroll_up = False
            if event.key == pygame.K_s:
                player.update_action(0)
                player.vspeed = 0
                scroll_down = False

            if event.key == pygame.K_UP:
                scroll_up = False
                player.vspeed = 0
            if event.key == pygame.K_DOWN:
                scroll_down = False
                player.vspeed = 0
            if event.key == pygame.K_LEFT:
                scroll_left = False
                player.speed = 0
            if event.key == pygame.K_RIGHT:
                scroll_right = False
                player.speed = 0

    pygame.display.update()

pygame.quit()


import pygame
import os
import button
import time
import subprocess

pygame.init()

clock = pygame.time.Clock()
fps = 60

#music and sounds
hit_sound = pygame.mixer.Sound('music/bossbattle/hit.wav')
heal_sound = pygame.mixer.Sound('music/bossbattle/heal.wav')
pot_sound = pygame.mixer.Sound('music/bossbattle/pot.mp3')
punch_sound = pygame.mixer.Sound('music/bossbattle/punch.mp3')
sword_sound = pygame.mixer.Sound('music/bossbattle/swordhit.mp3')
arrow_sound = pygame.mixer.Sound('music/bossbattle/arrow.mp3')
theme = pygame.mixer.music.load('music/BOSSE.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0, 0)


#game window
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel
level = 1
timer = 60
#BG
templist = []
num_of_frames = len(os.listdir(f'img/background/boss_{level}'))
for i in range(num_of_frames):
	img = pygame.image.load(f'img/background/boss_{level}/{i}.png')
	img1 = pygame.transform.scale(img, (800, 400))
	templist.append(img1)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Battle')

REDCOLOR = (221, 36, 36)
BLUECOLOR = (0, 168, 192)
player_hits = 0
player_life = 0

#load images
img0 = pygame.image.load(f'Buttom/0.png')
img1 = pygame.image.load(f'Buttom/1.png')
img2 = pygame.image.load(f'Buttom/2.png')
img3 = pygame.image.load(f'Buttom/4.png')
button0 = button.Button(20, 425, img0, 2)
button1 = button.Button(150, 425, img1, 2)
button2 = button.Button(275, 425, img2, 2)
button3 = button.Button(450, 370, img3, 1.5)
button4 = button.Button(525, 370, img3, 1.5)
button5 = button.Button(600, 370, img3, 1.5)
button6 = button.Button(675, 370, img3, 1.5)
button7 = button.Button(450, 465, img3, 1.5)
button8 = button.Button(525, 465, img3, 1.5)
button9 = button.Button(600, 465, img3, 1.5)
button10 = button.Button(675, 465, img3, 1.5)
#background image
#panel image
panel_img = pygame.image.load('img/Icons/panel.png').convert_alpha()


#function for drawing background
def draw_bg():
	screen.blit(background_img, (0, 0))


#function for drawing panel
def draw_panel():
	screen.blit(panel_img, (0, screen_height - bottom_panel))



#fighter class
class Fighter():
	def __init__(self, x, y, name, max_hp, strength, potions, scale, pos2):
		self.name = name
		self.pos2 = pos2
		self.scale = scale
		self.max_hp = max_hp
		self.hp = max_hp
		self.strength = strength
		self.start_potions = potions
		self.potions = potions
		self.alive = True
		self.animation_list = []
		self.frame_index = 0
		self.action = 0#0:idle, 1:attack, 2:hurt, 3:dead
		self.update_time = pygame.time.get_ticks()
		#load idle images
		temp_list = []
		if self.name == 'player_battle':
			animation_types = ['Idle', 'Attack', 'Attack2', 'Bow', 'Eat', 'Potion_1', 'Potion_2', 'Victory']
			for animation in animation_types:
				# reset temporary list of images
				temp_list = []
				# count number of files in the folder
				num_of_frames = len(os.listdir(f'img/{self.name}/{animation}'))
				for i in range(num_of_frames):
					img = pygame.image.load(f'img/{self.name}/{animation}/{i}.png')
					img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
					temp_list.append(img)
				self.animation_list.append(temp_list)
		else:
			num_of_frames = len(os.listdir(f'img/{self.name}/Idle'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.name}/Idle/{i}.png')
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)
			#load attack images
			temp_list = []
			num_of_frames = len(os.listdir(f'img/{self.name}/Attack'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'img/{self.name}/Attack/{i}.png')
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
		self.animation_list.append(temp_list)
		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)


	def update(self):
		if self.name == 'player_battle':
			animation_cooldown = 150
			# handle animation
			# update image
			self.image = self.animation_list[self.action][self.frame_index]
			# check if enough time has passed since the last update
			if pygame.time.get_ticks() - self.update_time > animation_cooldown:
				self.update_time = pygame.time.get_ticks()
				self.frame_index += 1
			# if the animation has run out then reset back to the start
			if self.frame_index >= len(self.animation_list[self.action]):
				self.frame_index = 0
		else:
			animation_cooldown = 100
			#handle animation
			#update image
			self.image = self.animation_list[self.action][self.frame_index]
			#check if enough time has passed since the last update
			if pygame.time.get_ticks() - self.update_time > animation_cooldown:
				self.update_time = pygame.time.get_ticks()
				self.frame_index += 1
			#if the animation has run out then reset back to the start
			if self.frame_index >= len(self.animation_list[self.action]):
				self.frame_index = 0




	def draw(self):

		if self.name == 'player_battle':
			if self.action == 0:
				screen.blit(self.image, (100, 0))
			elif self.action == 1:
				screen.blit(self.image, (100, 100))
			elif self.action == 2:
				screen.blit(self.image, (100, -100))
			elif self.action == 3:
				screen.blit(self.image, self.rect)
			elif self.action == 4:
				screen.blit(self.image, self.rect)
			elif self.action == 5:
				screen.blit(self.image, self.rect)
			elif self.action == 6:
				screen.blit(self.image, self.rect)
			elif self.action == 7:
				screen.blit(self.image, self.rect)
		else:
			if self.action == 1:
				screen.blit(self.image, self.pos2)
			else:
				screen.blit(self.image, self.rect)

knight = Fighter(200, 260, 'player_battle', 30, 10, 3, 5, (0,0))
POTS = Fighter(600, 450, 'POTIONS', 30, 10, 3, 0.3, (0,0))
BLUE = Fighter(200, 60, 'BLUE', 30, 10, 3, 1, (0,0))
RED = Fighter(600, 60, 'RED', 30, 10, 3, 1, (0,0))
finn0 = pygame.image.load('img/marco/finn.png')
finn = pygame.transform.scale(finn0, (100, 100))
fontext= pygame.font.Font('font/Fortnite.ttf', 45)

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
#dialogs
AUDIOIMG = pygame.image.load('img/DIALOGO.png')
dialog1 = pygame.mixer.Sound('music/AUDIOS FINAL/EINSTEIN FINAL.mp3')


if level == 0:
	bandit = Fighter(500, 280, f'boss {level}', 20, 6, 1, 1, (0,-275))
elif level == 1:
	bandit = Fighter(350, 280, f'boss {level}', 20, 6, 1, 1, (375,-50))
elif level == 2:
	bandit = Fighter(650, 100, f'boss {level}', 20, 6, 1, 1, (375,-50))
elif level == 3:
	bandit = Fighter(200, 280, f'boss {level}', 20, 6, 1, 1, (375,-50))
elif level == 4:
	bandit = Fighter(500, 175, f'boss {level}', 20, 6, 1, 1, (0, -300))
run = True
while run:

	clock.tick(fps)
	num_of_frames = len(os.listdir(f'img/background/boss_{level}'))
	for i in range(num_of_frames):
		screen.blit(templist[i], (0, 0))
		#draw panel
		draw_panel()
		if button0.draw(screen):
			sword_sound.play()
			bandit.action = 1
			bandit.frame_index = 0
			knight.frame_index = 0
			knight.action = 2
			player_hits += 1
		if button1.draw(screen):
			punch_sound.play()
			bandit.action = 0
			bandit.frame_index = 0
			knight.frame_index = 0
			knight.action = 1
			player_hits += 1
		if button2.draw(screen):
			arrow_sound.play()
			knight.frame_index = 0
			knight.action = 3
			bandit.action = 1
			bandit.frame_index = 0
			player_hits += 1
		if button3.draw(screen):
			pot_sound.play()
			knight.frame_index = 0
			knight.action = 6
			player_life -= 1
			heal_sound.play()
		if button4.draw(screen):
			pot_sound.play()
			knight.frame_index = 0
			knight.action = 4
			player_life -= 1
			heal_sound.play()
		if button5.draw(screen):
			pot_sound.play()
			knight.frame_index = 0
			knight.action = 5
			player_life -= 1
			heal_sound.play()
		if button6.draw(screen):
			pot_sound.play()
			knight.frame_index = 0
			knight.action = 4
			player_life -= 1
			heal_sound.play()
		if button7.draw(screen):
			pot_sound.play()
			knight.frame_index = 0
			knight.action = 6
			player_life -= 1
			heal_sound.play()
		if button8.draw(screen):
			pot_sound.play()
			knight.frame_index = 0
			knight.action = 5
			player_life -= 1
			heal_sound.play()
		if button9.draw(screen):
			pot_sound.play()
			knight.frame_index = 0
			knight.action = 4
			player_life -= 1
			heal_sound.play()
		if button10.draw(screen):
			pot_sound.play()
			knight.frame_index = 0
			knight.action = 6
			player_life -= 1
			heal_sound.play()
			heal_sound.stop()
		#player & enemy
		RED.draw()
		RED.update()
		BLUE.draw()
		BLUE.update()
		knight.update()
		knight.draw()
		pygame.draw.rect(screen, REDCOLOR, (471, 53, 12 * player_hits + 3 * player_hits, 12))
		pygame.draw.rect(screen, REDCOLOR, (474, 65, 12 * player_hits + 3 * player_hits, 3))
		pygame.draw.rect(screen, BLUECOLOR, (int(330 - (12 * player_life + 3 * player_life)), 53, 12 * player_life + 3 * player_life, 12))
		pygame.draw.rect(screen, BLUECOLOR, (326 - (12 * player_life + 3 * player_life), 65, 12 * player_life + 3 * player_life, 3))
		bandit.update()
		bandit.draw()
		POTS.draw()
		POTS.update()
		text = fontext.render(str(int(timer)).zfill(2), 1, (0, 0, 0))
		screen.blit(text, (383, 47))
		text1 = fontext.render(str(int(timer)).zfill(2), 1, (255, 255, 255))
		screen.blit(text1, (380, 50))

		if player_life >= 12:
			screen.fill(REDCOLOR)
			for i in range(5):
				b_img = pygame.image.load(f'img/player/Death/{i}.png').convert_alpha()
				b1_img = pygame.transform.scale(b_img, (400, 350))
				b_img2 = pygame.image.load(f'img/background/4.png').convert_alpha()
				screen.blit(b_img2, (-320, 0))
				screen.blit(b1_img, (250, 250))
				time.sleep(0.2)
				pygame.display.update()
			pygame.quit()
			subprocess.call(["python", "DARK.py"])
		if player_hits >= 12:
			pygame.mixer.music.set_volume(0.1)
			if counter_dialog == 0:
				screen.blit(AUDIOIMG, (0, -90))
				dialog1.play()
				time.sleep(1)
				dialog('PERFECTO, CADA VEZ MAS CERCA, ENERGIA NUCLEAR', 13, (200, 400), (255, 255, 255))
				dialog('AL PARECER EL HOMBRE SIEMPRE HA ESTADO ', 13, (200, 450), (255, 255, 255))
				dialog('INTERASADO EN LA ENERGIA, DE HECHO SABIAS QUE', 13, (200, 500), (255, 255, 255))
				dialog('HAY UNA ESCALA QUE MIDE EL AVANCE TECNOLOGICO', 13, (200, 550), (255, 255, 255))
				screen.blit(AUDIOIMG, (0, -90))
				dialog('DE UNA CIVILIZACION BASADA EN ENERGIA, LA ', 13, (200, 400), (255, 255, 255))
				dialog('ESCALA DE KARDASHOV, 3 TIPOS DE CIVILIZACIONES', 13, (200, 450), (255, 255, 255))
				dialog('NIVEL I EL DOMINIO LA ENERGIA A PARTIR', 13, (200, 500), (255, 255, 255))
				dialog('DE LOS RECURSOS DEL PLANETA DE ORIGEN, EL TIPO', 13, (200, 550), (255, 255, 255))
				screen.blit(AUDIOIMG, (0, -90))
				dialog('II LA ENERGIA DE TODO EL SISTEMA PLANETARIO', 13, (200, 400), (255, 255, 255))
				dialog('Y EL TIPO III DE TODA UNA GALAXIA', 13, (200, 450), (255, 255, 255))
				dialog('LASTIMA QUE SEGUIMOS SIENDO EL TIPO 0', 13, (200, 500), (255, 255, 255))
				counter_dialog += 1
				time.sleep(4)
				pygame.quit()
				subprocess.call(["python", "FOREST.py"])

		timer -= 0.01
		pygame.display.update()
	player_life += 0.3


	pygame.display.update()
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RIGHT:
				level +=1
				if level == 0:
					bandit = Fighter(500, 280, f'boss {level}', 20, 6, 1, 1, (0,0))
				elif level == 1:
					bandit = Fighter(350, 280, f'boss {level}', 20, 6, 1, 1, (0,0))
				elif level == 2:
					bandit = Fighter(650, 100, f'boss {level}', 20, 6, 1, 1, (0,0))
				elif level == 3:
					bandit = Fighter(200, 280, f'boss {level}', 20, 6, 1, 1, (0,0))
				elif level == 4:
					bandit = Fighter(500, 175, f'boss {level}', 20, 6, 1, 1, (260, 20))
			elif event.key == pygame.K_LEFT:
				level -=1
				if level == 0:
					bandit = Fighter(500, 280, f'boss {level}', 20, 6, 1, 1, (0,0))
				elif level == 1:
					bandit = Fighter(350, 280, f'boss {level}', 20, 6, 1, 1, (0,0))
				elif level == 2:
					bandit = Fighter(650, 100, f'boss {level}', 20, 6, 1, 1, (0,0))
				elif level == 3:
					bandit = Fighter(200, 280, f'boss {level}', 20, 6, 1, 1, (0,0))
				elif level == 4:
					bandit = Fighter(500, 175, f'boss {level}', 20, 6, 1, 1, (260, 20))
	pygame.display.update()

pygame.quit()


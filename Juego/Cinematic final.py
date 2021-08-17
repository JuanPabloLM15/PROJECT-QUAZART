import pygame
import os
import button
import time
import subprocess

pygame.init()

clock = pygame.time.Clock()
fps = 60
#cinematic_speed = 10

#game window

screen_width = 1000
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('PROJECT QUASART')

class CinematicSlide():
    def __init__(self, screen_start,screen_end, root, cinematic_speed, format):
        self.screen_start = screen_start
        self.root = root
        self.cinematic_speed = cinematic_speed
        self.screen_end = screen_end
        self.format = format

    def draw(self):
        num_of_frames = len(os.listdir(f'{self.root}'))
        start = self.screen_start
        if self.screen_start >=0:
            while self.screen_start <= (self.screen_end - (num_of_frames * self.cinematic_speed)):
                for i in range(1, num_of_frames):
                    img = pygame.image.load(f'{self.root}/c ({i}).{self.format}')
                    img1 = pygame.transform.scale(img, (screen_width, screen_height))
                    screen.blit(img1, (0-self.screen_start, 0))
                    pygame.display.update()
                    time.sleep(0.1)
                    self.screen_start += self.cinematic_speed
                    pygame.display.update()
        else:
            while self.screen_start <= (self.screen_end - (num_of_frames * self.cinematic_speed)):
                for i in range(1, num_of_frames):
                    img = pygame.image.load(f'{self.root}/c ({i}).{self.format}')
                    img1 = pygame.transform.scale(img, (screen_width, screen_height))
                    screen.blit(img1, (self.screen_start, 0))
                    pygame.display.update()
                    time.sleep(0.1)
                    self.screen_start += self.cinematic_speed
                    pygame.display.update()
class CinematicStatic():
    def __init__(self, root, format):
        self.root = root
        self.format = format

    def draw(self):
        num_of_frames = len(os.listdir(f'{self.root}'))
        for i in range(1, num_of_frames):
            img = pygame.image.load(f'{self.root}/{i}.{self.format}')
            img1 = pygame.transform.scale(img, (screen_width, screen_height))
            screen.blit(img1, (0, 0))
            pygame.display.update()
            time.sleep(0.1)
class CinematicSlideStatic():
    def __init__(self, screen_start,screen_end, root, cinematic_speed, format, scale, update):
        self.screen_start = screen_start
        self.root = root
        self.cinematic_speed = cinematic_speed
        self.screen_end = screen_end
        self.format = format
        self.scale = scale
        self.update = update

    def draw(self):
        if self.screen_start >=0 and self.screen_start <= self.screen_end:
            while self.screen_start <= self.screen_end:
                num_of_frames = len(os.listdir(f'{self.root}'))
                for i in range(1, num_of_frames):
                    img = pygame.image.load(f'{self.root}/{i}.{self.format}')
                    img1 = pygame.transform.scale(img, self.scale)
                    screen.blit(img1, (self.screen_start, 0))
                    pygame.display.update()
                    time.sleep(self.update)
                    self.screen_start += self.cinematic_speed
                    pygame.display.update()
        else:
            while self.screen_start >= self.screen_end :
                num_of_frames = len(os.listdir(f'{self.root}'))
                for i in range(1, num_of_frames):
                    img = pygame.image.load(f'{self.root}/{i}.{self.format}')
                    img1 = pygame.transform.scale(img, self.scale)
                    screen.blit(img1, (self.screen_start, 0))
                    pygame.display.update()
                    time.sleep(self.update)
                    self.screen_start += self.cinematic_speed
                    pygame.display.update()
class CinematicStaticBG():
    def __init__(self, root, format, scale, coords, speed):
        self.root = root
        self.format = format
        self.scale = scale
        self.updateScore = 0
        self.coords = coords
        self.speed = speed
    def update(self):
        num_of_frames = len(os.listdir(f'{self.root}'))
        if self.updateScore < num_of_frames:
            self.updateScore+= 1
        else:
            self.updateScore = 1
    def draw(self):
        img = pygame.image.load(f'{self.root}/c ({self.updateScore}).{self.format}')
        img1 = pygame.transform.scale(img, self.scale)
        screen.blit(img1, self.coords)
        pygame.display.update()
        time.sleep(self.speed)

Creditos = pygame.image.load('img/Creditos.png')
pygame.mixer.music.load('music/credits.mp3')

class CinematicSlideStaticVertical():
    def __init__(self, screen_start,screen_end, root, cinematic_speed, format, scale, update):
        self.screen_start = screen_start
        self.root = root
        self.cinematic_speed = cinematic_speed
        self.screen_end = screen_end
        self.format = format
        self.scale = scale
        self.update = update

    def draw(self):
        if self.screen_start >=0 and self.screen_start <= self.screen_end:
            while self.screen_start <= self.screen_end:
                num_of_frames = len(os.listdir(f'{self.root}'))
                for i in range(1, num_of_frames):
                    img = pygame.image.load(f'{self.root}/c ({i}).{self.format}')
                    img1 = pygame.transform.scale(img, self.scale)
                    screen.blit(img1, (0, self.screen_start))
                    pygame.display.update()
                    time.sleep(self.update)
                    self.screen_start += self.cinematic_speed
                    pygame.display.update()

        else:
            while self.screen_start >= self.screen_end :
                num_of_frames = len(os.listdir(f'{self.root}'))
                for i in range(1, num_of_frames):
                    if i < 50 or i > 50:
                        img = pygame.image.load(f'{self.root}/c ({i}).{self.format}')
                        img1 = pygame.transform.scale(img, self.scale)
                        screen.blit(img1, (0, self.screen_start))
                        pygame.display.update()
                        time.sleep(self.update)
                        self.screen_start += self.cinematic_speed
                        screen.blit(Creditos, (0, 0))
                        pygame.display.update()
                    if i == 50 or i == 1:
                        img = pygame.image.load(f'{self.root}/c ({i}).{self.format}')
                        img1 = pygame.transform.scale(img, self.scale)
                        screen.blit(img1, (0, self.screen_start))
                        pygame.display.update()
                        time.sleep(self.update)
                        self.screen_start += self.cinematic_speed
                        screen.blit(Creditos, (0, 0))
                        pygame.display.update()
                        time.sleep(0.35)

#Cinematics
Cinematic_1 = CinematicStatic('cinematics/trans', 'png')
Cinematic_2 = CinematicStatic('cinematics/book', 'png')
Cinematic_3 = CinematicSlideStaticVertical(0, -500,'cinematics/credits', -1, 'png', (1000, 1500), 0.05)


#audio theme
narrator = pygame.mixer.Sound('music/audios/Grabación-_11_.mp3')
lluvia = pygame.mixer.Sound('music/continuara.mp3')
glitch = pygame.mixer.Sound('music/glitch.mp3')

narrator.set_volume(1)
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1, 0, 0)
run = True
while run:
    clock.tick(fps)
    Cinematic_2.draw()
    Cinematic_2.draw()
    Cinematic_2.draw()
    Cinematic_2.draw()
    Cinematic_3.draw()



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.quit()
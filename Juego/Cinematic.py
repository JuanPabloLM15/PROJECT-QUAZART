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
            img = pygame.image.load(f'{self.root}/c ({i}).{self.format}')
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
                    img = pygame.image.load(f'{self.root}/c ({i}).{self.format}')
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
                    img = pygame.image.load(f'{self.root}/c ({i}).{self.format}')
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
                    img = pygame.image.load(f'{self.root}/c ({i}).{self.format}')
                    img1 = pygame.transform.scale(img, self.scale)
                    screen.blit(img1, (0, self.screen_start))
                    pygame.display.update()
                    time.sleep(self.update)
                    self.screen_start += self.cinematic_speed
                    pygame.display.update()
#Cinematics
Cinematic_1 = CinematicSlide(0, 250, 'cinematics/introciudad', 2, 'png')
Cinematic_2 = CinematicStatic('cinematics/smoking', 'gif')
Cinematic_3 = CinematicStatic('cinematics/smoke 2', 'gif')
Cinematic_4 = CinematicSlideStatic(0, -300,'cinematics/cyber', -0.5, 'gif', (1400, 600), 0.02)
Cinematic_5 = CinematicStatic('cinematics/cyber2', 'gif')
Cinematic_6 = CinematicStatic('cinematics/cyber3', 'gif')
#screen_start,screen_end, root, cinematic_speed, format, scale)
Cinematic_7 = CinematicSlideStatic(0, 250,'cinematics/apartament', 1, 'gif', (1000, 600), 0.02)
Cinematic_8 = CinematicSlideStaticVertical(0, -500,'cinematics/trainread', -1, 'gif', (1000, 1500), 0.01)
Cinematic_9 = CinematicSlideStaticVertical(0, -600,'cinematics/telescope', -1, 'gif', (1000, 1500), 0.01)
Cinematic_10 = CinematicStatic('cinematics/fire_greece', 'gif')
Cinematic_11 = CinematicStatic('cinematics/player 2', 'gif')
Cinematic_12 = CinematicStatic('cinematics/shutdown', 'gif')
#Images

vs = pygame.image.load(f'cinematics/Introciudad/c (1).png')
vs_ = pygame.transform.scale(vs, (screen_width, screen_height))

#audio theme
theme = pygame.mixer.music.load('music/themes/bioshock-soundtrack-01-the-ocean-on-his-shoulders.mp3')
narrator = pygame.mixer.Sound('music/audios/Grabación-_11_.mp3')
lluvia = pygame.mixer.Sound('music/lluvia.mp3')
glitch = pygame.mixer.Sound('music/glitch.mp3')
lluvia.set_volume(0.1)
narrator.set_volume(1)
pygame.mixer.music.set_volume(0.1)
run = True
while run:
    clock.tick(fps)
    pygame.mixer.music.play(-1, 0, 0)
    lluvia.play()
    Cinematic_1.draw()
    Cinematic_2.draw()
    Cinematic_2.draw()
    Cinematic_3.draw()
    Cinematic_3.draw()
    Cinematic_3.draw()
    lluvia.stop()
    Cinematic_4.draw()
    narrator.play()
    Cinematic_5.draw()
    Cinematic_6.draw()
    Cinematic_7.draw()
    Cinematic_8.draw()
    Cinematic_9.draw()
    Cinematic_9.draw()
    Cinematic_10.draw()
    Cinematic_10.draw()
    Cinematic_10.draw()
    Cinematic_10.draw()
    Cinematic_10.draw()
    Cinematic_10.draw()
    Cinematic_11.draw()
    Cinematic_11.draw()
    Cinematic_11.draw()
    Cinematic_11.draw()
    Cinematic_11.draw()
    glitch.play()
    Cinematic_12.draw()
    pygame.quit()
    subprocess.call(["python", "Avance 8.py"])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.quit()

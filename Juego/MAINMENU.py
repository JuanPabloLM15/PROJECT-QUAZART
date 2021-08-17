import pygame
import os
import button
import subprocess
pygame.init()

clock = pygame.time.Clock()
fps = 5

#game window

screen_width = 1000
screen_height = 600
#music
pygame.mixer.music.load('music/mainmenu/MAINMENUS.mp3')
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1, 0, 0)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('PROJECT QUASART')
#img
start_img = pygame.image.load('img/mainmenu/start_img.png').convert_alpha()
exit_img = pygame.image.load('img/mainmenu/exit_img.png').convert_alpha()
title = pygame.image.load(f'img/mainmenu/prueba.png')
title1 = pygame.transform.scale(title, (750, 280))

#create buttons
start_button = button.Button(350,375, start_img, 0.3)
exit_button = button.Button(310,450, exit_img, 0.3)

run = True

while run:
    clock.tick(fps)
    num_of_frames = len(os.listdir(f'img/mainmenu/intro'))
    for i in range(1, num_of_frames):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pygame.quit()
                subprocess.call(["python", "Cinematic.py", 'stdin=PIPE', 'stdout=PIPE', 'stderr=PIPE'])
        # gif background
        screen.blit(title1, (140, 50))
        pygame.display.update()
        img = pygame.image.load(f'img/mainmenu/intro/c ({i}).png')
        img1 = pygame.transform.scale(img, (1000, 600))
        screen.blit(img1, (0, 0))
        #if start_button.draw(screen):
            #run = False
        #if exit_button.draw(screen):
            #run = False
        if i > 80:
            screen.blit(title1, (150, 50))
            pygame.display.update()


        pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()
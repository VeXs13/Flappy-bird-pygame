import pip
import pygame 
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864 #define the width
screen_height = 936 #define the height

screen = pygame.display.set_mode((screen_width, screen_height)) #create the screen with W&H 
pygame.display.set_caption('Flappy Bird') #name of windows

#define font
font = pygame.font.SysFont('Bauhaus 93', 60)

#define colors
white = (255, 255, 255)

#game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150 #gap between 2 pipes
pipe_frequency = 1500 #milliseconds => 1 pipe every 1.5seconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

#load img
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')


def draw_text(text, font, text_color, x, y ):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score



class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):#create the bird Object
        pygame.sprite.Sprite.__init__(self)

        self.images = []
        self.index = 0
        self.counter = 0

        for num in range(1, 4): #loop that will alternate the 3 images
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)

        self.image = self.images[self.index]
        self.rect = self.image.get_rect()#creates a square around the image like a hitbox
        self.rect.center = [x, y]
        self.velocity = 0
        self.clicked = False
    
    def update(self): 

        #gravity
        if flying == True:
            self.velocity += 0.5 #falling speed

            if self.velocity > 8:#blocks velocity increment once on the ground
                self.velocity > 8

            if self.rect.bottom < 768: #prevents going under the map
                self.rect.y += int(self.velocity)

        if game_over == False:
            #jump + condition that prevents staying pressed on the mouse
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.velocity = -10
            
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            self.counter += 1
            swap_couldown = 10#time for sprite change

            if self.counter > swap_couldown:
        
                self.counter = 0
                self.index += 1

                if self.index >= len(self.images): #avoid an out of range, after 1 cycle, game crash
                    self.index = 0 

            self.image = self.images[self.index]
            
            self.image = pygame.transform.rotate(self.images[self.index], self.velocity * -2)#create a rotational movement
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)#if the bird hit the ground, is dead

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):#create the Pipe Object
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()

        if position == 1: #1 is for the top pipe
            self.image = pygame.transform.flip(self.image, False, True) #flip the pipe image
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1: #-1 is for the bottom pipe
            self.rect.topleft = [x, y + int(pipe_gap / 2)]
    
    def update(self):
        self.rect.x -= scroll_speed 

        #supp the pipe 
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()    
        self.rect.topleft =  (x, y)  

    def draw(self):

        action = False 

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check if mouse is over the button 
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2)) # x = 100 & y = screen / 2
bird_group.add(flappy)

#create restart button instance

button = Button(screen_width //2 - 50, screen_height //2 - 100, button_img)


run = True
while run: #main loop

    clock.tick(fps) #frame per second of the game

    screen.blit(bg, (0,0)) #background position

    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0: #putting true instead of false would make the bird or the pipes disappear
        game_over = True

    bird_group.draw(screen)
    bird_group.update() #display bird's animation
    pipe_group.draw(screen)



    screen.blit(ground_img, (ground_scroll,768)) #ground position

    #check score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, white, int(screen_width / 2), 20)

    #Game Over
    if flappy.rect.bottom > 768: #check if the bird hit the ground
        game_over = True
        flying = False


    if game_over == False and flying == True:

        #pipe generator
        time_now = pygame.time.get_ticks()

        if time_now - last_pipe > pipe_frequency:

            pipe_heigth = random.randint(-100, 100)
            bottom_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_heigth, -1) #-1 = position
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_heigth, 1)
            pipe_group.add(bottom_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        ground_scroll -= scroll_speed # -= scroll left, += scroll right, = not moving
        if abs(ground_scroll) > 35: #reset ground to have movement effect
            ground_scroll = 0

        pipe_group.update() #placing the update here allows you to stop the spawn in case of game over
    
    #check for game over and reset 
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()




    #in-game interaction
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:#stop the game by closing it
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
        

    pygame.display.update() #display bg 

pygame.quit()
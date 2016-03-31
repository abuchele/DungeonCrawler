import pygame
import time
import math
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION

from Dungeon import Dungeon
from terrainUtils import *



class DungeonModelView(object):
    def __init__(self, dungeon, screen, size):
        self.model = dungeon
        self.screen = screen
        self.size = size
        self.dispSize = (size[1],size[1])
        tht = 0.3
        self.blockSize = (50,48,15)
        self.playerPos = (36,36)
        self.screenBounds = (-size[1]/self.blockSize[0]/2, size[1]/self.blockSize[0]/2, -size[1]/self.blockSize[1]/2, size[1]/self.blockSize[1]/2)
        self.bigmap = pygame.Surface((size[0], size[0]))

        self.minimap = pygame.Surface((size[0]-size[1], size[0]-size[1]))
        for x in range(0,self.minimap.get_width()):
            for y in range(0,self.minimap.get_height()):
                self.minimap.set_at((x,y), self.model.getBlock(x*self.model.getWidth()/self.minimap.get_width(),
                    y*self.model.getHeight()/self.minimap.get_height()).color)

        self.font = pygame.font.SysFont("Times New Roman", 30, bold=True)
        

    def display(self):
        for dy in range(self.screenBounds[2], self.screenBounds[3]+1):    # draw all the blocks
            for dx in range(self.screenBounds[0], self.screenBounds[1]+1):
                block = self.model.getBlock(self.playerPos[0]+dx, self.playerPos[1]+dy)
                #try:
                self.bigmap.blit(block.sprite, ((dx-0.5)*self.blockSize[0]+self.dispSize[0]/2, (dy-0.5)*self.blockSize[1]+self.dispSize[1]/2))
                #except:
                #    print block
        self.screen.blit(self.bigmap, (0,0))

        pygame.draw.rect(self.screen, pygame.Color("black"), (self.size[1], 0, self.size[0]-self.size[1], self.size[1]))    # draw the background of the HUD

        self.screen.blit(self.minimap, (self.size[1],0))    # draw the minimap
        
        actionLog = self.font.render(self.model.getLog(), 1, (255,255,255,255), (0,0,0,100))    # draw the action log
        self.screen.blit(actionLog, (0, self.size[1]-34))

        hp = 3*100
        pygame.draw.rect(self.screen, pygame.Color("red"), (size[0]-90, size[1]-30-hp, 60, hp)) # draw the hp bar

        pygame.display.update()




if __name__ == '__main__':
    pygame.init()
    screenX = 1080
    screenY = 720
    size = (screenX, screenY)
    screen = pygame.display.set_mode(size)
    model = Dungeon(72,72,"piece")
    
    view = DungeonModelView(model, screen, size)
    #pygame.key.set_repeat(350,35)
    # controller = PyGameMouseController(model)
    #controller = PyGameKeyboardController(model) 
    running = True
    view.display()
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running == False
                pygame.quit()
            #controller.handle_event(event)
        view.display()
        time.sleep(.01)
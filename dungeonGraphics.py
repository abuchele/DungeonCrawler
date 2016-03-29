import pygame
import time
import math
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION

from Dungeon import Dungeon
from terrainUtils import *



class DungeonModelView(object):
    def __init__(self, dungeon, screen, size, bs):
        self.model = dungeon
        self.screen = screen
        self.size = size
        self.blockSize = (bs,int(bs*math.cos(0.7)),int(bs*math.sin(0.1)))
        self.playerPos = (36,36)
        self.screenBounds = (-int(size[0]/bs/2+1), int(size[0]/bs/2+1), -int(size[1]/bs/math.sqrt(2)+1), int(size[1]/bs/math.sqrt(2)+1))
        

    def display(self):
        #self.screen.fill(pygame.Color('black'))
        for dy in range(self.screenBounds[2], self.screenBounds[3]):
            for dx in range(self.screenBounds[0], self.screenBounds[1]):
                block = self.model.getBlock(self.playerPos[0]+dx, self.playerPos[1]+dy)
                if block.raised:
                    rec = pygame.Rect((dx-0.5)*self.blockSize[0]+size[0]/2, (dy-1)*self.blockSize[1]-self.blockSize[2]+size[1]/2, self.blockSize[0], self.blockSize[1]+self.blockSize[2])
                else:
                    rec = pygame.Rect((dx-0.5)*self.blockSize[0]+size[0]/2, (dy-1)*self.blockSize[1]+size[1]/2, self.blockSize[0], self.blockSize[1])
                pygame.draw.rect(self.screen, pygame.Color(*block.color), rec)
        pygame.display.update()


if __name__ == '__main__':
    pygame.init()
    screenX = 1080
    screenY = 720
    size = (screenX, screenY)
    blockSize = 50
    screen = pygame.display.set_mode(size)
    model = Dungeon(72,72,"maze1")
    
    view = DungeonModelView(model, screen, size, blockSize)
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
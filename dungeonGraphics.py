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
        self.dispSize = (size[1],size[1])
        tht = 0.3
        self.blockSize = (bs,int(bs*math.cos(tht)),int(bs*math.sin(tht)))
        self.playerPos = (36,36)
        self.screenBounds = (-int(size[1]/bs/2), int(size[1]/bs/2)+1, -int(size[1]/bs/math.sqrt(2)), int(size[1]/bs/math.sqrt(2)))
        self.bigmap = pygame.Surface((size[0], size[0]))

        self.minimap = pygame.Surface((size[0]-size[1], size[0]-size[1]))
        for x in range(0,self.minimap.get_width()):
            for y in range(0,self.minimap.get_height()):
                self.minimap.set_at((x,y), self.model.getBlock(x*self.model.getWidth()/self.minimap.get_width(),
                    y*self.model.getHeight()/self.minimap.get_height()).color)

        self.font = pygame.font.SysFont("Times New Roman", 30, bold=True)
        

    def display(self):
        for dy in range(self.screenBounds[2], self.screenBounds[3]):    # draw all the blocks
            for dx in range(self.screenBounds[0], self.screenBounds[1]):
                block = self.model.getBlock(self.playerPos[0]+dx, self.playerPos[1]+dy)
                if block.raised:
                    rec = pygame.Rect((dx-0.5)*self.blockSize[0]+self.dispSize[0]/2, (dy-1)*self.blockSize[1]-self.blockSize[2]+self.dispSize[1]/2,
                        self.blockSize[0], self.blockSize[1]+self.blockSize[2])
                else:
                    rec = pygame.Rect((dx-0.5)*self.blockSize[0]+self.dispSize[0]/2, (dy-1)*self.blockSize[1]+self.dispSize[1]/2,
                        self.blockSize[0],self.blockSize[1])
                pygame.draw.rect(self.bigmap, pygame.Color(*block.color), rec)
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
    blockSize = 50
    screen = pygame.display.set_mode(size)
    model = Dungeon(72,72,"rooms")
    
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
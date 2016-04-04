import pygame
import time
import math

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
        # self.playerPos = [36,36]
        self.screenBounds = (-size[1]/self.blockSize[0]/2, size[1]/self.blockSize[0]/2+1, -size[1]/self.blockSize[1]/2, size[1]/self.blockSize[1]/2+1)
        self.bigmap = pygame.Surface((size[0], size[0]))    # the actual display window
        self.minimap = pygame.Surface((len(dungeon.grid[0]), len(dungeon.grid)))    # the 1 pixel/block map
        self.font = pygame.font.SysFont("Times New Roman", 30, bold=True)
        self.shadowSprite = pygame.image.load("sprites/Shadow.png") # the sprite to put over explored but not visible blocks
        self.playerSprite = pygame.image.load("sprites/Player.png") # the player sprite

        self.losLst = []    # the list that will determine line of sight
        for r in range(1,max(self.screenBounds[1],self.screenBounds[3])+1):
            for t in range(-r,r):
                if r < self.screenBounds[1] and t >= self.screenBounds[2] and t < self.screenBounds[3]:
                    self.losLst.append(drawLOS(r,t))   # each element is a tuple with x,y of the point in question, and x,y of the point it is pointing to
                if -r >= self.screenBounds[0] and -t >= self.screenBounds[2] and -t < self.screenBounds[3]:
                    self.losLst.append(drawLOS(-r,-t))
                if -t >= self.screenBounds[0] and -t < self.screenBounds[1] and r < self.screenBounds[3]:
                    self.losLst.append(drawLOS(-t,r))
                if t >= self.screenBounds[0] and t < self.screenBounds[1] and -r >= self.screenBounds[2]:
                    self.losLst.append(drawLOS(t,-r))

        self.visible = dict()
        self.visible[(0,0)] = True  # keeps track fo which blocks are visible
        

    def display(self):
        for x1,y1,x2,y2 in self.losLst:
            self.visible[(x1,y1)] = self.visible[(x2,y2)] and self.model.getBlock(self.model.player.x+x2, self.model.player.y+y2).transparent

        for dy in range(self.screenBounds[2], self.screenBounds[3]):    # draw all the blocks
            for dx in range(self.screenBounds[0], self.screenBounds[1]):
                block = self.model.getBlock(self.model.player.x+dx, self.model.player.y+dy)
                if self.visible[(dx,dy)]:
                    self.bigmap.blit(block.sprite, (dx*self.blockSize[0]+self.dispSize[0]/2, dy*self.blockSize[1]+self.dispSize[1]/2))
                    self.minimap.set_at((self.model.player.x+dx, self.model.player.y+dy), block.color)
                    block.explored = True
                elif block.explored:
                    self.bigmap.blit(block.sprite, (dx*self.blockSize[0]+self.dispSize[0]/2, dy*self.blockSize[1]+self.dispSize[1]/2))
                    self.bigmap.blit(self.shadowSprite, (dx*self.blockSize[0]+self.dispSize[0]/2, dy*self.blockSize[1]+self.dispSize[1]/2))
                else:
                    self.bigmap.blit(self.model.nullBlock.sprite, (dx*self.blockSize[0]+self.dispSize[0]/2, dy*self.blockSize[1]+self.dispSize[1]/2))

        self.bigmap.blit(self.playerSprite, (self.dispSize[0]/2, self.dispSize[1]/2))

        self.screen.blit(self.bigmap, (0,0))

        pygame.draw.rect(self.screen, pygame.Color("black"), (self.size[1], 0, self.size[0]-self.size[1], self.size[1]))    # draw the background of the HUD

        self.screen.blit(pygame.transform.scale(self.minimap, (self.size[0]-self.size[1],self.size[0]-self.size[1])), (self.size[1],0))    # draw the minimap
        
        actionLog = self.font.render(self.model.getLog(), 1, (255,255,255,255), (0,0,0,100))    # draw the action log
        self.screen.blit(actionLog, (0, self.size[1]-34))

        hp = 3*100
        pygame.draw.rect(self.screen, pygame.Color("red"), (self.size[0]-90, self.size[1]-30-hp, 60, hp)) # draw the hp bar

        pygame.display.update()


def drawLOS(x,y):   # gets the point that is 1 closer to the origin (if that block is visible and transparent, this block is visible)
    return (x, y, int(math.floor(0.5+x-x/math.hypot(x,y))), int(math.floor(0.5+y-y/math.hypot(x,y))))



if __name__ == '__main__':
    pygame.init()
    screenX = 1080
    screenY = 720
    size = (screenX, screenY)
    screen = pygame.display.set_mode(size)
    model = Dungeon(72,72,"piece")
    
    view = DungeonModelView(model, screen, size)
    view.display()
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                break
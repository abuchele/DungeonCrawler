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
            self.visible[(x1,y1)] = self.visible[(x2,y2)] and self.model.getBlock(self.model.Player.x+x2, self.model.Player.y+y2).transparent

        for dy in range(self.screenBounds[2], self.screenBounds[3]):    # draw all the blocks
            for dx in range(self.screenBounds[0], self.screenBounds[1]):
                block = self.model.getBlock(self.model.Player.x+dx, self.model.Player.y+dy)
                if self.visible[(dx,dy)]:
                    self.bigmap.blit(block.sprite, (dx*self.blockSize[0]+self.dispSize[0]/2, dy*self.blockSize[1]+self.dispSize[1]/2))
                    self.minimap.set_at((self.model.Player.x+dx, self.model.Player.y+dy), block.color)
                elif block.explored:
                    self.bigmap.blit(block.sprite, (dx*self.blockSize[0]+self.dispSize[0]/2, dy*self.blockSize[1]+self.dispSize[1]/2))
                    self.bigmap.blit(self.shadowSprite, (dx*self.blockSize[0]+self.dispSize[0]/2, dy*self.blockSize[1]+self.dispSize[1]/2))
                else:
                    self.bigmap.blit(self.model.nullBlock.sprite, (dx*self.blockSize[0]+self.dispSize[0]/2, dy*self.blockSize[1]+self.dispSize[1]/2))

        self.bigmap.blit(self.playerSprite, (self.dispSize[0]/2, self.dispSize[1]/2))

        self.screen.blit(self.bigmap, (0,0))

        pygame.draw.rect(self.screen, pygame.Color("black"), (self.size[1], 0, self.size[0]-self.size[1], self.size[1]))    # draw the background of the HUD

        self.screen.blit(pygame.transform.scale(self.minimap, (size[0]-size[1],size[0]-size[1])), (self.size[1],0))    # draw the minimap
        
        actionLog = self.font.render(self.model.getLog(), 1, (255,255,255,255), (0,0,0,100))    # draw the action log
        self.screen.blit(actionLog, (0, self.size[1]-34))

        hp = 3*100
        pygame.draw.rect(self.screen, pygame.Color("red"), (size[0]-90, size[1]-30-hp, 60, hp)) # draw the hp bar

        pygame.display.update()


def drawLOS(x,y):   # gets the point that is 1 closer to the origin (if that block is visible and transparent, this block is visible)
    return (x, y, int(math.floor(0.5+x-x/math.hypot(x,y))), int(math.floor(0.5+y-y/math.hypot(x,y))))


class PyGameKeyboardController(object):
    def __init__(self, model):
        self.model = model

    def handle_event(self, event):
        # self.model.Player.history = (self.model.Player.xpos,self.model.Player.ypos, self.model.Player.history[0], self.model.Player.history[1])
        if event.type != KEYDOWN:
            return
   #    while running:
   #        keys = pygame.key.get_pressed()
   #        if keys[pygame.K_LEFT] and self.model.Player.xpos > 1:
   #            self.model.Player.xpos -= 1
            # if keys[pygame.K_RIGHT] and self.model.Player.xpos < self.model.x - 1:
            #   self.model.Player.xpos += 1
            # if keys[pygame.K_UP] and self.model.Player.ypos > 1:
            #   self.model.Player.ypos -=1
            # if keys[pygame.K_DOWN] and self.model.Player.ypos < self.model.y - 1:
            #   self.model.Player.ypos +=1

        if event.key == pygame.K_LEFT and not self.model.grid[self.model.Player.y][self.model.Player.x-1].collides:
            # if self.model.Player.direction == "L":
            self.model.Player.x -= 1
            self.model.Player.direction = "L"
        elif event.key == pygame.K_RIGHT and not self.model.grid[self.model.Player.y][self.model.Player.x+1].collides:
            # if self.model.Player.direction == "R":
            self.model.Player.x += 1
            self.model.Player.direction = "R"
        elif event.key == pygame.K_UP and not self.model.grid[self.model.Player.y-1][self.model.Player.x].collides:
            # if self.model.Player.direction == "U":            
            self.model.Player.y -=1
            self.model.Player.direction = "U"
        elif event.key == pygame.K_DOWN and not self.model.grid[self.model.Player.y+1][self.model.Player.x].collides:
            # if self.model.Player.direction == "D":
            self.model.Player.y +=1
            self.model.Player.direction = "D"



        
        # if event.key == pygame.K_LEFT and not self.model.grid[self.model.Player.x-1,self.model.Player.y].collides:
        #     # if self.model.Player.direction == "L":
        #     self.model.Player.x -= 1
        #     self.model.Player.direction = "L"
        # elif event.key == pygame.K_RIGHT and not self.model.grid[self.model.Player.x+1,self.model.Player.y].collides:
        #     # if self.model.Player.direction == "R":
        #     self.model.Player.x += 1
        #     self.model.Player.direction = "R"
        # elif event.key == pygame.K_UP and not self.model.grid[self.model.Player.x,self.model.Player.y-1].collides:
        #     # if self.model.Player.direction == "U":            
        #     self.model.Player.y -=1
        #     self.model.Player.direction = "U"
        # elif event.key == pygame.K_DOWN and not self.model.grid[self.model.Player.x,self.model.Player.y+1].collides:
        #     # if self.model.Player.direction == "D":
        #     self.model.Player.y +=1
        #     self.model.Player.direction = "D"


        # if self.model.Player.xpos == self.model.KeyX and self.model.Player.ypos == self.model.KeyY:
        #     self.model.Player.hasKey = True
        # if self.model.Player.hasKey == True:
        #     self.model.Grid[self.model.ChestX,self.model.ChestY] = 0
        # if (self.model.Player.xpos,self.model.Player.ypos)==(self.model.ChestX,self.model.ChestY):
        #     self.model.won = True
        # self.model.MonsterPack.move(self.model.MonsterPack.grid)
        # for coord in self.model.MonsterPack.coordinates:
        #     # print coord
        #     if coord == (self.model.Player.xpos,self.model.Player.ypos):
        #         self.model.eaten = True





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
    controller = PyGameKeyboardController(model) 
    running = True
    view.display()
    while running:
        time.sleep(.25)
        events = pygame.event.get()
        if len(events) == 0:
            pass
        # if event.type == QUIT:
        #         running == False
        #         pygame.quit()
        
        else:
            controller.handle_event(events[len(events)-1])
            
        #     controller.handle_event(event)
        view.display()

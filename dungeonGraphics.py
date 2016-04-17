import pygame
import time
import math

import coreMechanics
from terrainUtils import *



class DungeonModelView(object):
    def __init__(self, dungeon, screen, size):
        self.model = dungeon
        self.screen = screen
        self.size = size
        self.dispSize = (size[1],size[1])
        self.mimpSz = (size[0]-size[1], size[0]-size[1])            # minimap size
        self.rempSz = (len(dungeon.grid[0])/2, len(dungeon.grid)/2) # real map size (half the size of the whole dungeon)
        self.blockSize = (50,48,15)
        self.screenBounds = (-size[1]/self.blockSize[0]/2, size[1]/self.blockSize[0]/2+1, -size[1]/self.blockSize[1]/2, size[1]/self.blockSize[1]/2+1)
        self.bigmap = pygame.Surface((size[0], size[0]))    # the actual display window
        self.minimap = loadMinimap(dungeon.grid)    # the 1 pixel/block map
        self.font = pygame.font.SysFont("Times New Roman", 30, bold=True)
        self.shadowSprite = pygame.image.load("sprites/Shadow.png") # the sprite to put over explored but not visible blocks
        self.playerSpriteFront = [pygame.image.load("sprites/PlayerFrontStand.png"),pygame.image.load("sprites/PlayerFrontWalk1.png"),pygame.image.load("sprites/PlayerFrontWalk2.png")]
        self.playerSpriteBack = [pygame.image.load("sprites/PlayerBackStand.png"),pygame.image.load("sprites/PlayerBackWalk1.png"),pygame.image.load("sprites/PlayerBackWalk2.png")]
        self.playerSpriteLeft = [pygame.image.load("sprites/PlayerLeftStand.png"),pygame.image.load("sprites/PlayerLeftWalk1.png"),pygame.image.load("sprites/PlayerLeftWalk2.png")]
        self.playerSpriteRight = [pygame.image.load("sprites/PlayerRightStand.png"),pygame.image.load("sprites/PlayerRightWalk1.png"),pygame.image.load("sprites/PlayerRightWalk2.png")]
        self.dotSprite = pygame.image.load("sprites/Dot.png")   # the dot for the minimap
        self.pauseScreen = pygame.image.load("sprites/Paused.png")
        self.playerSprite = self.playerSpriteFront[0]
        self.sprites = loadSprites()
        self.shadows = loadShadowSprites()
        self.steps = 0
        self.prex = self.model.player.x
        self.prey = self.model.player.y
        self.prevdirection = self.model.player.direction
        self.prevSprite = self.playerSprite

        self.losLst = []    # the list that will determine line of sight
        for r in range(2,max(self.screenBounds[1],self.screenBounds[3])+1):
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
        for x in [-1,0,1]:
            for y in [-1,0,1]:
                self.visible[(x,y)] = True  # keeps track fo which blocks are visible
        

    def display(self):
        """
        Draws all entities, blocks, minimaps, etc. to the screen and displays
        to be called once per tick
        """
        for x1,y1,x2,y2 in self.losLst:
            self.visible[(x1,y1)] = self.visible[(x2,y2)] and self.model.getBlock(self.model.player.x+x2, self.model.player.y+y2).transparent

        for dy in range(self.screenBounds[2], self.screenBounds[3]):    # draw all the blocks
            for dx in range(self.screenBounds[0], self.screenBounds[1]):
                block = self.model.getBlock(self.model.player.x+dx, self.model.player.y+dy)
                if self.visible[(dx,dy)]:
                    self.screen.blit(self.sprites[block.sprite], (dx*self.blockSize[0]+self.dispSize[0]/2, dy*self.blockSize[1]+self.dispSize[1]/2))
                    self.minimap.set_at((self.model.player.x+dx, self.model.player.y+dy), block.color)
                    block.explored = True
                elif block.explored:
                    self.screen.blit(self.shadows[block.sprite], (dx*self.blockSize[0]+self.dispSize[0]/2, dy*self.blockSize[1]+self.dispSize[1]/2))
                else:
                    self.screen.blit(self.sprites[0], (dx*self.blockSize[0]+self.dispSize[0]/2, dy*self.blockSize[1]+self.dispSize[1]/2))
            if dy == 0:
                if (self.prex - self.model.player.x) == 0 and (self.prey - self.model.player.y) == 0:
                    if self.prevdirection == self.model.player.direction:
                        playerSpriteCurrent = self.prevSprite
                        self.steps = 0
                else:
                    if self.steps is not 2:
                        self.steps += 1
                    else:
                        self.steps = 1

                direction_to_angle = {"U":0,"L":90,"D":180,"R":270}
                if self.model.player.direction == "U":
                    playerSpriteCurrent = self.playerSpriteBack[self.steps]
                elif self.model.player.direction == "D":
                    playerSpriteCurrent = self.playerSpriteFront[self.steps]
                elif self.model.player.direction == "L":
                    playerSpriteCurrent = self.playerSpriteLeft[self.steps]
                elif self.model.player.direction == "R":
                    playerSpriteCurrent = self.playerSpriteRight[self.steps]
                self.prevSprite = playerSpriteCurrent
                self.prex = self.model.player.x
                self.prey = self.model.player.y

                self.screen.blit(playerSpriteCurrent, (self.dispSize[0]/2, self.dispSize[1]/2))   # draw the player
                

        pygame.draw.rect(self.screen, pygame.Color("black"), (self.size[1], self.size[0]-self.size[1], self.size[0]-self.size[1], self.size[1]))    # draw the background of the HUD
        self.screen.blit(pygame.transform.scale(self.minimap, (2*(self.size[0]-self.size[1]),2*(self.size[0]-self.size[1]))), (self.size[1],0),
            area = ((self.model.player.x/self.rempSz[0]*self.mimpSz[0], self.model.player.y/self.rempSz[1]*self.mimpSz[1]), self.mimpSz))    # draw the minimap

        self.screen.blit(self.dotSprite, (self.size[1]+int((self.model.player.x+0.5)*self.mimpSz[0]/self.rempSz[0])%self.mimpSz[0]-self.dotSprite.get_width()/2+1,
            int((self.model.player.y+0.5)*self.mimpSz[1]/self.rempSz[1])%self.mimpSz[1]-self.dotSprite.get_height()/2+1))  # draw the dot on the minimap

        if self.model.player.hasAttacked == True: # draw player attack sprite!
                    self.screen.blit(pygame.transform.rotate(self.sprites[self.model.player.attackSprite], direction_to_angle[self.model.player.direction]),(self.dispSize[0]/2 + self.model.player.directionCoordinates[self.model.player.direction][0]*self.blockSize[0], self.dispSize[1]/2 + self.model.player.directionCoordinates[self.model.player.direction][1]*self.blockSize[1]))
        actionLog = self.font.render(self.model.getLog(), 1, (255,255,255,255), (0,0,0,100))    # draw the action log
        self.screen.blit(actionLog, (0, self.size[1]-34))

        hp = 3*100
        pygame.draw.rect(self.screen, pygame.Color("red"), (self.size[0]-90, self.size[1]-30-hp, 60, hp)) # draw the hp bar

        if self.model.paused:
            self.screen.blit(self.pauseScreen, (0,0))

        pygame.display.update()


def loadMinimap(grid):  # creates a minimap for the given block list-list
    output = pygame.Surface((len(grid[0]), len(grid)))
    for x in range(0, len(grid[0])):    # draw all the blocks
        for y in range(0, len(grid)):
            if grid[y][x].explored:
                output.set_at((x, y), grid[y][x].color)
    return output


def loadSprites():
    return [pygame.image.load("sprites/{}.png".format(name)) for name in ["Null","Floor","Stone","Brick","DoorOpen","DoorClosed","Lava","Bedrock","Obsidian","Glass","Metal","Metal","Loot","LootOpen"]]


def loadShadowSprites():
    return [pygame.image.load("sprites/{}_Shadow.png".format(name)) for name in ["Null","Floor","Stone","Brick","DoorOpen","DoorClosed","Lava","Bedrock","Obsidian","Glass","Metal","Metal","Loot","LootOpen"]]


def drawLOS(x,y):   # gets the point that is 1 closer to the origin (if that block is visible and transparent, this block is visible)
    return (x, y, int(math.floor(0.5+x-x/math.hypot(x,y))), int(math.floor(0.5+y-y/math.hypot(x,y))))



if __name__ == '__main__':
    pygame.init()
    screenX = 1080
    screenY = 720
    size = (screenX, screenY)
    screen = pygame.display.set_mode(size)
    model = coreMechanics.Dungeon(72,72,method="piece")
    
    view = DungeonModelView(model, screen, size)
    view.display()
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                break
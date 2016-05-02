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
        self.font = pygame.font.SysFont("Times New Roman", 26, bold=True)
        self.targetLocations = []
        self.shadowSprite = pygame.image.load("sprites/Shadow.png") # the sprite to put over explored but not visible blocks

        spriteNames = [["Stand","Walk1","Walk2"], ["Back","Front","Left","Right"]]
        self.playerSprites = [[pygame.image.load("sprites/Player"+direc+movem+".png") for movem in spriteNames[0]] for direc in spriteNames[1]]
        self.dotSprite = pygame.image.load("sprites/Dot.png")   # the dot for the minimap
        self.crossheir = pygame.image.load("sprites/Target.png")
        self.blastSprite = pygame.image.load("sprites/Blast.png")
        self.pauseScreen = pygame.image.load("HUD_sprites/Paused.png")
        self.dialogueBox = pygame.image.load("HUD_sprites/Dialogue_GUI.png")
        self.deathScreen = pygame.image.load("HUD_sprites/Dead.png")
        self.soundSprite = pygame.image.load("sprites/Sound.png")
        self.HUD = pygame.image.load("HUD_sprites/Hud.png")
        self.playerSprite = self.playerSprites[0][0]

        spriteNames = ["Null","Floor","Stone","Brick","DoorOpen","DoorClosed","Lava","Bedrock","Obsidian","Glass","Metal","Metal",
                        "Loot","LootOpen","Furniture0","Furniture1","Furniture2","Furniture3"]
        shadowNames = [name+"_Shadow" for name in spriteNames]
        monsterSpriteNames = ["Demon","Ghost","ZombieF","ZombieM","NPC","DemonAttack","Creeper","Skeleton","Bones"]
        effectNames = ["Stunned","OnFire"]
        attackSpriteNames = ["attack"+str(i) for i in range(0,8)]
        songSpriteNames = ["song"+str(i) for i in range(0,8)]
        self.sprites = loadSprites(spriteNames)
        self.shadows = loadSprites(shadowNames)
        self.monsterSprites = loadSprites(monsterSpriteNames)
        self.effectSprites = loadSprites(effectNames)
        self.attackSprites = loadSprites(attackSpriteNames)
        self.sheetSprites = loadSprites(songSpriteNames, directory="HUD_sprites")

        self.t = 0

        self.compose_LOS_list()  # do some preliminary calculations for Line of Sight

        self.visible = dict()
        for x in [-1,0,1]:
            for y in [-1,0,1]:
                self.visible[(x,y)] = True  # keeps track fo which blocks are visible


    def update(self):
        for x1,y1,x2,y2 in self.losLst: # decides what blocks are visible
            self.visible[(x1,y1)] = self.visible[(x2,y2)] and self.model.getBlock(self.model.player.x+x2, self.model.player.y+y2).transparent
        self.targetLocations = []
        self.explosionLocations = []

    def display(self, t):
        """
        Draws all entities, blocks, minimaps, etc. to the screen and displays
        takes input t, a float between 0 and 1 that represents at what point in the tick we are (0=beginning, 1=end)
        """
        if self.model.state == "R":
            self.t = t
        pxr, pyr = (self.model.player.x, self.model.player.y)   # the "real" player coordinates
        pxc, pyc = self.model.player.getCoords(self.t)             # the calculated coordinates that produce smoother motion

        self.drawBlocks(self.t, pxr, pyr, pxc, pyc)
        self.drawMonsters(self.t, pxr, pyr, pxc, pyc)
        self.drawAttacks(self.t, pxr, pyr, pxc, pyc)                
        self.drawHUD(self.t, pxr, pyr, pxc, pyc)
        pygame.display.update()


    def drawBlocks(self, t, pxr, pyr, pxc, pyc):   # draws all nearby blocks
        for dy in range(self.screenBounds[2], self.screenBounds[3]):    # draw all the blocks and monsters
            for dx in range(self.screenBounds[0], self.screenBounds[1]):
                blockCoords = ((dx-pxc+pxr)*self.blockSize[0]+self.dispSize[0]/2, (dy-pyc+pyr)*self.blockSize[1]+self.dispSize[1]/2)
                block = self.model.getBlock(pxr+dx, pyr+dy)
                if self.visible[(dx,dy)]:                                       # if it is visible,
                    self.screen.blit(self.sprites[block.sprite], blockCoords)
                    self.minimap.set_at((pxr+dx, pyr+dy), block.color)          # and mark it on the minimap
                    block.explored = True                                       # and remember it for later

                elif block.explored:                                            # if it is not visible but we've been here before
                    self.screen.blit(self.shadows[block.sprite], blockCoords)   # draw it, but darker
                else:                                                           # if we don't know what it looks like
                    self.screen.blit(self.sprites[0], blockCoords)              # put in a placeholder block


    def drawMonsters(self, t, pxr, pyr, pxc, pyc): # draws all nearby entites (including the player)
        for dy in range(self.screenBounds[2], self.screenBounds[3]):    # draw all the blocks and monsters
            for dx in range(self.screenBounds[0], self.screenBounds[1]):
                blockCoords = ((dx-pxc+pxr)*self.blockSize[0]+self.dispSize[0]/2, (dy-pyc+pyr)*self.blockSize[1]+self.dispSize[1]/2)
                monster = self.model.monstercoords.get((pxr+dx,pyr+dy),0) #this is a Monster
                if self.visible[(dx,dy)]:                                       # if it is visible,
                    if monster != 0:
                        mxr, myr = (monster.x, monster.y)
                        mxc, myc = monster.getCoords(t)
                        monstCoords = (blockCoords[0]+self.blockSize[0]*(mxc-mxr), blockCoords[1]+self.blockSize[1]*(myc-myr))
                        self.screen.blit(self.monsterSprites[monster.sprite],monstCoords)   # just draw it and the monster on it
                        if monster.effect.get("ignited",0):
                            self.screen.blit(self.effectSprites[1], monstCoords)
                        if monster.effect.get("stunned",0):
                            self.screen.blit(self.effectSprites[0], monstCoords)
                        if monster.name == "Demon":
                            if monster.attackWarmup > 0:
                                self.targetLocations.append(monster.attackCoords)
                            elif monster.attackWarmup == 0:
                                self.explosionLocations.append(monster.attackCoords)
                elif self.model.player.listening: #draws "listen sprites" on all monsters within range
                    if monster != 0:
                        mxr, myr = (monster.x, monster.y)
                        mxc, myc = monster.getCoords(t)
                        monstCoords = (blockCoords[0]+self.blockSize[0]*(mxc-mxr), blockCoords[1]+self.blockSize[1]*(myc-myr))
                        self.screen.blit(self.soundSprite,monstCoords)
            if dy == 0:
                pSpriteInd = self.model.player.sprite
                self.screen.blit(self.playerSprites[pSpriteInd[0]][pSpriteInd[1]], (self.dispSize[0]/2, self.dispSize[1]/2))   # draw the player


    def drawAttacks(self, t, pxr, pyr, pxc, pyc):
        direction_to_angle = {"U":0,"L":90,"D":180,"R":270}
        if self.model.player.attackCooldown > 0: # draw player attack sprite!
            attackSprite = self.attackSprites[self.model.player.song]
            for atX, atY in self.model.player.earshot:
                attackCoords = ((atX-pxc)*self.blockSize[0]+self.dispSize[0]/2,
                                (atY-pyc)*self.blockSize[1]+self.dispSize[1]/2 + int((self.model.player.attackCooldown-t)*20/self.model.player.attackSpeed) - 15)
                self.screen.blit(attackSprite,attackCoords)
        for atX, atY in self.targetLocations:
            attackCoords = ((atX-pxc)*self.blockSize[0]+self.dispSize[0]/2, (atY-pyc)*self.blockSize[1]+self.dispSize[1]/2)
            self.screen.blit(self.crossheir,attackCoords)
        for atX, atY in self.explosionLocations:
            attackCoords = ((atX-pxc)*self.blockSize[0]+self.dispSize[0]/2, (atY-pyc)*self.blockSize[1]+self.dispSize[1]/2)
            self.screen.blit(self.blastSprite,attackCoords)


    def drawHUD(self, t, pxr, pyr, pxc, pyc):
        pygame.draw.rect(self.screen, pygame.Color("black"), (self.size[1], self.mimpSz[0], self.size[0]-self.size[1], self.size[1]))    # draw the background of the HUD
        self.screen.blit(pygame.transform.scale(self.minimap, (2*(self.size[0]-self.size[1]),2*(self.size[0]-self.size[1]))), (self.size[1],0),
            area = ((self.model.player.x/self.rempSz[0]*self.mimpSz[0], self.model.player.y/self.rempSz[1]*self.mimpSz[1]), self.mimpSz))    # draw the minimap

        self.screen.blit(self.dotSprite, (self.size[1]+int((self.model.player.x+0.5)*self.mimpSz[0]/self.rempSz[0])%self.mimpSz[0]-self.dotSprite.get_width()/2+1,
            int((self.model.player.y+0.5)*self.mimpSz[1]/self.rempSz[1])%self.mimpSz[1]-self.dotSprite.get_height()/2+1))  # draw the dot on the minimap

        actionLog = self.font.render(self.model.getLog(), 1, (255,255,255,255), (0,0,0,100))    # draw the action log
        self.screen.blit(actionLog, (0, self.size[1]-30))

        hp = 3.24*self.model.player.health
        pygame.draw.rect(self.screen, pygame.Color("red"), (self.size[0]-74, self.size[1]-17-hp, 54, hp)) # draw the hp bar
        self.screen.blit(self.HUD, (self.size[1],self.mimpSz[0]))

        if len(self.model.player.availableSong) > 1:
            self.screen.blit(pygame.transform.scale(self.sheetSprites[self.model.player.nextSong],(75,75)), (self.size[1]+25, self.mimpSz[0]))
        if len(self.model.player.availableSong) > 0:
            self.screen.blit(self.sheetSprites[self.model.player.song], (self.size[1], self.mimpSz[0]+75))  # draw the songs
        if len(self.model.player.availableSong) > 1:
            self.screen.blit(pygame.transform.scale(self.sheetSprites[self.model.player.lastSong],(75,75)), (self.size[1]+25, self.mimpSz[0]+225))

        if self.model.state == "P":
            self.screen.blit(self.pauseScreen, (0,0))
        elif self.model.state == "D":
            self.screen.blit(self.dialogueBox, (0,0))
            paragraph = self.model.currentParagraph()
            for y, line in enumerate(paragraph):
                self.screen.blit(line, (30,30+30*y))
        elif self.model.state == "K":
            self.screen.blit(self.deathScreen, (0,0))


    def compose_LOS_list(self): # does preliminary calculations for line of sight
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


    def setModel(self, model):
        self.model = model
        self.minimap = loadMinimap(model.grid)


def loadMinimap(grid):  # creates a minimap for the given block list-list
    output = pygame.Surface((len(grid[0]), len(grid)))
    for x in range(0, len(grid[0])):    # draw all the blocks
        for y in range(0, len(grid)):
            if grid[y][x].explored:
                output.set_at((x, y), grid[y][x].color)
    return output


def loadSprites(filenames, directory="sprites"):
    return [pygame.image.load("{}/{}.png".format(directory,name)) for name in filenames]


def drawLOS(x,y):   # gets the point that is 1 closer to the origin (if that block is visible and transparent, this block is visible)
    return (x, y, int(math.floor(0.5+x-1.4*x/math.hypot(x,y))), int(math.floor(0.5+y-1.4*y/math.hypot(x,y))))



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
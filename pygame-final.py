import pygame
from pygame import *
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION
import time
from random import choice, randint
import numpy

class Wall(object):
    is_blockable = True
    def __init__(self):
        pass


# def generate_rectangles(player, minRec, maxRec, grid, gridx, gridy, maxwidth, maxheight):
#     total_rec = randint(minRec, maxRec)
#     for i in range(total_rec):
#         if i == 0: #make sure a 3x3 is always around the player.
#             clearRectangle(grid, gridx, gridy, player.xpos-1, player.ypos+2, 3, 3)
#         width = randint(int(maxwidth/float(2)), maxwidth)
#         height = randint(int(maxheight/float(2)), maxheight)
#         randx = randint(1,gridx-1)
#         randy = randint(1, gridy-1) #random coordinate
#         clearRectangle(grid, gridx, gridy, randx, randy, width, height)


class Player(object):
    def __init__(self,xpos,ypos, hasKey = False):
        self.xpos = xpos
        self.ypos = ypos
        self.history = (xpos+1,ypos+1, xpos+1, ypos+1)
        self.hasKey = hasKey

class Monster(object):
    def __init__(self, XorY=0, xposition=60, yposition=60):
        self.xpos = xposition 
        self.ypos = yposition
        self.history = (xposition+1, yposition+1, xposition+1, yposition+1)
        self.XorY = XorY


class MonsterPack(object):
    def __init__(self,player,grid,monsters): #monsters is list of monsters
        self.player = player
        self.grid = grid
        self.monsters = monsters
        self.coordinates = [(monster.xpos,monster.ypos) for monster in self.monsters]


    def move(self, grid, speed=1):
        for monster in self.monsters:
            monster.history = (monster.xpos, monster.ypos, monster.history[0], monster.history[1])
            change_in_position = 0
            if monster.XorY==0:
                if monster.xpos > self.player.xpos and self.grid[monster.xpos-1,monster.ypos] == 0:
                    monster.xpos -= speed
                    change_in_position = abs(monster.history[0] - monster.history[2])
                    # return

                elif monster.xpos < self.player.xpos and self.grid[monster.xpos+1,monster.ypos] == 0:
                    monster.xpos += speed
                    change_in_position = abs(monster.history[0] - monster.history[2])
                    # return

                elif monster.ypos > self.player.ypos and self.grid[monster.xpos,monster.ypos-1] == 0:
                    monster.ypos -= speed
                    change_in_position = abs(monster.history[1] - monster.history[3])
                    # return

                elif monster.ypos <self.player.ypos and self.grid[monster.xpos,monster.ypos+1] == 0:
                    monster.ypos += speed
                    change_in_position = abs(monster.history[1] - monster.history[3])
                    # return
            else:
                if monster.ypos > self.player.ypos and self.grid[monster.xpos,monster.ypos-1] == 0:
                    monster.ypos -= speed
                    change_in_position = abs(monster.history[1] - monster.history[3])
                    # return

                elif monster.ypos <self.player.ypos and self.grid[monster.xpos,monster.ypos+1] == 0:
                    monster.ypos += speed
                    change_in_position = abs(monster.history[1] - monster.history[3])


                elif monster.xpos > self.player.xpos and self.grid[monster.xpos-1,monster.ypos] == 0:
                    monster.xpos -= speed
                    change_in_position = abs(monster.history[0] - monster.history[2])
                    # return

                elif monster.xpos < self.player.xpos and self.grid[monster.xpos+1,monster.ypos] == 0:
                    monster.xpos += speed
                    change_in_position = abs(monster.history[0] - monster.history[2])
                    # return


                    # return                

            if change_in_position == 0:
                # self.grid[monster.xpos,monster.ypos] = 1
                if monster.xpos < self.player.xpos and self.grid[monster.xpos+1,monster.ypos+1] == 1 and self.grid[monster.xpos,monster.ypos-1] == 0:
                    self.grid[monster.history[0],monster.history[1]] = 2
                    monster.ypos -= 1
                elif monster.xpos > self.player.xpos and self.grid[monster.xpos-1,monster.ypos+1] == 1 and self.grid[monster.xpos,monster.ypos-1] == 0:
                    self.grid[monster.history[0],monster.history[1]] = 2
                    monster.ypos -= 1
                elif monster.ypos > self.player.ypos and self.grid[monster.xpos+1,monster.ypos-1] == 1 and self.grid[monster.xpos-1,monster.ypos] == 0:
                    self.grid[monster.history[0],monster.history[1]] = 2
                    monster.xpos -= 1
                elif monster.ypos > self.player.ypos and self.grid[monster.xpos-1,monster.ypos-1] == 1 and self.grid[monster.xpos+1,monster.ypos] == 0:
                    self.grid[monster.history[0],monster.history[1]] = 2
                    monster.xpos += 1
                # return    
            self.coordinates = [(monster.xpos,monster.ypos) for monster in self.monsters]

    # def move(self, grid, speed=1):
    #     self.history = (monster.xpos,self.ypos, self.history[0], self.history[1])
    #     if monster.xpos > self.player.xpos and self.grid[monster.xpos-1,self.ypos] == 0:
    #         monster.xpos -= speed
    #     elif monster.xpos < self.player.xpos and self.grid[monster.xpos+1,self.ypos] == 0:
    #         monster.xpos += speed

    #     elif self.ypos > self.player.ypos and self.grid[monster.xpos,self.ypos-1] == 0:
    #         self.ypos -= speed
    #     elif self.ypos < self.player.ypos and self.grid[monster.xpos,self.ypos+1] == 0:
    #         self.ypos += speed


class DungeonModel(object):
    def __init__(self, x, y, xpos, ypos, monsternum = 4, won = False, eaten = False):
        self.x = x
        self.y = y
        self.Grid = numpy.ones((x,y))
        self.Player = Player(xpos,ypos, False)
        self.monsternum = monsternum

        self.won = won
        self.eaten = eaten

        # print self.Grid
        
        # self.Grid[0, :] = self.Grid[-1, :] = 1
        # self.Grid[:, 0] = self.Grid[:, -1] = 1

        # for i in range(x):
        #     for j in range(y):
        #         if i == 0 or i == x-1 or j == 0 or j == y-1:
        #             self.Grid[i,j] = 1
                # else:
                #     self.Grid[i,j] = choice([0,1])
        def clearRectangle(grid, gridx, gridy, left, top, width, height): #grid is an array, gridx is the largest rightward index 1 is walls, 0 is empty space
            if left + width > gridx:
                rightbound = gridx
            else:
                rightbound = left + width
            if top - height < 0:
                upperbound = 1
            else:
                upperbound = top - height
            for i in range(left,rightbound):
                for j in range(upperbound,top):
                    grid[i,j] = 0
        
        def generate_rectangles(player, xRec, yRec, grid, gridx, gridy, maxwidth, maxheight): #xRec and yRec are how many rectangles you want in each direction
            for i in range(xRec):
                for j in range(yRec):
                    clearRectangle(grid,gridx,gridy, i * int(gridx/float(xRec))+1, (j+1) * int(gridy/float(yRec)-1), int(gridx/float(xRec))-2, int(gridy/float(yRec))-2)
                    grid[(2*i-1)*(gridx-1)/float(xRec*2),range(1,gridy-1)] = 0
                    grid[range(1,gridx-1),(2*j-1)*(gridy)/float(yRec*2)] = 0

        def getEmpty(grid, gridx, gridy):
            result = []
            for i in range(0,gridx):
                for j in range(0,gridy):
                    if grid[i,j] == 0:
                        result.append((i,j))
            return result
        
        generate_rectangles(self.Player, 6, 4, self.Grid, self.x, self.y, 40, 40)
        emptylist = getEmpty(self.Grid, self.x, self.y)
        coord = randint(0,len(emptylist)-1)
        (self.KeyX,self.KeyY) = (emptylist[coord][0],emptylist[coord][1])
        emptylist.remove(emptylist[coord])
        coord1 = randint(0,len(emptylist)-1)
        (self.ChestX,self.ChestY) = (emptylist[coord1][0],emptylist[coord1][1])
        self.Grid[(self.ChestX,self.ChestY)] = 1
        emptylist.remove(emptylist[coord1])
        MonsterLst = []
        for i in range(self.monsternum):
            coord = randint(0,len(emptylist)-1)
            MonsterLst.append(Monster(randint(0,1),emptylist[coord][0],emptylist[coord][1]))
            emptylist.remove(emptylist[coord])

        self.MonsterPack = MonsterPack(self.Player, self.Grid, MonsterLst)
        # print self.KeyX
        # print self.KeyY
        # print emptylist
        # print numpy.where(self.Grid==0)[1][30]


        def __str__(self):
            return str(self.Grid)

class PyGameKeyboardController(object):
    def __init__(self, model):
        self.model = model

    def handle_event(self, event):
        self.model.Player.history = (self.model.Player.xpos,self.model.Player.ypos, self.model.Player.history[0], self.model.Player.history[1])
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
        
        if event.key == pygame.K_LEFT and self.model.Grid[self.model.Player.xpos-1,self.model.Player.ypos] != 1:
            self.model.Player.xpos -= 1
        elif event.key == pygame.K_RIGHT and self.model.Grid[self.model.Player.xpos+1,self.model.Player.ypos] != 1:
            self.model.Player.xpos += 1
        elif event.key == pygame.K_UP and self.model.Grid[self.model.Player.xpos,self.model.Player.ypos-1] != 1:
            self.model.Player.ypos -=1
        elif event.key == pygame.K_DOWN and self.model.Grid[self.model.Player.xpos,self.model.Player.ypos+1] != 1:
            self.model.Player.ypos +=1
        if self.model.Player.xpos == self.model.KeyX and self.model.Player.ypos == self.model.KeyY:
            self.model.Player.hasKey = True
        if self.model.Player.hasKey == True:
            self.model.Grid[self.model.ChestX,self.model.ChestY] = 0
        if (self.model.Player.xpos,self.model.Player.ypos)==(self.model.ChestX,self.model.ChestY):
            self.model.won = True
        self.model.MonsterPack.move(self.model.MonsterPack.grid)
        for coord in self.model.MonsterPack.coordinates:
            # print coord
            if coord == (self.model.Player.xpos,self.model.Player.ypos):
                self.model.eaten = True

class DungeonModelView(object):
    def __init__(self, model, screen, size):
        self.model = model
        self.screen = screen
        self.size = size
        

    def drawMap(self):
        self.screen.fill(pygame.Color('black'))
        gridsize = self.size[1]/float(self.model.y)
        for x in range(self.model.x):
            for y in range(self.model.y):
                if self.model.Grid[x,y] == 1:
                    r = pygame.Rect(x * gridsize, y * gridsize, gridsize, gridsize)
                    pygame.draw.rect(self.screen, pygame.Color('red'), r)
        y = pygame.Rect(self.model.KeyX * gridsize, self.model.KeyY * gridsize, gridsize, gridsize)
        pygame.draw.rect(self.screen, pygame.Color('yellow'), y)
        b = pygame.Rect(self.model.ChestX * gridsize, self.model.ChestY * gridsize, gridsize, gridsize)
        pygame.draw.rect(self.screen, pygame.Color('brown'), b)
        pygame.display.update()

    def drawPlayer(self):
        if self.model.won == False:
            p = pygame.Rect(self.model.Player.xpos * self.size[1]/float(self.model.y), self.model.Player.ypos * self.size[1]/float(self.model.y), self.size[1]/float(self.model.y), self.size[1]/float(self.model.y))
            pygame.draw.rect(self.screen, pygame.Color('white'), p)
            if self.model.Player.xpos != self.model.Player.history[0] or self.model.Player.ypos != self.model.Player.history[1]:
                b = pygame.Rect(self.model.Player.history[0] * self.size[1]/float(self.model.y), self.model.Player.history[1] * self.size[1]/float(self.model.y), self.size[1]/float(self.model.y), self.size[1]/float(self.model.y))
                pygame.draw.rect(self.screen, pygame.Color('black'), b)
            if self.model.Player.xpos != self.model.Player.history[2] or self.model.Player.ypos != self.model.Player.history[3]:
                b1 = pygame.Rect(self.model.Player.history[2] * self.size[1]/float(self.model.y), self.model.Player.history[3] * self.size[1]/float(self.model.y), self.size[1]/float(self.model.y), self.size[1]/float(self.model.y))
                pygame.draw.rect(self.screen, pygame.Color('black'), b1)
        else:
            self.screen.fill(pygame.Color('pink')) 
        pygame.display.update()

    def drawMonster(self):
        for monster in self.model.MonsterPack.monsters:
            # print len(self.model.MonsterPack.monsters)
            if self.model.eaten == False:
                p = pygame.Rect(monster.xpos * self.size[1]/float(self.model.y), monster.ypos * self.size[1]/float(self.model.y), self.size[1]/float(self.model.y), self.size[1]/float(self.model.y))
                pygame.draw.rect(self.screen, pygame.Color('green'), p)
                if monster.xpos != monster.history[0] or monster.ypos != monster.history[1]:
                    b = pygame.Rect(monster.history[0] * self.size[1]/float(self.model.y), monster.history[1] * self.size[1]/float(self.model.y), self.size[1]/float(self.model.y), self.size[1]/float(self.model.y))
                    pygame.draw.rect(self.screen, pygame.Color('black'), b)
                if monster.xpos != monster.history[2] or monster.ypos != monster.history[3]:
                    b1 = pygame.Rect(monster.history[2] * self.size[1]/float(self.model.y), monster.history[3] * self.size[1]/float(self.model.y), self.size[1]/float(self.model.y), self.size[1]/float(self.model.y))
                    pygame.draw.rect(self.screen, pygame.Color('black'), b1)
            else:
                self.screen.fill(pygame.Color('red'))
        pygame.display.update()

if __name__ == '__main__':
    pygame.init()
    screenX = 1080
    screenY = 720
    size = (screenX, screenY)
    screen = pygame.display.set_mode(size)
    model = DungeonModel(int(screenX/float(10)),int(screenY/float(10)),int(screenX/float(20)),int(screenY/float(20)))
    
    view = DungeonModelView(model, screen, size)
    pygame.key.set_repeat(350,35)
    # controller = PyGameMouseController(model)
    controller = PyGameKeyboardController(model) 
    running = True
    view.drawMap()
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running == False
                pygame.quit()
            controller.handle_event(event)
        view.drawPlayer()
        view.drawMonster()
        time.sleep(.01)


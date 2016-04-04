import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION



class PyGameKeyboardController(object):
    def __init__(self, model):
        self.model = model

    def handle_event(self, event):
        if event.type != KEYDOWN:
            return

        controllerDirections = {"U":(0,-1),"D":(0,1),"L":(-1,0),"R":(1,0)}
        if event.key == pygame.K_e:
            blockcoords = controllerDirections[self.model.Player.direction]
            block_to_interact_with = self.model.grid[self.model.Player.y+blockcoords[1]][self.model.Player.x+blockcoords[0]] #grid is nested lists, (x,y) is grid[y][x]
            block_to_interact_with.interact()

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
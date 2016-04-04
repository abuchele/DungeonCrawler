import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION



class PyGameKeyboardController(object):
    def __init__(self, model):
        self.model = model
        pygame.key.set_repeat(350,35)


    def handle_event(self, event):
        """
        takes a pygame event and executes on it. Returns True if the program should continue running
        """
        if event.type == KEYDOWN:

            controllerDirections = {"U":(0,-1),"D":(0,1),"L":(-1,0),"R":(1,0)}
            if event.key == pygame.K_e:
                blockcoords = controllerDirections[self.model.player.direction]
                block_to_interact_with = self.model.grid[self.model.player.y+blockcoords[1]][self.model.player.x+blockcoords[0]] #grid is nested lists, (x,y) is grid[y][x]
                block_to_interact_with.interact()

            if event.key == pygame.K_LEFT and not self.model.grid[self.model.player.y][self.model.player.x-1].collides:
                self.model.player.x -= 1
                self.model.player.direction = "L"
            elif event.key == pygame.K_RIGHT and not self.model.grid[self.model.player.y][self.model.player.x+1].collides:
                self.model.player.x += 1
                self.model.player.direction = "R"
            elif event.key == pygame.K_UP and not self.model.grid[self.model.player.y-1][self.model.player.x].collides:
                self.model.player.y -=1
                self.model.player.direction = "U"
            elif event.key == pygame.K_DOWN and not self.model.grid[self.model.player.y+1][self.model.player.x].collides:
                self.model.player.y +=1
                self.model.player.direction = "D"

            return True

        if event.type == QUIT:
            pygame.quit()
            return False

        return True
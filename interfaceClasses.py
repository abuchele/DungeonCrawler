import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION



class PyGameKeyboardController(object):
    def __init__(self, model):
        self.model = model

    def handle_event(self, event):
        if event.type != KEYDOWN:
            return

        if event.key == pygame.K_LEFT and not self.model.grid[self.model.Player.y][self.model.Player.x-1].collides:
            self.model.Player.x -= 1
            self.model.Player.direction = "L"
        elif event.key == pygame.K_RIGHT and not self.model.grid[self.model.Player.y][self.model.Player.x+1].collides:
            self.model.Player.x += 1
            self.model.Player.direction = "R"
        elif event.key == pygame.K_UP and not self.model.grid[self.model.Player.y-1][self.model.Player.x].collides:
            self.model.Player.y -=1
            self.model.Player.direction = "U"
        elif event.key == pygame.K_DOWN and not self.model.grid[self.model.Player.y+1][self.model.Player.x].collides:
            self.model.Player.y +=1
            self.model.Player.direction = "D"
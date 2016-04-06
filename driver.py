import time
import pygame

from dungeonGraphics import DungeonModelView
from interfaceClasses import PyGameKeyboardController
from Dungeon import Dungeon



if __name__ == '__main__':
    pygame.init()
    screenX = 1080
    screenY = 720
    size = (screenX, screenY)
    screen = pygame.display.set_mode(size)
    model = Dungeon(2*72,2*72,"whole")
    
    view = DungeonModelView(model, screen, size)
    controller = PyGameKeyboardController(model) 
    running = True
    view.display()
    while running:
        time.sleep(.25)

        events = pygame.event.get()
        if len(events) > 0:
            running = controller.handle_event(events[-1])

        view.display()

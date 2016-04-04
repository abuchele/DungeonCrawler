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

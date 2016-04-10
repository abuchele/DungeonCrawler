import time
import pygame
import pickle

from dungeonGraphics import DungeonModelView
from interfaceClasses import PyGameKeyboardController
from Dungeon import Dungeon
import pickle



if __name__ == '__main__':
    pygame.init()
    screenX = 1080
    screenY = 720
    size = (screenX, screenY)
    screen = pygame.display.set_mode(size)
    #model = Dungeon(2*72,2*72, method="whole")
    model = pickle.load(open("saves/pregeneratedDungeon.txt",'r'))
    
    view = DungeonModelView(model, screen, size)
    pygame.key.set_repeat(150,35)
    # controller = PyGameMouseController(model)
    controller = PyGameKeyboardController(model) 
    running = True
    view.display()
    while running:
        time.sleep(.1)

        events = pygame.event.get()
        if len(events) > 0:
            running = controller.handle_event(events[-1])

        view.display()

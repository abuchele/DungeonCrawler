import time
import pygame
import pickle
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION

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
    # controller = PyGameMouseController(model)
    controller = PyGameKeyboardController(model) 
    running = True
    view.display()
    while running:
        time.sleep(.15)
        running = controller.handle_all_events(pygame.event.get())
        model.update()
        view.display()

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
    pygame.key.set_repeat(200,10)
    # controller = PyGameMouseController(model)
    controller = PyGameKeyboardController(model) 
    running = True
    view.display()
    controls = {pygame.K_e:1,pygame.K_r:1,pygame.K_LEFT:1,pygame.K_RIGHT:1,pygame.K_UP:1,pygame.K_DOWN:1}
    while running:
        time.sleep(.1)

        events = pygame.event.get()
        # print events
        if len(events) > 0:
            for event in reversed(events):
                if event.type == KEYDOWN and event.key in controls:
                    running = controller.handle_event(event)#IF YOU LET GO OF THE KEY, THE LAST EVENT IS A KEY UP!!!
                    break
                if event.type == QUIT:
                    running = False
        view.display()

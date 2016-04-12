import time
import pygame
import pickle
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION

from dungeonGraphics import DungeonModelView
from interfaceClasses import PyGameKeyboardController
import coreMechanics
import pickle



if __name__ == '__main__':
    pygame.init()
    screenX = 1080
    screenY = 720
    size = (screenX, screenY)
    
    if raw_input("Would you like to start where you left off? [y/n]") == "y":
        model = coreMechanics.load("saves/last_save.dun")
    else:
        model = pickle.load(open("saves/pregeneratedDungeon.txt",'r'))

    screen = pygame.display.set_mode(size)
    view = DungeonModelView(model, screen, size)
    controller = PyGameKeyboardController(model) 

    running = True
    view.display()
    while running:
        time.sleep(.15)
        running = controller.handle_all_events(pygame.event.get())
        model.update()
        view.display()

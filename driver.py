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
    delay = 0.2
    
    if raw_input("Would you like to start where you left off? [y/n]") == "y":
        model = coreMechanics.load("saves/last_save.dun")
    else:
        model = pickle.load(open("saves/pregeneratedDungeon.dun",'r'))

    screen = pygame.display.set_mode(size)
    view = DungeonModelView(model, screen, size)
    controller = PyGameKeyboardController(model)
    events = []

    running = True
    view.update()
    while running:

        start_time = time.time()
        end_time = start_time+delay

        running = controller.handle_all_events(events)
        model.update()
        view.update()
        
        events = [] # I know what you're thinking: "What is this convoluted events variable? pygame does all that automatically. This variable should be entirely unnecessary to make the game function properly." to which I respond, "Yes, it should."
        while time.time() < end_time:
            events = events+pygame.event.get()
            view.display((time.time()-start_time)/delay)
        # model.update()
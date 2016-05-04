import time
import pygame
import pickle
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION

from dungeonGraphics import DungeonModelView
from interfaceClasses import PyGameKeyboardController
import coreMechanics
import pickle



def loadDungeon():
    return coreMechanics.load("saves/last_save.dun")



if __name__ == '__main__':
    pygame.init()
    screenX = 1080
    screenY = 720
    size = (screenX, screenY)
    delay = 0.15
    
    if raw_input("Would you like to start where you left off? [Y/n]") != "n":
        model = loadDungeon()
    else:
        model = coreMechanics.Dungeon(120, 120, method="whole")
        #model = pickle.load(open("saves/pregeneratedDungeon.dun",'r'))

    screen = pygame.display.set_mode(size)
    view = DungeonModelView(model, screen, size)
    controller = PyGameKeyboardController(model)
    events = []

    running = True
    view.update()
    while running:

        start_time = time.time()                        # start the timer
        end_time = start_time+delay

        running = controller.handle_all_events(events)  # update all objects
        model.update()
        view.update()

        if controller.reset:                            # reset to last save if necessary
            model = loadDungeon()
            controller.setModel(model)
            view.setModel(model)
        
        events = [] # I know what you're thinking: "What is this convoluted events variable? pygame does all that automatically. This variable should be entirely unnecessary to make the game function properly." to which I respond, "Yes, it should."
        while time.time() < end_time: #after each update is called, this while loop runs for (delay) seconds before the next update can happen
            events = events+pygame.event.get()
            view.display((time.time()-start_time)/delay)
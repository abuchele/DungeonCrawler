#!/usr/bin/python


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
    delay = 0.15 #length of each tick

    screen = pygame.display.set_mode(size)
    screen.blit(pygame.image.load("HUD_sprites/Opening.png"),(0,0)) # the opening screen
    pygame.display.update()
    
    running = False
    while not running:  # start by determining where to load the dungeon from
        for event in pygame.event.get():
            if event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.K_y:     # last save,
                    model = loadDungeon()
                    running = True
                elif event.key == pygame.K_n:
                    model = coreMechanics.Dungeon(120, 120, method="whole")
                    running = True                  # or brand new one?

    view = DungeonModelView(model, screen, size)
    controller = PyGameKeyboardController(model)
    events = []
    view.update()   # then jump into the main loop
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
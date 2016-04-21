import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION



class PyGameKeyboardController(object):
    def __init__(self, model):
        self.model = model
        self.controls = {pygame.K_e:1,pygame.K_r:1,pygame.K_LEFT:1,pygame.K_RIGHT:1,pygame.K_UP:1,pygame.K_DOWN:1,
            pygame.K_w:1,pygame.K_a:1,pygame.K_s:1,pygame.K_d:1}
        pygame.key.set_repeat(150,150)
        self.controllerDirections = {"U":(0,-1),"D":(0,1),"L":(-1,0),"R":(1,0)}


    def handle_all_events(self, events):
        if len(events) > 0:
            for event in reversed(events):
                if event.type == QUIT:
                        return False
                if self.model.state == "P":
                    if event.type == KEYDOWN:   # if it is paused, any key press resumes the game
                        self.model.resume()
                        return True
                elif self.model.state == "R":
                    if event.type == KEYDOWN and event.key in self.controls:
                        running = self.handle_event(event)#IF YOU LET GO OF THE KEY, THE LAST EVENT IS A KEY UP!!!
                        return True
                    if event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.model.pause()
                        return True
                elif self.model.state == "D":
                    if event.type == KEYDOWN:
                        self.model.advance_dialogue()
                        return True
            pygame.event.clear()  #empties queue
        return True


    def handle_event(self, event):
        """
        takes a pygame event and executes on it. Returns True if the program should continue running
        """
        self.model.player.hasAttacked = False
        if event.type == KEYDOWN:
            if event.key == pygame.K_e:
                blockcoords = self.model.player.facingCoordinates()
                monsters = self.model.monstercoords.get(blockcoords, 0)
                if monsters != 0:                           # if there is a mob,
                    self.model.interp_action(monsters[0].interact(self.model.player))   # interact with the mob
                else:                                                   # otherwise
                    block_to_interact_with = self.model.getBlock(*blockcoords)
                    self.model.interp_action(block_to_interact_with.interact(self.model.player)) # interact with the block and print the result
            if event.key == pygame.K_r:
                blockcoords = self.model.player.facingCoordinates() #this gives the (x,y) coordinate which you are facing!
                """If we have a monster list with coordinates, we iterate over the list to see if there's a monster on blockcoords."""

                target_to_attack = self.model.grid[blockcoords[1]][blockcoords[0]] #if we find no monster, this attacks a grid square or a block!

                self.model.player.attack(target_to_attack) #FEATURE UNDER DEVELOPMENT                

            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if self.model.player.direction == "L":
                    self.model.player.moving = True
                self.model.player.direction = "L"
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if self.model.player.direction == "R":
                    self.model.player.moving = True
                self.model.player.direction = "R"
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                if self.model.player.direction == "U":
                    self.model.player.moving = True
                self.model.player.direction = "U"
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if self.model.player.direction == "D":
                    self.model.player.moving = True
                self.model.player.direction = "D"

        pygame.event.clear()
        return True
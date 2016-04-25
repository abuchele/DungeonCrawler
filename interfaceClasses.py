import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION



class PyGameKeyboardController(object):
    def __init__(self, model):
        self.model = model
        self.controls = {pygame.K_e:1,pygame.K_r:1,pygame.K_LEFT:1,pygame.K_RIGHT:1,pygame.K_UP:1,pygame.K_DOWN:1,
            pygame.K_w:1,pygame.K_a:1,pygame.K_s:1,pygame.K_d:1,pygame.K_f:1,pygame.K_z:1,pygame.K_x:1}
        pygame.key.set_repeat()
        self.controllerDirections = {"U":(0,-1),"D":(0,1),"L":(-1,0),"R":(1,0)}


    def handle_all_events(self, events):
        self.model.player.listening = False
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
                        return self.handle_event(event)#IF YOU LET GO OF THE KEY, THE LAST EVENT IS A KEY UP!!!
                    if event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.model.pause()
                        return True
                elif self.model.state == "D":
                    if event.type == KEYDOWN:
                        self.model.advance_dialogue()
                        return True
            pygame.event.clear()  #empties queue

        held = pygame.key.get_pressed()  # if there are no key presses, check for keys being held down
        for key in self.controls:
            if held[key]:
                return self.handle_event(pygame.event.Event(KEYDOWN, key=key))
            else:
                self.model.player.listening = True
        return True


    def handle_event(self, event):
        """
        takes a pygame event and executes on it. Returns True if the program should continue running
        """
        self.model.player.hasAttacked = False
        self.model.player.listening = False
        if event.type == KEYDOWN:
            # if event.key == pygame.K_f:
            #     self.model.player.listening = True
            if event.key == pygame.K_e:
                blockcoords = self.model.player.facingCoordinates()
                monster = self.model.monstercoords.get(blockcoords, 0)
                if monster != 0:                           # if there is a mob,
                    self.model.current_interactee = monster
                    self.model.interp_action(monster.interact(self.model.player))   # interact with the mob
                else:                                                   # otherwise
                    block_to_interact_with = self.model.getBlock(*blockcoords)
                    self.model.interp_action(block_to_interact_with.interact(self.model.player)) # interact with the block and print the result
            elif event.key == pygame.K_r:
                blockcoords = self.model.player.facingCoordinates() #this gives the (x,y) coordinate which you are facing!
                """If we have a monster list with coordinates, we iterate over the list to see if there's a monster on blockcoords."""
                monster = self.model.monstercoords.get(blockcoords,0)
                if monster != 0:
                    target_to_attack = monster
                    # print "Attempting to attack entity!" + str(target_to_attack.__repr__)
                else:
                    target_to_attack = self.model.grid[blockcoords[1]][blockcoords[0]] #if we find no monster, this attacks a grid square or a block!
                self.model.player.attack(target_to_attack) #FEATURE UNDER DEVELOPMENT  
            elif event.key == pygame.K_z:
                self.model.player.decrementSong()
            elif event.key == pygame.K_x:
                self.model.player.incrementSong()

            elif event.key == pygame.K_LEFT:
                if self.model.player.direction == "L":
                    self.model.player.moving = True
                self.model.player.direction = "L"
            elif event.key == pygame.K_RIGHT:
                if self.model.player.direction == "R":
                    self.model.player.moving = True
                self.model.player.direction = "R"
            elif event.key == pygame.K_UP:
                if self.model.player.direction == "U":
                    self.model.player.moving = True
                self.model.player.direction = "U"
            elif event.key == pygame.K_DOWN:
                if self.model.player.direction == "D":
                    self.model.player.moving = True
                self.model.player.direction = "D"

            elif event.key == pygame.K_a:
                self.model.player.direction = "L"
                self.model.player.moving = True
            elif event.key == pygame.K_d:
                self.model.player.direction = "R"
                self.model.player.moving = True
            elif event.key == pygame.K_w:
                self.model.player.direction = "U"
                self.model.player.moving = True
            elif event.key == pygame.K_s:
                self.model.player.direction = "D"
                self.model.player.moving = True

        pygame.event.clear()
        return True
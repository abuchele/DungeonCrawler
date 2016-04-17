import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEMOTION



class PyGameKeyboardController(object):
    def __init__(self, model):
        self.model = model
        self.controls = {pygame.K_e:1,pygame.K_r:1,pygame.K_LEFT:1,pygame.K_RIGHT:1,pygame.K_UP:1,pygame.K_DOWN:1,
            pygame.K_w:1,pygame.K_a:1,pygame.K_s:1,pygame.K_d:1}
        pygame.key.set_repeat(1,35)
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
                block_to_interact_with = self.model.getBlock(*blockcoords) #grid is nested lists, (x,y) is grid[y][x]
                self.model.interp_action(block_to_interact_with.interact(self.model.player)) # interact with the block and print the result
            if event.key == pygame.K_r:
                blockcoords = self.model.player.facingCoordinates() #this gives the (x,y) coordinate which you are facing!
                # targetcoords = self.controllerDirections[self.model.player.direction]
                target_to_attack = self.model.grid[blockcoords[1]][blockcoords[0]]
                # if type(target_to_attack).__name__ != Entity: #.__name__ isn't recognized, apparently
                #     return
                self.model.player.attack(target_to_attack) #FEATURE UNDER DEVELOPMENT                

            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if not self.model.grid[self.model.player.y][self.model.player.x-1].collides:
                    self.model.player.x -= 1
                self.model.player.direction = "L"
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if not self.model.grid[self.model.player.y][self.model.player.x+1].collides:
                    self.model.player.x += 1
                self.model.player.direction = "R"
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                if not self.model.grid[self.model.player.y-1][self.model.player.x].collides:
                    self.model.player.y -=1
                self.model.player.direction = "U"
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                if not self.model.grid[self.model.player.y+1][self.model.player.x].collides:
                    self.model.player.y +=1
                self.model.player.direction = "D"
            pygame.event.clear()
            return True

        if event.type == QUIT:
            pygame.quit()
            return False

        return True
import pygame
from pygame.locals import QUIT, KEYDOWN
import pygame.mixer
import entities



class PyGameKeyboardController(object):
    def __init__(self, model):
        pygame.mixer.init()
        self.attackSongs = [pygame.mixer.Sound('sounds/songZ{}.wav'.format(i)) for i in range(0,8)]
        self.model = model
        self.controls = {pygame.K_e:1,pygame.K_r:1,pygame.K_LEFT:1,pygame.K_RIGHT:1,pygame.K_UP:1,pygame.K_DOWN:1,
        pygame.K_w:1,pygame.K_a:1,pygame.K_s:1,pygame.K_d:1,pygame.K_TAB:1,pygame.K_LSHIFT:1,
        pygame.K_1:1,pygame.K_2:1,pygame.K_3:1,pygame.K_4:1,pygame.K_5:1,pygame.K_6:1,pygame.K_7:1,pygame.K_g:1,pygame.K_i:1}

        pygame.key.set_repeat()
        self.reset = False


    def handle_all_events(self, events):
        self.model.player.listening = False
        if len(events) > 0:
            for event in reversed(events):
                if event.type == QUIT:
                        return False
                if self.model.state == "P": #Paused
                    if event.type == KEYDOWN:   # if it is paused, any key press resumes the game
                        self.model.resume()
                        return True
                elif self.model.state == "R": #Running
                    if event.type == KEYDOWN and event.key in self.controls:
                        return self.handle_event(event)#IF YOU LET GO OF THE KEY, THE LAST EVENT IS A KEY UP!!!
                    if event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.model.pause()
                        return True
                    if event.type == KEYDOWN and event.key == pygame.K_RETURN: #Menu
                        self.model.menu_pause()
                        return True
                elif self.model.state == "D": #Dialogue
                    if event.type == KEYDOWN:
                        self.model.advance_dialogue()
                        return True
                elif self.model.state == "K": #killed.
                    if event.type == KEYDOWN:
                        self.reset = True
                elif self.model.state == "M": #Menu
                    if event.type == KEYDOWN:
                        self.model.resume()
                        return True
            pygame.event.clear()  #empties queue

        if self.model.state == "R":
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
        self.model.player.listening = False
        if event.type == KEYDOWN and self.model.state=="R":
            # if event.key == pygame.K_f:
            #     self.model.player.listening = True
            if event.key == pygame.K_i:
                self.handlePlayerInventory()
            elif event.key == pygame.K_e:
                blockcoords = self.model.player.facingCoordinates()
                monster = self.model.monstercoords.get(blockcoords, 0)
                if monster != 0:                           # if there is a mob,
                    self.model.current_interactee = monster
                    self.model.interp_action(monster.interact(self.model.player))   # interact with the mob
                else:                                                   # otherwise
                    block_to_interact_with = self.model.getBlock(*blockcoords)
                    self.model.interp_action(block_to_interact_with.interact(self.model.player)) # interact with the block and print the result
            elif event.key == pygame.K_r:
                if self.model.player.attackCooldown <= 0 and len(self.model.player.availableSong) > 0:
                    self.model.player.playSong()
                    self.attackSongs[self.model.player.song].play()
            elif event.key == pygame.K_TAB:
                if self.model.player.attackCooldown <= 0:
                    self.model.player.incrementSong()
            elif event.key == pygame.K_LSHIFT:
                if self.model.player.attackCooldown <= 0:
                    self.model.player.decrementSong()
            elif event.key == pygame.K_g:
                if self.model.player.hasBullet:
                    self.model.player.shoot()

            elif event.key >= 49 and event.key <= 55:   # these are the number keys
                if event.key-49 in self.model.player.availableSong:
                    self.model.player.song = event.key-49

            elif event.key == pygame.K_a:
                if self.model.player.direction == "L":
                    self.model.player.moving = self.model.player.attackCooldown <= 0
                self.model.player.direction = "L"
            elif event.key == pygame.K_d:
                if self.model.player.direction == "R":
                    self.model.player.moving = self.model.player.attackCooldown <= 0
                self.model.player.direction = "R"
            elif event.key == pygame.K_w:
                if self.model.player.direction == "U":
                    self.model.player.moving = self.model.player.attackCooldown <= 0
                self.model.player.direction = "U"
            elif event.key == pygame.K_s:
                if self.model.player.direction == "D":
                    self.model.player.moving = self.model.player.attackCooldown <= 0
                self.model.player.direction = "D"

            elif event.key == pygame.K_LEFT:
                self.model.player.direction = "L"
                self.model.player.moving = self.model.player.attackCooldown <= 0
            elif event.key == pygame.K_RIGHT:
                self.model.player.direction = "R"
                self.model.player.moving = self.model.player.attackCooldown <= 0
            elif event.key == pygame.K_UP:
                self.model.player.direction = "U"
                self.model.player.moving = self.model.player.attackCooldown <= 0
            elif event.key == pygame.K_DOWN:
                self.model.player.direction = "D"
                self.model.player.moving = self.model.player.attackCooldown <= 0

            else:
                raise ValueError("{} is not a valid command.".format(event.key))

        pygame.event.clear()
        return True

    def handlePlayerInventory(self):
        self.model.pause()
        print "Inventory: " + str(self.model.player.inventory)
        userInput = raw_input("Use an item by typing its name and pressing Enter. Type 'exit' to exit.")
        while userInput.lower() != 'exit':
            item = entities.parseItem(userInput)
            # print item.__repr__()
            item.use(self.model.player)
            userInput = raw_input("Use another item?")
        self.model.resume()


    def setModel(self, model):
        self.model = model
        self.reset = False
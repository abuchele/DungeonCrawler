"""
To-do:

Sprites for different entities


Notes:

Removed need for global variables. Now initializing player requires x, y, and grid, and each monster needs x, y, player and grid.
It's a bit more of a pain to initialize (more variables required) but we can change stuff and feed it in, instead of them grabbing the global 
    value for 'player' and 'grid'.
"""

from random import randint, choice
import pygame
import math


"""Changes:"""

# added 'effect' -> basically, being poisoned or something. It's a dictionary, with True or False for whether the effect is active. We can add in what the effect actually does eventually. 
# also added the action of being effected, and can call Entity.active_effects() to get a list of all active effects. 

# added in items, and made it so items can be added to the inventory and used, along with some fun text descriptions for their appearence and usage.
# made potion class, for easy potion making (writing all those descriptions is a pain, this way you just have to put what they do)

# also added max health, so that when the player uses potions they can't go past their max health. 

# ex: Anna.effected('poisoned') -> "You've been poisoned!" -> Anna.effect['poisoned'] = True -> Anna.active_effects = ['poisoned'] -> cure_potion = Potion('cure','poisoned') 
# 	  cure_potion.pickup(Anna) -> (fun flair text) -> Anna.inventory = {'Weird Blue Potion' , 1} -> cure_potion.use(Anna) -> (fun cured flair text) -> Anna.active_effects = []


"""General Classes"""

class Entity(object):
    def __init__(self, model, x=0, y=0, monstercoords = 0, direction="U", speed=1, name = None):
        self.model = model       
        self.direction = direction #direction can be U for up, D for down, L for left, R for right
        self.speed = speed
        self.effect = dict()
        self.directionCoordinates = {"U":(0,-1),"D":(0,1),"L":(-1,0),"R":(1,0)} # a table of which directions means which coordinates
        self.moving = False
        self.x = x
        self.y = y
        self.prex = x
        self.prey = y
        self.attackCooldown = 0
        self.monstercoords = monstercoords
        
    def attackRoll(self): #1d20+accuracy, if it exceeds armor class it's a hit
        return randint(1,20)+self.accuracy #roll a 20-sided dice and add accuracy to the roll - average is 10.5 + accuracy

    def damage(self):
        return randint(1,self.damageRange)+self.flatDamage #roll a damageRange-sided dice and add flatDamage to the roll

    def attack(self,that):
        try:
            if self.attackRoll() >= that.armor:
                damage = self.damage()
                that.damaged(damage)
                self.model.interp_action("{} hits {} for {} damage!".format(str(self),str(that),damage))
            # if this.name!="You":
            #     print "{} misses {}!".format(str(this),str(that))
            else:
                self.model.interp_action("{} misses {}!".format(str(self),str(that)))
            # print "Attacked entity!"
        except AttributeError:
            pass
            # print "Attacked tile!"

    def damaged(self, damage):
        self.health -= damage

    def effected(self,effect_specific):
    	self.effect[effect_specific] = True
    	p = ''
    	return p.join([self.name," has been ",effect_specific,'!'])

    def active_effects(self):
    	effect_list=list()
    	for x in self.effect:
    		if self.effect[x] is True:
    			effect_list.append(x)
    	return effect_list

    def facingCoordinates(self):    # the coordinates of the block you are facing
        return (self.x+self.directionCoordinates[self.direction][0], self.y+self.directionCoordinates[self.direction][1])

    def getCoords(self, t):   # calculates coordinates based on current x,y, previous x,y, and time t
        if self.x != self.prex or self.y != self.prey:
            return (self.x*t + self.prex*(1-t), self.y*t + self.prey*(1-t))
        else:
            return (self.x, self.y)

    def update(self):
        self.prex, self.prey = (self.x, self.y)
        if self.moving and not self.model.grid[self.facingCoordinates()[1]][self.facingCoordinates()[0]].collides and not self.monstercoords.has_key(self.facingCoordinates()):
            self.x, self.y = self.facingCoordinates()
        self.moving = False
        if self.attackCooldown>0:
            self.attackCooldown -= 1

    def interact(self,player):
        return "You poke the thing."

"""Player Related"""

# I think the inventory should be a dictionary: inventory[Item] = quantity. 
class Player(Entity):
    def __init__(self,model,monstercoords,x,y, name = "Ray"):
        Entity.__init__(self,model,x,y, monstercoords) #grid is a global variable which needs to be defined before initializing any entities.
        self.health = 100
        self.maxhealth = 100
        self.armor= 10
        self.accuracy = 20
        self.flatDamage = 2
        self.damageRange = 5
        self.damageMod = 2
        self.inventory = dict()
        self.name = name
        self.sprite = (0,0)
        self.steps = 0
        self.attackCooldown = 0
        self.healCooldown = 0
        self.listening = False
        self.earshot = [] # the area currently being attacked
        self.song = 0   # the selected attack song
        self.lastSong = 0
        self.nextSong = 0
        self.availableSong = [0,1,2,3,4,5,6]  # which songs you can play
        
    def __str__(self):
        return self.name

    def editinventory(self,Item,add=True): #add is whether the item is being added or removed. if True, the item is being added, if False, the item is being removed.
    	quantity = self.inventory.get(Item,0)
    	if add == True:
    		quantity += 1
    	else:
    		quantity += -1
    	self.inventory[Item] = quantity
    	if quantity == 0:
    		del self.inventory[Item]

    def incrementSong(self):    # switches to the next song
        self.song, self.lastSong = (self.nextSong, self.song)
        newSongIdx = self.availableSong.index(self.song)+1
        self.nextSong = self.availableSong[newSongIdx%len(self.availableSong)]

    def decrementSong(self):    # switches to the last song
        self.song, self.nextSong = (self.lastSong, self.song)
        newSongIdx = self.availableSong.index(self.song)-1
        self.lastSong = self.availableSong[newSongIdx%len(self.availableSong)]

    def playSong(self):
        if self.song == 0:      # basic attack
            self.playSong0()
        elif self.song == 1:    # spread attack
            self.playSong1()
        elif self.song == 2:    # range attack
            self.playSong2()
        elif self.song == 3:    # stun attack
            self.playSong3()
        elif self.song == 4:    # grenade attack
            self.playSong4()
        elif self.song == 5:    # flamethrower attack
            self.playSong5()
        elif self.song == 6:    # octothorpe attack
            self.playSong6()
        else:
            raise TypeError("{} is not a defined song!".format(self.song))

    def getCurrentSprite(self):   # figures out which sprite to use for the entity
        if not self.moving:   # if the player has not moved
            self.steps = 0    # then they use the standing sprite
        else:
            if self.steps is not 2:
                self.steps += 1
            else:
                self.steps = 1
        if self.direction == "U":
            return (0,self.steps)
        elif self.direction == "D":
            return (1,self.steps)
        elif self.direction == "L":
            return (2,self.steps)
        elif self.direction == "R":
            return (3,self.steps)

    def damaged(self,damage):
        self.healCooldown = 10
        Entity.damaged(self,damage)

    def update(self):   # just kind of moves you around
        self.sprite = self.getCurrentSprite()
        if self.healCooldown > 0:
            self.healCooldown -= 1
        elif self.health < 100:
            self.health += 1
        Entity.update(self)

    def playSong0(self):    # basic attack
        self.earshot = [self.facingCoordinates()]   # you attack the block in front of you
        self.attackCooldown = 2
        self.flatDamage, self.damageRange = (3,5)   #dps = 6
        if self.model.monstercoords.has_key(self.earshot[0]):
            self.attack(self.model.monstercoords[self.earshot[0]])

    def playSong1(self):    # blast attack
        self.earshot = []
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                self.earshot.append((self.x+dx, self.y+dy)) # you attack all adjacent blocks
        self.attackCooldown = 2
        self.flatDamage, self.damageRange = (0,2)   #dps = 1.5
        for place_to_attack in self.earshot:
            if self.model.monstercoords.has_key(place_to_attack):
                self.attack(self.model.monstercoords[place_to_attack])
        self.attack(self)

    def playSong2(self):    # ranged attack
        self.attackCooldown = 2
        self.flatDamage, self.damageRange = (1,2)   #dps = 2.5
        self.earshot = []
        coords = (self.x, self.y)
        direc = self.directionCoordinates[self.direction]
        for i in range(6):
            coords = (coords[0]+direc[0], coords[1]+direc[1])
            self.earshot.append(coords)
            if self.model.monstercoords.has_key(coords):
                self.attack(self.model.monstercoords[coords])
                break
            elif self.model.getBlock(*coords).collides:
                break

    def playSong3(self):    # stun attack
        self.attackCooldown = 4
        self.earshot = []
        for dx in range(-2,3):
            for dy in range(-2,3):
                if (dx+dy)%2 == 1:
                    self.earshot.append((self.x+dx, self.y+dy))
        for place_to_stun in self.earshot:
            if self.monstercoords.has_key(place_to_stun):
                self.model.interp_action(self.monstercoords[place_to_stun].effected("stunned"))

    def playSong4(self):    # grenade attack
        self.attackCooldown = 2
        self.flatDamage, self.damageRange = (0,1)   #dps = 1
        epicenter = (self.x,self.y)
        direc = self.directionCoordinates[self.direction]
        for i in range(5):
            epicenter = (epicenter[0]+direc[0], epicenter[1]+direc[1])
            if self.model.monstercoords.has_key(epicenter) or self.model.getBlock(*epicenter).collides:
                break
        epicenter = (epicenter[0]-direc[0], epicenter[1]-direc[1])
        self.earshot = []
        for dx, dy in [(1,0), (0,1), (-1,0), (0,-1), (0,0)]:
            if not self.model.getBlock(epicenter[0]+dx, epicenter[1]+dy).collides:
                for ddx, ddy in [(1,0), (0,1), (-1,0), (0,-1)]:
                    if not (epicenter[0]+dx+ddx, epicenter[1]+dy+ddy) in self.earshot:
                        self.earshot.append((epicenter[0]+dx+ddx, epicenter[1]+dy+ddy))
        for place_to_attack in self.earshot:
            if self.monstercoords.has_key(place_to_attack):
                self.attack(self.monstercoords[place_to_attack])
            elif place_to_attack == (self.x,self.y):
                self.attack(self)

    def playSong5(self):    # flamethrower attack
        self.attackCooldown = 2
        self.earshot = []
        coords = (self.x, self.y)
        direc = self.directionCoordinates[self.direction]
        for i in range(0,3):
            coords = (coords[0]+direc[0], coords[1]+direc[1])
            if self.model.getBlock(*coords).collides:
                break
            for sign in [-1,1]:
                for j in range(0, sign*(i+1), sign):
                    newCoords = (coords[0]+j*direc[1], coords[1]+j*direc[0])
                    if self.model.getBlock(*newCoords).collides:
                        break
                    self.earshot.append(newCoords)
        for place_to_burn in self.earshot:
            if self.monstercoords.has_key(place_to_burn):
                self.model.interp_action(self.monstercoords[place_to_burn].effected("ignited"))

    def playSong6(self):    # octothorpe attack
        self.attackCooldown = 6
        self.flatDamage, self.damageRange = (3,8)   #dps = 7.5
        self.earshot = []
        for dx in [-2,-1,0,1,2]:
            for dy in [-1,1]:
                self.earshot.append((self.x+dx, self.y+dy))
        for dy in [-2, 0, 2]:
            for dx in [-1,1]:
                self.earshot.append((self.x+dx, self.y+dy))
        for place_to_attack in self.earshot:
            if self.monstercoords.has_key(place_to_attack):
                self.attack(self.monstercoords[place_to_attack])
        

"""Monster Subclass"""

class Monster(Entity):
    def __init__(self, x, y, player, model, monstercoords): #speed =256,  flatDamage=0, armor=0):
        Entity.__init__(self,model,x,y, monstercoords)
        self.aggro = False
        self.seen = False #With large numbers of monsters, we want them idle when out of player vision
        self.name = None
        self.seenrange = 8
        self.aggrorange = 2
        self.player = player
        self.distance = 0   # it moves when this reaches 256

    def __str__(self):
        return self.name

    def checkstatus(self):
        self.seen = (abs(self.x - self.player.x)<=self.seenrange and abs(self.y - self.player.y)<=self.seenrange)
        # print "seen:", self.seen
            # self.seen = True
        self.aggro = (abs(self.x - self.player.x)<=self.aggrorange and abs(self.y - self.player.y)<=self.aggrorange)
        # print "aggro:", self.aggro
            # self.aggro = True

    def passiveMove(self): # decides where to move and sets its variables accordingly
        if randint(1,2) == 1:
            direction = ["R","D","L","U"]
            self.direction = choice(direction)
            self.moving = True
        # print (self.x,self.y), (self.player.x,self.player.y), "Passively Moving"

    def aggressiveMove(self): # decides where to move and sets its variables accordingly
        self.moving = True    # the monster will greedy-first search the player
        delX, delY = (self.x-self.player.x, self.y-self.player.y)
        matchX = (self.x-int(math.copysign(1,delX)), self.y) # where it will go if it wants to match X
        matchY = (self.x, int(self.y-math.copysign(1,delY))) # where it will go if it wants to match Y
        if self.monstercoords.has_key(matchX) or self.model.grid[matchX[1]][matchX[0]].collides:      # matching X is no good
            self.direction = {1:"U",-1:"D"}[math.copysign(1,delY)]                              # so go vertical
        elif self.monstercoords.has_key(matchY) or self.model.grid[matchY[1]][matchY[0]].collides:    # matching Y is no good
            self.direction = {1:"L",-1:"R"}[math.copysign(1,delX)]                              # so go horizontal
        elif abs(delX) < abs(delY):                                                             # both are open, but the vertical distance is greater
            self.direction = {1:"U",-1:"D"}[math.copysign(1,delY)]                              # so go vertical
        else:                                                                                   # vice versa
            self.direction = {1:"L",-1:"R"}[math.copysign(1,delX)]                              # so go horizontal


    def decide(self): #monster checks its own status, then takes either a move or an attack action. We assume monster is melee.
        self.checkstatus()
        if self.aggro == True:
            if (self.x-self.player.x == 0 and (self.y-self.player.y == 1 or self.y-self.player.y == -1)) or ((self.x-self.player.x == 1 or self.x-self.player.x == -1) and self.y-self.player.y == 0):
                self.attack(self.player)
            else:
                self.aggressiveMove()
        elif self.seen == True:
            self.passiveMove()

    def update(self):
        if self.effect.get("stunned",False):    # if you are stunned
            if randint(1,50) == 1:             # you cannot move
                self.effect["stunned"] = False
        else:
            self.distance += self.speed
            if self.distance >= 256:
                self.distance -= 256
                self.decide()
        if self.effect.get("ignited",False) and randint(1,3) == 1:  # if you are on fire
            self.health -= 1                                        # you might take damage
            if randint(1,40) == 1:
                self.effect["ignited"] = False
        Entity.update(self)

    def interact(self,player):
        return "You try to poke the "+self.name+", but it swats your hand away."



class Zombie(Monster):
    def __init__(self,x,y, player, grid, monstercoords):
        Monster.__init__(self, x,y, player, grid, monstercoords)
        self.name = "Zombie"
        self.health = 10
        self.accuracy = 3
        self.damageRange = 3
        self.flatDamage = 2
        self.armor = 8
        self.speed = 127    # speed goes from 1 to 256
        if randint(0,1) == 0:
            self.sprite = 2
        else:
            self.sprite = 3

class Ghost(Monster):
    def __init__(self,x,y, player, grid, monstercoords):
        Monster.__init__(self, x,y, player, grid, monstercoords)
        self.name = "Ghost"
        self.health = 6
        self.accuracy = 4
        self.damageRange = 2
        self.flatDamage = 1
        self.armor = 10
        self.speed = 150
        self.sprite = 1

    def aggressiveMove(self):
        self.moving = True    # the monster will greedy-first search the player
        delX, delY = (self.x-self.player.x, self.y-self.player.y)
        matchX = (self.x-int(math.copysign(1,delX)), self.y) # where it will go if it wants to match X
        matchY = (self.x, int(self.y-math.copysign(1,delY))) # where it will go if it wants to match Y
        if self.monstercoords.has_key(matchX):                      # matching X is no good
            self.direction = {1:"U",-1:"D"}[math.copysign(1,delY)]  # so go vertical
        elif self.monstercoords.has_key(matchY):                    # matching Y is no good
            self.direction = {1:"L",-1:"R"}[math.copysign(1,delX)]  # so go horizontal
        elif abs(delX) < abs(delY):                                 # both are open, but the vertical distance is greater
            self.direction = {1:"U",-1:"D"}[math.copysign(1,delY)]  # so go vertical
        else:                                                       # vice versa
            self.direction = {1:"L",-1:"R"}[math.copysign(1,delX)]  # so go horizontal

    def update(self):
        self.distance += self.speed
        if self.distance >= 256:
            self.distance -= 256
            self.decide()
        self.prex, self.prey = (self.x, self.y)
        if self.moving and not self.monstercoords.has_key(self.facingCoordinates()):
            self.x, self.y = self.facingCoordinates()
        self.moving = False


class Demon(Monster):
    def __init__(self,x,y, player, model, monstercoords):
        Monster.__init__(self, x,y, player, model, monstercoords)
        self.name = "Demon"
        self.health = 15
        self.accuracy = 1
        self.damageRange = 6
        self.flatDamage = 2
        self.armor = 5
        self.speed = 64
        self.sprite = 0


class Skeleton(Monster):
    def __init__(self,x,y, player, model, monstercoords):
        Monster.__init__(self, x,y, player, model, monstercoords)
        self.name = "Skeleton"
        self.health = 20
        self.accuracy = 5
        self.damageRange = 1
        self.flatDamage = 4
        self.armor = 10
        self.speed = 100
        self.sprite = 0


"""NPC Subclass"""

class NPC(Monster): # people who do not take damage, and have dialogue
    def __init__(self,model,x,y,player,checklist,name,sprite,convID=0):
        Monster.__init__(self,x,y,player,model, 0)
        self.name = name
        self.sprite = sprite
        self.convID = convID
        self.checklist = checklist
        self.health = 9001

    def interact(self,player):
        return "$D{}".format(self.convID)

    def decide(self):
        pass

    def post_dialogue_action(self, conv_id):
        pass

# Perhaps we should organize the code such that everything to do with the player is in one section
#The group of NPCs is in another, and then the monsters and such are in a third.  

class MrE(NPC):
    def __init__(self, model, x, y, player, checklist):
        NPC.__init__(self, model, x, y, player, checklist, "Mr. E", 4)

    def interact(self,player):
        if not self.checklist.state["player_Named"]:
            return "$D001"
        elif not self.checklist.state["tutorial_Dialogue002_Finished"]:
            return "$D002"
        elif 1==2: #Need to put in a condition if the player tries to open a door.  
            return "$D003"
        elif not self.checklist.state["tutorial_Dialogue004_Finished"]:
            return "$D004"
        elif not self.checklist.state["tutorial_Dialogue005_Finished"]:
            return "$D005"
        elif not self.checklist.state["tutorial_Dialogue006_Finished"]:
            return "$D006"
        elif (self.checklist.state["killcount"] >= 3) and not self.checklist.state["tutorial_quest_finished"]:
            return "$D008"
        elif not self.checklist.state["tutorial_quest_finished"]:
            return "$D007"
        elif not self.checklist.state["kerberoge_start"]:
            return "$D009"
    def post_dialogue_action(self, conv_id):
        if conv_id == 1:
            name = raw_input("What is your name?")
            self.player.name = name
            self.checklist.eventcomplete("player_Named")
            return
        if conv_id == 2:
            self.checklist.eventcomplete("tutorial_Dialogue002_Finished")
        elif conv_id == 4:
            self.checklist.eventcomplete("tutorial_Dialogue004_Finished")
        elif conv_id == 5:
            self.checklist.eventcomplete("tutorial_Dialogue005_Finished")
        elif conv_id == 6:
            self.checklist.eventcomplete("tutorial_Dialogue006_Finished")
        elif conv_id == 8:
            self.checklist.eventcomplete("tutorial_quest_finished")


"""Entity Related Subclasses that aren't entities"""

# allows easy creation/organization of different attacks and their stats (useful if a creature has more than one attack)
class Attack(Entity):
	def __init__(self,preattack,attack,postattack,damage,range,accuracy):
		pass

class Effect(object):
	def __init__(self,effect_type,effect_description,effect_value=10,effect_specific=None):
		self.effect_type = effect_type
		self.effect_value = effect_value
		self.effect_description = effect_description
		self.no_effect_description = "It doesn't seem to do anything."
		self.effect_specific = effect_specific
	def effect_on(self,Entity):
		if self.effect_type == 'heal':
			if Entity.health < Entity.maxhealth:
				if Entity.health + self.effect_value < Entity.maxhealth:
					Entity.health += self.effect_value
				else:
					Entity.health = Entity.maxhealth
			else:
				return self.no_effect_description
		elif self.effect_type == 'cure':
			if self.effect_specific == None:
				Entity.effect = dict()
				Entity.health = Entity.maxhealth
			elif Entity.effect[self.effect_specific] == True:
				Entity.effect[self.effect_specific] = False
				Entity.health += self.effect_value-10
			else:
				return self.no_effect_description
		return self.effect_description
		#add in other effects as we come up with them

class Item(object):
	def __init__(self,name,description,use_description='What are you going to do with that?',effect=None,target=None,image=None):
		self.name = name
		self.description = description
		self.use_description = use_description
		self.effect = effect
		self.image = image
		self.target = target
	def __str__(self):
		return self.name
	def read_description(self):
		return self.description
	def pickup(self,Entity):
		s = ' '
		Entity.editinventory(self.name)
		return s.join([Entity.name,'picks up',self.description])
		# need to remove item from map
	def use(self,Entity):
		if Entity.inventory.get(self.name,0) > 0:
			if self.effect is not None:
				Entity.editinventory(self.name,False)
				return self.use_description + self.effect.effect_on(Entity)
			return self.use_description
		else:
			return "You don't have that."

class Potion(Item):
	def __init__(self,effect_type,effect_class=1,effect_specific = None,image=None):
		self.effect_type = effect_type 
		self.effect_class = effect_class	# effect class is the 'strength' of the potion. 1 is normal, 2 is really good.
		self.effect_specific = effect_specific
		s = ' '
		p = ''
		if effect_class == 1:
			color_description = 'murky'
			name_description = 'Weird'
			end_description = 'It looks pretty gross.'
			use_description = 'It tastes about how you expected. '
			other_description = "It's nice to not be"
		else:
			color_description = 'clear'
			name_description = 'Clear'
			end_description = 'It actually looks drinkable.'
			use_description = 'It tastes surprisingly nice. '
			other_description = 'You actually feel better than you did before you were'
		if effect_type == 'heal':
			color = 'green'
			self.effect_description = 'You feel rejuvinated! Whew!'
			other_description = ''
		elif effect_type == 'cure':
			if effect_specific == 'poisoned':
				color = 'blue'
				self.effect_description = s.join(['You feel the poison leaving your body. What a relief!', other_description, p.join([effect_specific,'!'])])
			elif effect_specific == 'paralyzed':
				color = 'amber'
				self.effect_description = s.join(["You can move freely again!",other_description, 'paralyzed!'])
			else:
				color = 'red'
				self.effect_description = 'You feel better than you have ever felt!'

		ncolor = color.capitalize()
		self.description = s.join(['a vial filled with a',color_description,color,'liquid.',end_description])
		self.name = s.join([name_description,ncolor,'Potion'])
		self.use_description = s.join(['You drink the',p.join([self.name,'.']),use_description])
		self.effect = Effect(self.effect_type,self.effect_description,10*(self.effect_class*2),effect_specific=self.effect_specific)
		self = Item(self,self.name,self.description,self.use_description,self.effect)

if __name__ == "__main__":
    player = Player("model", 0,0)
    d = []
    for i in range (5):
        zombie = Zombie(randint(1,20),randint(1,20), player, "model")
        d.append(zombie)
    for monster in d:
        monster.checkstatus()
        print (monster.x,monster.y),monster.seen,monster.aggro

    c = Ghost(2,2, player, "model")
    # print b.attack(a)
    print player.attack(c)
    print c.attack(player)
    # print a.inventory
    # jar = Item('Jar','an empty glass jar.')
    # print jar.pickup(a)
    # print a.inventory
    # frog = Item('Frog',"a frog. It isn't moving. Is it dead?",)
    # print frog.pickup(a)
    # print a.inventory
    # print frog.use(a)
    # heal = Potion('cure',1,'poisoned')
    # print heal.pickup(a)
    # print a.effected('poisoned')
    # print a.active_effects()
    # print heal.use(a)
    # print a.active_effects()

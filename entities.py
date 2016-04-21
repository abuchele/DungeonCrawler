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
    def __init__(self, grid, x=0, y=0, direction="U", speed=1, phasing = False, name = None, effect = dict(), hasAttacked = False):
        self.grid = grid       
        self.direction = direction #direction can be U for up, D for down, L for left, R for right
        self.speed = speed
        self.effect = effect
        self.phasing = phasing
        self.directionCoordinates = {"U":(0,-1),"D":(0,1),"L":(-1,0),"R":(1,0)} # a table of which directions means which coordinates
        self.moving = False
        self.x = x
        self.y = y
        self.prex = x
        self.prey = y
        self.hasAttacked = hasAttacked
        
    def attackRoll(self): #1d20+accuracy, if it exceeds armor class it's a hit
        return randint(1,20)+self.accuracy #roll a 20-sided dice and add accuracy to the roll - average is 10.5 + accuracy

    def damage(self):
        return randint(1,self.damageRange)+self.flatDamage #roll a damageRange-sided dice and add flatDamage to the roll

    def attack(this,that):
        try:
            if this.attackRoll() >= that.armor:
                damage = this.damage()
                that.health -= damage
                if this.name!="You":
                    print "{} hits {} for {} damage!".format(str(this),str(that),damage)
                
                
                """Pseudocode"""
                # DISPLAY pygame.rotate(this.attackSprite, direction_to_angle[this.direction]) AT (this.x+this.directionCoordinates[0],this.y+this.directionCoordinates[1])
                return "{} hit {} for {} damage!".format(str(this),str(that),damage)

            if this.name!="You":
                print "{} misses {}!".format(str(this),str(that))
            return "{} miss {}!".format(str(this),str(that))
            this.hasAttacked = True
        except AttributeError:
            this.hasAttacked = True

    def effected(self,effect_specific):
    	self.effect[effect_specific] = True
    	p = ''
    	return p.join(["You've been ",effect_specific,'!'])

    def active_effects(self):
    	effect_list=list()
    	for x in self.effect:
    		if self.effect[x] is True:
    			effect_list.append(x)
    	return effect_list

    def facingCoordinates(self):    # the coordinates of the block you are facing
        return (self.x+self.directionCoordinates[self.direction][0], self.y+self.directionCoordinates[self.direction][1])

    def getCoords(self, t):   # calculates coordinates based on current x,y, previous x,y, and time t
        return (self.x*t + self.prex*(1-t), self.y*t + self.prey*(1-t))

    def update(self):
        self.prex, self.prey = (self.x, self.y)
        if self.moving and not self.grid[self.facingCoordinates()[1]][self.facingCoordinates()[0]].collides:
            self.x, self.y = self.facingCoordinates()
        self.moving = False

    def interact(self,player):
        return "You poke the thing."

"""Player Related"""

# I think the inventory should be a dictionary: inventory[Item] = quantity. 
class Player(Entity):
    def __init__(self,grid,x,y, name = "Ray"):
        Entity.__init__(self,grid,x,y) #grid is a global variable which needs to be defined before initializing any entities.
        self.health = 100
        self.maxhealth = 100
        self.armor = 10
        self.accuracy = 2
        self.flatDamage = 2
        self.damageRange = 2
        self.damageMod = 2
        self.inventory = dict()
        self.name = name
        self.sprite = (0,0)
        self.steps = 0
        self.attackSprite = 3 #sprites is a list of .png images, so this calls sprites[self.attackSprite]
        self.hasAttacked = False
        
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

    def update(self):   # just kind of moves you around
        self.sprite = self.getCurrentSprite()
        Entity.update(self)
        

"""Monster Subclass"""

class Monster(Entity):
    def __init__(self, x, y, player, grid): #speed =256,  flatDamage=0, armor=0):
        Entity.__init__(self,grid,x,y)
        self.aggro = False
        self.seen = False #With large numbers of monsters, we want them idle when out of player vision
        self.name = None
        self.seenrange = 8
        self.aggrorange = 5
        self.player = player
        self.distance = 0   # it moves when this reaches 256

    def checkstatus(self):
        self.seen = (abs(self.x - self.player.x)<=self.seenrange or abs(self.y - self.player.y)<=self.seenrange)
        # print "seen:", self.seen
            # self.seen = True
        self.aggro = (abs(self.x - self.player.x)<=self.aggrorange or abs(self.y - self.player.y)<=self.aggrorange)
        # print "aggro:", self.aggro
            # self.aggro = True

    def passiveMove(self): # decides where to move and sets its variables accordingly
        direction = ["R","D","L","U"]
        if self.phasing == False:
            if self.grid[self.y][self.x+1].collides:
                direction.remove("R")
            if self.grid[self.y+1][self.x].collides:
                direction.remove("D")
            if self.grid[self.y][self.x-1].collides:
                direction.remove("L")
            if self.grid[self.y-1][self.x].collides:
                direction.remove("U")
        self.direction = choice(direction)
        self.moving = True
        # print (self.x,self.y), "Passively Moving"

    def aggressiveMove(self): # decides where to move and sets its variables accordingly
        self.moving = True
        if self.phasing == False: #There's probably a more efficient way to do this, but it'll work for now.
            if (self.x>self.player.x+1 or (self.x>self.player.x and self.y!=self.player.y)) and not self.grid[self.y][self.x-1].collides:
                self.direction = "L"
                # print "i'm to the player's right!"
            elif (self.x<self.player.x-1 or (self.x<self.player.x and self.y!=self.player.y)) and not self.grid[self.y][self.x+1].collides:
                self.direction = "R"
                # print "i'm to the player's left!"
            else:
                if (self.y>self.player.y+1 or (self.y>self.player.y and self.x!=self.player.x)) and not self.grid[self.y-1][self.x].collides:
                    self.direction = "U"
                if (self.y<self.player.y-1 or (self.y<self.player.y and self.x!=self.player.x)) and not self.grid[self.y+1][self.x].collides:
                    self.direction = "D"
        else:
            if self.x>self.player.x+1 or (self.x>self.player.x and self.y!=self.player.y):
                self.direction = "L"
                # print "i'm to the player's right!"
            elif self.x<self.player.x-1 or (self.x<self.player.x and self.y!=self.player.y):
                self.direction = "R"
                # print "i'm to the player's left!"
            else:
                if self.y>self.player.y+1 or (self.y>self.player.y and self.x!=self.player.x):
                    self.direction = "U"
                if self.y<self.player.y-1 or (self.y<self.player.y and self.x!=self.player.x):
                    self.direction = "D"
        # print (self.x,self.y), "Aggressively Moving"

    def decide(self): #monster checks its own status, then takes either a move or an attack action. We assume monster is melee.
        self.checkstatus()
        if self.aggro == True:
            if (self.x-self.player.x == 0 and (self.y-self.player.y == 1 or self.y-self.player.y == -1)) or ((self.x-self.player.x == 1 or self.x-self.player.x == -1) and self.y-self.player.y == 0):
                self.attack(self.player)
            else:
                self.aggressiveMove()
        elif self.seen == True:
            self.passiveMove()

    def think(self):
        self.distance += self.speed
        if self.distance >= 256:
            self.distance -= 256
            self.decide()

    def interact(self,player):
        return "You try to poke the "+self.name+", but it swats your hand away."



class Zombie(Monster):
    def __init__(self,x,y, player, grid):
        Monster.__init__(self, x,y, player, grid)
        self.name = "Zombie"
        self.health = 30
        self.accuracy = 3
        self.damageRange = 3
        self.flatDamage = 2
        self.armor = 8
        self.speed = 127    # speed goes from 1 to 256
        if randint(0,1) == 0:
            self.sprite = 2
        else:
            self.sprite = 3
    def __str__(self):
        return "Zombie"

class Ghost(Monster):
    def __init__(self,x,y, player, grid):
        Monster.__init__(self, x,y, player, grid)
        self.name = "Ghost"
        self.health = 20
        self.accuracy = 4
        self.damageRange = 2
        self.flatDamage = 1
        self.armor = 10
        self.speed = 150
        self.phasing = True
        self.sprite = 1
    def __str__(self):
        return "Ghost"



"""NPC Subclass"""

class NPC(Monster): # people who do not take damage, and have dialogue
    def __init__(self,grid,x,y,player,checklist,name,sprite,convID=0):
        Monster.__init__(self,x,y,player,grid)
        self.name = name
        self.sprite = sprite
        self.convID = convID
        self.checklist = checklist

    def interact(self,player):
        return "$D{}".format(self.convID)

    def decide(self):
        pass

# Perhaps we should organize the code such that everything to do with the player is in one section
#The group of NPCs is in another, and then the monsters and such are in a third.  

class MrE(NPC):
    def __init__(self, grid, x, y, player, checklist):
        NPC.__init__(self, grid, x, y, player, checklist, "Mr. E", 4)

    def interact(self,player):
        if not self.checklist.player_Named:
            return "$D001"
        elif not self.checklist.tutorial_Dialogue002_Finished:
            return "$D002"
        else:
            return "$D003"


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
    player = Player("grid", 0,0)
    d = []
    for i in range (5):
        zombie = Zombie(randint(1,20),randint(1,20), player, "grid")
        d.append(zombie)
    for monster in d:
        monster.checkstatus()
        print (monster.x,monster.y),monster.seen,monster.aggro

    c = Ghost(2,2, player, "grid")
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

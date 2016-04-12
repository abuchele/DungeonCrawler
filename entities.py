"""
To-do:

Sprites for different entities


Notes:

Removed need for global variables. Now initializing player requires x, y, and grid, and each monster needs x, y, player and grid.
It's a bit more of a pain to initialize (more variables required) but we can change stuff and feed it in, instead of them grabbing the global 
    value for 'player' and 'grid'.
"""

from random import randint



"""Changes:"""

# added 'effect' -> basically, being poisoned or something. It's a dictionary, with True or False for whether the effect is active. We can add in what the effect actually does eventually. 
# also added the action of being effected, and can call Entity.active_effects() to get a list of all active effects. 

# added in items, and made it so items can be added to the inventory and used, along with some fun text descriptions for their appearence and usage.
# made potion class, for easy potion making (writing all those descriptions is a pain, this way you just have to put what they do)

# also added max health, so that when the player uses potions they can't go past their max health. 

# ex: Anna.effected('poisoned') -> "You've been poisoned!" -> Anna.effect['poisoned'] = True -> Anna.active_effects = ['poisoned'] -> cure_potion = Potion('cure','poisoned') 
# 	  cure_potion.pickup(Anna) -> (fun flair text) -> Anna.inventory = {'Weird Blue Potion' , 1} -> cure_potion.use(Anna) -> (fun cured flair text) -> Anna.active_effects = []


class Entity(object):
    def __init__(self, grid, health=30, maxhealth=30, speed=1, accuracy=2, flatDamage = 2, damageRange=2, damageMod=2, vision=3, armor=10, phasing = False, name = None, effect = dict()):
        # self.xpos = xpos
        # self.ypos = ypos
        self.grid = grid        
        self.speed = speed
        self.health = health
        self.maxhealth = maxhealth
        self.effect = effect
        self.accuracy = accuracy
        self.flatDamage = flatDamage
        self.damageRange = damageRange
        self.damageMod = damageMod
        self.vision = vision #sight radius
        self.armor = armor
        self.phasing = phasing
    def attackRoll(self): #1d20+accuracy, if it exceeds armor class it's a hit
        return randint(1,20)+self.accuracy #roll a 20-sided dice and add accuracy to the roll - average is 10.5 + accuracy
    def damage(self):
        return randint(1,self.damageRange)+self.flatDamage #roll a damageRange-sided dice and add flatDamage to the roll
    def attack(this,that):
        if this.attackRoll() >= that.armor:
            damage = this.damage()
            that.health -= damage
            if this.name!="You":
                return "{} hits {} for {} damage!".format(str(this),str(that),damage)
            return "{} hit {} for {} damage!".format(str(this),str(that),damage)
        return "{} misses {}!".format(str(this),str(that))
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


# I think the inventory should be a dictionary: inventory[Item] = quantity. 
class Player(Entity):
    def __init__(self,x,y, grid, direction="U", health = 100, maxhealth = 100, inventory = dict(), name = "You"):
        Entity.__init__(self,grid) #grid is a global variable which needs to be defined before initializing any entities.
        self.x = x
        self.y = y
        # self.history = (xpos,ypos, xpos, ypos)
        self.direction = direction #direction can be U for up, D for down, L for left, R for right
        # self.speed = speed
        self.health = health
        self.maxhealth = maxhealth
        self.inventory = inventory
        self.name = name
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





class Monster(Entity):
    def __init__(self, player, grid): #speed =1,  flatDamage=0, armor=0):
        Entity.__init__(self,grid)
        self.aggro = False
        self.seen = False #With large numbers of monsters, we want them idle when out of player vision
        self.name = None
        self.seenrange = 8
        self.aggrorange = 5
        self.player = player
        # self.grid = grid #we shouldn't need this, since Entity takes grid

    def checkstatus(self):
        if abs(self.x-self.player.x)<=self.seenrange or abs(self.y-self.player.y)<=self.seenrange:
            self.seen = True
        if abs(self.x-self.player.x)<=self.aggrorange or abs(self.y-self.player.y)<=self.aggrorange:
            self.aggro = True



    def passiveMove(self):
        # if self.seen = True:
        direction = [(1,0),(0,1),(-1,0),(0,-1)]
        if self.grid[self.x+1,self.y].collides():
            direction.remove((1,0))
        if self.grid[self.x,self.y+1].collides():
            direction.remove((0,1))
        if self.grid[self.x-1,self.y].collides():
            direction.remove((-1,0))
        if self.grid[self.x,self.y-1].collides():
            direction.remove((0,-1))
        move = direction[randint(0,3)]
        self.x+=move[0]
        self.y+=move[1]
    def aggressiveMove(self,that):
        pass



class Zombie(Monster):
    def __init__(self,x,y, player, grid):
        Monster.__init__(self, player, grid)
        self.x = x
        self.y = y
        self.health = 30
        self.accuracy = 3
        self.damageRange = 3
        self.flatDamage = 2
        self.armor = 8
        self.speed = 1
    def __str__(self):
        return "Zombie"

class Ghost(Monster):
    def __init__(self,x,y, player, grid):
        Monster.__init__(self, player, grid)
        self.x = x
        self.y = y
        self.health = 20
        self.accuracy = 4
        self.damageRange = 2
        self.flatDamage = 1
        self.armor = 10
        self.speed = 1
        self.phasing = True
    def __str__(self):
        return "Ghost"        

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



player = Player(0,0, "grid")
d = []
for i in range (5):
    zombie = Zombie(randint(1,20),randint(1,20), player, "grid")
    d.append(zombie)
for monster in d:
    monster.checkstatus()
    print (monster.x,monster.y),monster.seen,monster.aggro



c = Ghost(2,2, player, "grid")
# print b.attack(a)
# print player.attack(c)
# print c.attack(player)
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
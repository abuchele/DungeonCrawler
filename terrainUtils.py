import random as rng
import math

import entities



class Block(object):
	def __init__(self, biome=-1):
		self.explored = False
		self.biome = biome
		self.sound = -1

	def passable(self):
		return not self.collides

	def interact(self, player):
		return "Boop."


class Null(Block):
	def __init__(self, biome=-1):
		Block.__init__(self, biome)
		self.color = (0,0,0)
		self.collides = False
		self.transparent = False
		self.sprite = 0

	def __str__(self):
		return "nl"

	def interact(self,player):
		return ""


class Floor(Block):
	def __init__(self, biome=-1):
		Block.__init__(self, biome)
		self.color = (200,200,200)
		self.collides = False
		self.transparent = True
		random= rng.random()
		if random < 0.05:
			self.sprite = rng.choice([37,44,45])
		elif random <0.15:
			self.sprite = rng.choice([38,39,40,41,42,43])
		elif random <0.40:
			self.sprite = rng.choice([51,50])
		else:
			self.sprite = 1

	def __str__(self):
		return "  "

	def interact(self,player):
		if self.sprite == 37:
			return "I hope those aren't human bones."

		elif self.sprite == 44:
			return "It looks like... moss?"			

		elif self.sprite == 45:
			return "It's a puddle of... probably something gross."	
		else:	
			return rng.choice(["An empty space.","Nothing to interact with here.","I wonder why there's tile down here.","The tile is a bit cracked."])


class Stone(Block):
	def __init__(self, biome=-1):
		Block.__init__(self, biome)
		self.color = (80,80,80)
		self.collides = True
		self.transparent = False
		self.sprite = 2

	def __str__(self):
		return "@@"

	def interact(self,player):
		return rng.choice(["It looks like some kind of sandstone... or maybe ignimbrite?","You lick the rock. It tastes dirty.","The walls here are surprisingly smooth."])


class Brick(Block):
	def __init__(self, biome=-1):
		Block.__init__(self, biome)
		self.color = (70,70,70)
		self.collides = True
		self.transparent = False
		self.blank = True
		self.density = 0.25
		if rng.random() < 0.25:
			self.blank = False
		self.blankSprites = [29,30,31,32,33,34,35,36]
		self.objectSprites = [19,20,21,22,23,24,25,26,27,28]
		if self.blank == True:
			self.sprite = rng.choice(self.blankSprites)
		else:
			self.sprite = rng.choice(self.objectSprites)

	def __str__(self):
		return "##"

	def interact(self,player):
		if self.sprite == 19:
			return "You decide not to think about that."

		elif self.sprite == 20:
			return "Huh, what purpose would that serve?"

		elif self.sprite == 21:
			return "There is a crack in the wall. It looks very artistic, don't you think?"

		elif self.sprite == 22:
			return "There is a crack in the wall."

		elif self.sprite == 23:
			return "Yikes. It looks like something was trying to break out of here."

		elif self.sprite == 24:
			return "Umm, is that blood?"

		elif self.sprite == 25:
			return "Gross."

		elif self.sprite == 26:
			return "There's a spiderweb on the wall. No spider, though."

		elif self.sprite == 27:
			return "There's a spiderweb on the wall. No spider, though."

		elif self.sprite == 28:
			return "A lamp. How nice."

		elif self.sprite > 28:
			return rng.choice(["These stone bricks are huge!","Clearly man-made; who built this, and why?","The bricks are cold."])

class Door(Block):
	def __init__(self, biome=-1):
		Block.__init__(self, biome)
		self.color = (140,140,140)
		self.collides = True
		self.sprite = 5
		self.transparent = False

	def __str__(self):
		return "/\\"

	def passable(self):
		return True

	def open(self):
		self.color = (160,160,160)
		self.collides = False
		self.sprite = 4
		self.transparent = True

	def close(self):
		self.color = (120,120,120)
		self.collides = True
		self.sprite = 5
		self.transparent = False

	def interact(self, player):
		self.sound = 2
		if self.collides:
			self.open()
			return rng.choice(["You push the door open.","The door slides into the ground.","The door creaks as it moves out of the way."])
		else:
			self.close()
			return rng.choice(["You close the door behind you.","The door slides out of the ground.","With a great heft, you pull the door up."])


class Lava(Block):
	def __init__(self, biome=-1):
		Block.__init__(self, biome)
		self.color = (255,20,0)
		self.collides = False
		self.transparent = True
		self.sprite = 6

	def __str__(self):
		return "::"

	def passable(self):
		return False

	def interact(self,player):
		return rng.choice(["You can feel the heat from here.","I'd better not fall into that.","Magma... I must be deep!"])


class Bedrock(Block):
	def __init__(self, biome=-1):
		Block.__init__(self, biome)
		self.color = (0,0,0)
		self.collides = True
		self.transparent = False
		self.sprite = 7

	def __str__(self):
		return "BB"

	def interact(self,player):
		return rng.choice(["This rock is corse and tough.","You bite the rock. Mm, crunchy!","If you look closely, you can see minerals sparkling in the stone wall."])


class Obsidian(Block):
	def __init__(self, biome=-1):
		Block.__init__(self, biome)
		self.color = (80,10,100)
		self.collides = True
		self.transparent = False
		self.sprite = 8

	def __str__(self):
		return "XX"

	def interact(self,player):
		return rng.choice(["The lava rock here is shiny and purple.","The walls are pourus and sharp.","This rooms seems to be a drained lava chamber."])


class Glass(Block):
	def __init__(self, biome=-1):
		Block.__init__(self, biome)
		self.color = (240,240,240)
		self.collides = True
		self.transparent = True
		self.sprite = 9

	def __str__(self):
		return "||"

	def interact(self,player):
		return rng.choice(["I wonder how they got glass down here.","The glass is surprisingly clean.","You breathe on the glass and draw a smiley face."])


class Metal(Block):
	def __init__(self, biome=-1):
		Block.__init__(self, biome)
		self.color = (140,140,140)
		self.collides = True
		self.transparent = False
		self.sprite = 10

	def __str__(self):
		return "//"

	def interact(self,player):
		return rng.choice(["The walls here are metal and hollow.","You knock on the wall, and hear a resounding clang.","There are no bolts here; the metal is fused together."])


class Furniture(Block):
	def __init__(self, biome=-1):
		Block.__init__(self, biome)
		self.color = (200,150,120)
		self.collides = True
		self.transparent = True
		self.sprite = rng.choice([14,15,16,17,18,46,47,48,49])

	def __str__(self):
		return "TT"

	def interact(self,player):
		if self.sprite == 14:
			return rng.choice(["There is nothing on this table.","You lean on the table, and it wobbles dangerously.","The surface of the table is caked in dust."])
		elif self.sprite == 15:
			return rng.choice(["You sit down, and then stand back up.","This chair has a broken leg.","This must be the time-out chair."])
		elif self.sprite == 16:
			return "You examine a random book: "+rng.choice(["Death of Pi","To Murder a Mockingbird","The Afterlife for Dummies","Basics of Pomegrante Gardening","Twilight","Bury Potter and the Dead Hallows","Dealing with Grief","Pictures of Puppies","It's Okay to be Dead"])
		else:
			return rng.choice(["What a comfy-looking couch.","You would sit, but it's filled with holes.","You reach under the cusions and find a penny."])


class Loot(Block):
	def __init__(self, value, islocked = False, isopen = False, biome=-1):
		Block.__init__(self, biome)
		self.color = (255,250,0)
		self.collides = True
		self.transparent = True
		self.raised = True
		self.islocked = islocked
		self.isopen = isopen
		if self.isopen == True:
			self.sprite = 13
			self.contents = None
		else:
			self.sprite = 12
			self.contents = []
			if rng.random() < 0.5:
				self.contents.append(entities.Item('Frog',"a frog. It isn't moving. Is it dead?")) #contents can be a list of stuff
			if rng.random() < 0.2:
				self.contents.append(entities.MusicSheet(rng.choice([1,3,5])))	# chests can have odd songs
			if rng.random() < 0.95:
				self.contents.append(entities.Potion('heal',1))

	def __str__(self):
		return "[]"

	def interact(self, player):
		if self.isopen == True:
			return "This chest has been emptied."
			#Have way to unlock
		elif self.islocked == True:
			return "This chest is locked."
		else:
			self.color = (229,225,50)
			self.sprite = 13
			if self.contents == None:
				return "The chest is empty."
			else:
				for item in self.contents:
					player.editinventory(item)
				self.isopen = True
				self.contents = None
				return "You loot the chest of its contents."


class Node(object):	# used for my A* search
	def __init__(self, x,y,xf,yf,parent,cost):
		self.x = x
		self.y = y
		if parent != None:
			self.parent = parent
			self.g = parent.g+cost
		else:
			self.parent = None
			self.g = 0
		self.h = abs(x-xf) + abs(y-yf)
		self.f = self.g+self.h

	def __lt__(this, that):	# if x < y then y is objectively better than x i.e. x is redundant
		return this.x == that.x and this.y == that.y and this.f >= that.f
import random as rng
import math
from pygame import image



class Block(object):
	def __init__(self):
		self.explored = False

	def passable(self):
		return not self.collides

	def interact(self, player):
		print rng.choice(self.descriptions)


class Null(Block):
	def __init__(self):
		Block.__init__(self)
		self.color = (0,0,0)
		self.collides = False
		self.transparent = False
		self.descriptions = ["There's nothing there."]
		self.sprite = image.load("sprites/Null.png")

	def __str__(self):
		return "nl"

class NPC(Block): #all we need is an opaque impassable block that can move and talk to you. Take passive move from entities
	def __init__(self):
		Block.__init__(self)
		self.collides = True
		self.transparent = False
		pass

class Floor(Block):
	def __init__(self):
		Block.__init__(self)
		self.color = (200,200,200)
		self.collides = False
		self.transparent = True
		self.descriptions = ["An empty space.","Nothing to interact with here.","I wonder why there's tile down here."]
		self.sprite = image.load("sprites/Floor.png")

	def __str__(self):
		return "  "


class Stone(Block):
	def __init__(self):
		Block.__init__(self)
		self.color = (80,80,80)
		self.collides = True
		self.transparent = False
		self.descriptions = ["It looks like some kind of sandstone... or maybe ignimbrite?","You lick the rock. It tastes dirty.","The walls here are surprisingly smooth."]
		self.sprite = image.load("sprites/Stone.png")

	def __str__(self):
		return "@@"


class Brick(Block):
	def __init__(self):
		Block.__init__(self)
		self.color = (70,70,70)
		self.collides = True
		self.transparent = False
		self.descriptions = ["These stone bricks are huge!","Clearly man-made; who built this, and why?","The bricks are cold."]
		self.sprite = image.load("sprites/Brick.png")

	def __str__(self):
		return "##"


class Door(Block):
	def __init__(self, open=False):
		Block.__init__(self)
		if open:
			self.color = (160,160,160)
			self.collides = False
			self.sprite = image.load("sprites/DoorOpen.png")
		else:
			self.color = (120,120,120)
			self.collides = True
			self.sprite = image.load("sprites/DoorClosed.png")
		self.transparent = False
		self.descriptions = ["The door is locked.","It appears to slide down into the ground when unlocked.","This is some high-quality mahogany"]

	def __str__(self):
		return "/\\"

	def passable(self):
		return True

	def open(self):
		self.color = (160,160,160)
		self.collides = False
		self.sprite = image.load("sprites/DoorOpen.png")

	def interact(self, player):
		self.open()


class Lava(Block):
	def __init__(self):
		Block.__init__(self)
		self.color = (255,20,0)
		self.collides = False
		self.transparent = True
		self.descriptions = ["You can feel the heat from here.","I'd better not fall into that.","Magma... I must be deep!"]
		self.sprite = image.load("sprites/Lava.png")

	def __str__(self):
		return "::"


class Bedrock(Block):
	def __init__(self):
		Block.__init__(self)
		self.color = (0,0,0)
		self.collides = True
		self.transparent = False
		self.descriptions = ["This rock is corse and tough.","You bite the rock. Mm, crunchy!","If you look closely, you can see minerals sparkling in the stone wall."]
		self.sprite = image.load("sprites/Bedrock.png")

	def __str__(self):
		return "BB"


class Obsidian(Block):
	def __init__(self):
		Block.__init__(self)
		self.color = (80,10,100)
		self.collides = True
		self.transparent = False
		self.descriptions = ["The lava rock here is shiny and purple.","The walls are pourus and sharp.","This rooms seems to be a drained lava chamber."]
		self.sprite = image.load("sprites/Obsidian.png")

	def __str__(self):
		return "XX"


class Glass(Block):
	def __init__(self):
		Block.__init__(self)
		self.color = (240,240,240)
		self.collides = True
		self.transparent = True
		self.descriptions = ["I wonder how they got glass down here.","The glass is surprisingly clean.","You breathe on the glass and draw a smiley face."]
		self.sprite = image.load("sprites/Glass.png")

	def __str__(self):
		return "||"

class Metal(Block):
	def __init__(self):
		Block.__init__(self)
		self.color = (140,140,140)
		self.collides = True
		self.transparent = False
		self.descriptions = ["The walls here are metal and hollow.","You knock on the wall, and hear a resounding clang.","There are no bolts here; the metal is fused together."]
		self.sprite = image.load("sprites/Metal.png")

	def __str__(self):
		return "//"

class OneWayGlass(Block):
	def __init__(self, direction):
		Block.__init__(self)
		self.color = (240,240,240)
		self.collides = True
		self.transparent = True
		self.direction = direction
		self.descriptions = ["This wall seems opaque, but you can just barely make something out on the other side."]
		self.sprite = image.load("sprites/Metal.png")

	def __str__(self):
		if self.direction == 0:
			return " >"
		elif self.direction == 1:
			return "^^"
		elif self.direction == 2:
			return "< "
		else:
			return "vv"

class Loot(Block):
	def __init__(self, value, contents = None):
		Block.__init__(self)
		self.color = (255,250,0)
		self.collides = True
		self.transparent = True
		self.raised = True
		self.descriptions = ["This chest is locked."]
		self.sprite = image.load("sprites/Loot.png")
		self.contents = contents #contents can be a list of stuff

	def __str__(self):
		return "[]"

	def interact(self, player):
		if self.contents == None:
			print "The chest is empty."
		else:
			for item in self.contents:
				player.inventory[item]=player.inventory.get(item, 0)+1


class Node(object):	# used for my A* search in the "halls" algorithm
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


class SquareRoom(object):	# used in basic generation
	def __init__(self):
		self.left = "solid"
		self.top = "solid"
		self.floor = "solid"

	def clear(self):	# clears the room
		self.floor = "open"

	def randomizeLeft(self):
		r = rng.random()
		if r < .7:
			self.left = "door"
		elif r < .9:
			self.left = "open"
		else:
			self.left = "glass"

	def randomizeTop(self):
		r = rng.random()
		if r < .7:
			self.top = "door"
		elif r < .9:
			self.top = "open"
		else:
			self.top = "glass"


class RectRoom(object):	# used in hall generation
	def __init__(self, x0, y0, x1, y1):
		self.x = min(x0,x1)
		self.y = min(y0,y1)
		self.w = abs(x0-x1)
		self.h = abs(y0-y1)
		self.dx = 0
		self.dy = 0

	def __str__(self):
		return "<({},{}),({},{})>".format(self.x, self.y, self.x+self.w, self.y+self.h)

	def __eq__(this, that):
		return this.x == that.x and this.y == that.y and this.w == that.w and this.h == that.h

	def intersect(this,that):
		"""
		calculates the intersection of two rooms as (x1,y1,x2,y2)
		>>> RectRoom(0,0,3,4).intersect(RectRoom(1,2,5,4))
		(1, 2, 3, 4)
		>>> RectRoom(0,0,1,1).intersect(RectRoom(5,5,1,1)) == None
		True
		"""
		if this.x-that.x >= 0 and this.x-that.x < that.w:	# this is right of that
			if this.y-that.y >= 0 and this.y-that.y < that.h:	# this is below that
				return (this.x, this.y, that.x+that.w, that.y+that.h)
			if that.y-this.y >= 0 and that.y-this.y < this.h:	# this is above that
				return (this.x, that.y, that.x+that.w, this.y+this.h)
		if that.x-this.x >= 0 and that.x-this.x < this.w:	# this is left of that
			if this.y-that.y >= 0 and this.y-that.y < that.h:	# this is below that
				return (that.x, this.y, this.x+this.w, that.y+that.h)
			if that.y-this.y >= 0 and that.y-this.y < this.h:	# this is above that
				return (that.x, that.y, this.x+this.w, this.y+this.h)
		return None

	def push(this, that): # repels that
		mass = this.intersect(that)
		if mass == None:
			return
		xcm = (mass[0]+mass[2])/2.0
		ycm = (mass[1]+mass[3])/2.0
		delX = this.x+this.w/2.0-xcm
		delY = this.y+this.h/2.0-ycm
		delR = math.hypot(delX, delY)
		if delR == 0:
			delR = 1.0
			delX = math.sin(rng.random()*math.pi/2)
			delY = math.sqrt(1-delX**2)
		this.dx = this.dx + delX/delR
		this.dy = this.dy + delY/delR

	def move(self):
		dr = math.hypot(self.dx, self.dy)	# normalizes velocity to 1
		if dr == 0:
			return
		self.x = self.x+self.dx/dr
		self.y = self.y+self.dy/dr
		self.dx = 0
		self.dy = 0

	def round(self):
		self.x = int(self.x)
		self.y = int(self.y)
		self.w = int(self.w)
		self.h = int(self.h)
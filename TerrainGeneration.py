import math
import random as rng


class Block(object):
	def __init__(self):
		self.color = (0,0,0)
		self.collides = False


class Floor(Block):
	def __init__(self):
		self.color = (200,200,200)
		self.collides = False

	def __str__(self):
		return "  "


class Stone(Block):
	def __init__(self):
		self.color = (50,50,50)
		self.collides = True

	def __str__(self):
		return "##"


class Door(Block):
	def __init__(self):
		self.color = (150,150,150)
		self.collides = False

	def __str__(self):
		return "/\\"


class Lava(Block):
	def __init__(self):
		self.color = (255,20,0)
		self.collides = False

	def __str__(self):
		return "~~"


class Bedrock(Block):
	def __init__(self):
		self.color = (0,0,0)
		self.collides = True

	def __str__(self):
		return "[]"


class Obsidian(Block):
	def __init__(self):
		self.color = (30,0,50)
		self.collides = True

	def __str__(self):
		return "XX"


class Glass(Block):
	def __init__(self):
		self.color = (220,220,220)
		self.collides = True

	def __str__(self):
		return "||"

class OneWayGlass(Block):
	def __init__(self):
		self.color = (220,220,220)
		self.collides = True
		self.direction = 0

	def __str__(self):
		if self.direction == 0:
			return ">>"
		elif self.direction == 1:
			return "^^"
		elif self.direction == 2:
			return "<<"
		else:
			return "vv"


class SquareRoom(object):
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


class Dungeon(object):
	def __init__(self, method):
		if method == "basic":
			self.grid = self.generateBasic(9,9,4,4)
		elif method == "panel":
			self.grid = self.generatePanel()
		elif method == "round":
			self.grid = self.generateRound()
		elif method == "halls":
			self.grid = self.generateHalls()
		else:
			self.grid = [[]]

	def __str__(self):
		output = ""
		for row in self.grid:
			for blk in row:
				output = output+str(blk)
			output = output+"\n"
		return output


	def generateBasic(self,w,h,x0,y0):	# generates a grid of square rooms separated by various kinds of wall
		bigGrid = []
		for y in range(0,h):
			row = []
			for x in range(0,w):
				row.append(SquareRoom())
			bigGrid.append(row)
		self.dig(x0,y0,bigGrid)

		fineGrid = []
		for y in range(0,12*h):
			row = []
			for x in range(0,12*w):
				row.append(Stone())
			row.append(Stone())
			fineGrid.append(row)
		row = []
		for x in range(0,12*w+1):
			row.append(Stone())
		fineGrid.append(row)
		for ry in range(0,h):
			for rx in range(0,w):
				if bigGrid[ry][rx].floor == "open":
					for dy in range(1,12):
						for dx in range(1,12):
							fineGrid[12*ry+dy][12*rx+dx] = Floor()

				if bigGrid[ry][rx].left == "door":	# finish the walls
					fineGrid[12*ry+rng.randint(1,11)][12*rx] = Door()
				elif bigGrid[ry][rx].left == "open":
					for dy in range(1,12):
						fineGrid[12*ry+dy][12*rx] = Floor()
				elif bigGrid[ry][rx].left == "glass":
					for dy in range(1,12):
						fineGrid[12*ry+dy][12*rx] = Glass()
				if bigGrid[ry][rx].top == "door":
					fineGrid[12*ry][12*rx+rng.randint(1,11)] = Door()
				elif bigGrid[ry][rx].top == "open":
					for dx in range(1,12):
						fineGrid[12*ry][12*rx+dx] = Floor()
				elif bigGrid[ry][rx].top == "glass":
					for dx in range(1,12):
						fineGrid[12*ry][12*rx+dx] = Glass()
		return fineGrid


	def dig(self,x,y, grid, d=7, bearing=-1):	# starts a tunnel here
		grid[y][x].clear()
		prob = (d/7.0)

		if bearing != 0 and x >= 1 and rng.random() < prob:		# left
			grid[y][x].randomizeLeft()
			self.dig(x-1, y, grid, d=d-1, bearing=2)
		if bearing != 1 and y >= 1 and rng.random() < prob:		# up
			grid[y][x].randomizeTop()
			self.dig(x, y-1, grid, d=d-1, bearing=3)
		if bearing != 2 and x < len(grid[0])-1 and rng.random() < prob:	# right
			grid[y][x+1].randomizeLeft()
			self.dig(x+1, y, grid, d=d-1, bearing=0)
		if bearing != 3 and y < len(grid)-1 and rng.random() < prob:	# down
			grid[y+1][x].randomizeTop()
			self.dig(x, y+1, grid, d=d-1, bearing=1)


if __name__ == "__main__":
	test = Dungeon("basic")
	print test
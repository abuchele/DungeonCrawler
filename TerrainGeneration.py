import math
import random as rng
import numpy as np
from scipy.spatial import Delaunay
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree



class Block(object):
	def __init__(self):
		self.color = (0,0,0)
		self.collides = False

	def isLava(self):
		return False


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
		self.color = (100,100,100)
		self.collides = False

	def __str__(self):
		return "/\\"


class Lava(Block):
	def __init__(self):
		self.color = (255,20,0)
		self.collides = False

	def __str__(self):
		return "()"

	def isLava(self):
		return True


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

class Metal(Block):
	def __init__(self):
		self.color = (150,150,150)
		self.collides = True

	def __str__(self):
		return "//"

class OneWayGlass(Block):
	def __init__(self, direction):
		self.color = (220,220,220)
		self.collides = True
		self.direction = direction

	def __str__(self):
		if self.direction == 0:
			return " >"
		elif self.direction == 1:
			return "^^"
		elif self.direction == 2:
			return "< "
		else:
			return "vv"

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


class Dungeon(object):
	def __init__(self, method):
		if method == "basic":
			self.grid = self.generateBasic(9,9,4,4,8)
		elif method == "panel":
			self.grid = self.generatePanel(72,72)
		elif method == "round":
			self.grid = self.generateRound(72,72, 53)
		elif method == "halls":
			self.grid = self.generateHalls(72,72, 16,16, 10)
		elif method == "fastH":
			self.grid = self.generateFastH(72,72, 16,16, 12)
		else:
			self.grid = [[]]

	def __str__(self):
		output = ""
		for row in self.grid:
			for blk in row:
				output = output+str(blk)
			output = output+"\n"
		return output


	def generateBasic(self,w,h,x0,y0,s):
		"""
		generates a grid of square rooms separated by various kinds of walls
		w = the width of the dungeon in rooms
		h = the height of the dungeon in rooms
		x0, y0 = the starting room coordinates
		s = the width of the rooms in blocks (counting one wall)
		"""
		bigGrid = []
		for y in range(0,h):
			row = []
			for x in range(0,w):
				row.append(SquareRoom())
			bigGrid.append(row)
		self.dig(x0,y0,bigGrid, d=w/2+h/2-1)

		fineGrid = []
		for y in range(0,s*h):
			row = []
			for x in range(0,s*w):
				row.append(Stone())
			row.append(Stone())
			fineGrid.append(row)
		row = []
		for x in range(0,s*w+1):
			row.append(Stone())
		fineGrid.append(row)
		for ry in range(0,h):
			for rx in range(0,w):
				if bigGrid[ry][rx].floor == "open":
					for dy in range(1,s):
						for dx in range(1,s):
							fineGrid[s*ry+dy][s*rx+dx] = Floor()

				if bigGrid[ry][rx].left == "door":	# finish the walls
					fineGrid[s*ry+rng.randint(1,s-1)][s*rx] = Door()
				elif bigGrid[ry][rx].left == "open":
					for dy in range(1,s):
						fineGrid[s*ry+dy][s*rx] = Floor()
				elif bigGrid[ry][rx].left == "glass":
					for dy in range(1,s):
						fineGrid[s*ry+dy][s*rx] = Glass()
				if bigGrid[ry][rx].top == "door":
					fineGrid[s*ry][s*rx+rng.randint(1,s-1)] = Door()
				elif bigGrid[ry][rx].top == "open":
					for dx in range(1,s):
						fineGrid[s*ry][s*rx+dx] = Floor()
				elif bigGrid[ry][rx].top == "glass":
					for dx in range(1,s):
						fineGrid[s*ry][s*rx+dx] = Glass()
		return fineGrid


	def generatePanel(self, w,h):
		"""
		generates a series of rotating panels to form an adjustable labyrinth
		w = the width of the dungeon in blocks
		h = the height of the dungeon in blocks
		"""
		grid = []
		for y in range(0,h+1):
			row = []
			for x in range(0,w+1):
				row.append(Floor())
			grid.append(row)

		rx1 = w*3/8	# the coordinates of the central room
		rx2 = w*5/8
		ry1 = h*3/8
		ry2 = h*5/8

		for x in range(2,w-1,4):	# the nodes of the first round of panels
			for y in range(2,h-1,4):
				if (x < rx1 or x >= rx2 or y < ry1 or y >= ry2):
					self.erectPanel(x,y,grid)

		for x in range(4,w-1,4):
			for y in range(4,h-1,4):
				if (x < rx1 or x >= rx2 or y < ry1 or y >= ry2):
					self.erectPanel(x,y,grid)

		for x in range(0,w+1):
			grid[0][x] = Metal()
			grid[w][x] = Metal()
		for y in range(0,h+1):
			grid[y][0] = Metal()
			grid[y][h] = Metal()

		return grid


	def generateRound(self, w, h, p):
		"""
		generates a dungeon with no discernable structure (and lots of lava)
		w = the width of the dungeon in blocks
		h = the height of the dungeon in blocks
		p = a scalar proportional to the number of walls
		"""
		grid = []
		for y in range(0,h+1):
			row = []
			for x in range(0,w+1):
				row.append(Floor())
			grid.append(row)
		for x in range(0,w+1):
			grid[0][x] = Obsidian()
			grid[w][x] = Obsidian()
		for y in range(0,h+1):
			grid[y][0] = Obsidian()
			grid[y][h] = Obsidian()
		grid[h/2][w/2] = Obsidian()	# places some initial seeds
		grid[h/4][w/4] = Obsidian()
		grid[3*h/4][w/4] = Obsidian()
		grid[3*h/4][3*w/4] = Obsidian()
		grid[h/4][3*w/4] = Obsidian()

		costs = [	[0.5, 1.0, 0.5],
					[1.0, 0.0, 1.0],
					[0.5, 1.0, 0.5]]	# determines how the walls grow
		dy = [-1, 0, 1]
		dx = [-1, 0, 1]
		for i in range(p):
			for y in range(1,h):
				for x in range(1,w):
					if not grid[y][x].collides:	# for all floor blocsk
						z = 0
						for i in range(len(dy)):
							for j in range(len(dx)):
								if grid[y+dy[i]][x+dx[j]].collides:
									z = z+costs[dy[i]-1][dx[j]-1]
						if rng.random() < (0.01+z)*(6.01-z)/200.0:
							grid[y][x] = Obsidian()

		for i in range(2):
			self.flowLava(w/2, h/2, grid, 2*(w+h))	# creates lava rivers

		return grid


	def generateHalls(self, w, h, rw, rh, n):
		"""
		generates a complex dungeon of rectangular rooms and halls
		w = the approximate width of the dungeon
		h = the approximate height of the dungeon
		rw, rh = the maximum dimensions of the rooms
		n = the number of main hub rooms
		"""
		print "generating rooms..."
		rooms = []
		for i in range(0, 30*(w/rw + h/rh)):
			newRoom = RectRoom(rng.randint(1,rw),rng.randint(1,rh),rng.randint(1,rw),rng.randint(1,rh))
			if newRoom.w <= 2 or newRoom.h <= 2:	# discard tiny rooms
				continue
			for other in rooms:
				if other == newRoom:	# discard identical rooms
					continue
			rooms.append(newRoom)

		print "expanding dungeon..."
		thereAreIntersections = True	# spaces out the rooms
		while thereAreIntersections:
			thereAreIntersections = False
			for i in range(0,len(rooms)):
				for j in range(0,i):
					room1 = rooms[i]
					room2 = rooms[j]
					if room1.intersect(room2) != None:
						thereAreIntersections = True
						room1.push(room2)	# rooms that intersect will move away from each other
						room2.push(room1)
			for room in rooms:
				room.move()
		for room in rooms:
			room.round()
		
		print "selecting hubs..."
		hubs = []	# discards all but the biggest rooms
		for i in range(n):
			if len(rooms) > 0:
				maxSize = 0
				biggestRoom = 0
				for ndx, room in enumerate(rooms):
					if room.w*room.h > maxSize:
						maxSize = room.w*room.h
						biggestRoom = ndx
				hubs.append(rooms.pop(biggestRoom))

		print "buidling array..."
		minX = hubs[0].x	# finds boundaries for the dungeon
		minY = hubs[0].y
		maxX = 0
		maxY = 0
		for room in hubs:
			if room.x < minX:
				minX = room.x
			if room.y < minY:
				minY = room.y
			if room.x+room.w > maxX:
				maxX = room.x+room.w
			if room.y+room.h > maxY:
				maxY = room.y+room.h
		grid = []
		for y in range(minY, maxY+1):
			row = []
			for x in range(minX, maxX+1):
				row.append(Stone())
			grid.append(row)
		for room in hubs:	# creates the dungeon
			for dx in range(1, room.w):
				for dy in range(1, room.h):
					grid[room.y-minY+dy][room.x-minX+dx] = Floor()

		print "finding hallways..."
		for i in range(0,len(hubs)):
			j = (i+1)%len(hubs)	# A* searches a hallway between each pair of rooms
			room1 = hubs[i]
			room2 = hubs[j]
			dest = (int(room2.x+room2.w/2-minX), int(room2.y+room2.h/2-minY))
			strt = (int(room1.x+room1.w/2-minX), int(room1.y+room1.h/2-minY))
			openQ = [Node(strt[0], strt[1], dest[0], dest[1], None, 0)]
			closQ = []
			while len(openQ) > 0:
				p = openQ.pop()	# take the point with the lowest f (openQ is already sorted)
				adj = []
				if p.x-1 > 0:
					adj.append(Node(p.x-1, p.y, dest[0], dest[1], p, 1+grid[p.y][p.x-1].collides))
				if p.y-1 > 0:
					adj.append(Node(p.x, p.y-1, dest[0], dest[1], p, 1+grid[p.y-1][p.x].collides))
				if p.x+1 < len(grid[p.y])-1:
					adj.append(Node(p.x+1, p.y, dest[0], dest[1], p, 1+grid[p.y][p.x+1].collides))
				if p.y+1 < len(grid)-1:
					adj.append(Node(p.x, p.y+1, dest[0], dest[1], p, 1+grid[p.y+1][p.x].collides))
				for nxt in adj:
					found = False
					if nxt.h == 0:	# if we have reached our destination
						self.clearHall(nxt, grid)
						found = True
						break;
					promising = True	# whether it should be added to the queue
					for p2 in openQ:
						if nxt < p2:
							promising = False	# skip it if there is another node that is objectively better already on either queue
					for p2 in closQ:
						if nxt < p2:
							promising = False
					if promising:
						k = 0
						while k < len(openQ) and openQ[k].f > nxt.f:	# add it to the queue, sorted from longest to shortest f
							k = k+1
						openQ.insert(k, nxt)
				if found:
					break;
				closQ.append(p)

		print "diversifying dungeon..."
		for room in rooms:	# adds in some of the smaller rooms
			if self.accessible(room, grid, minX, minY):	# only the ones that intersect a hallway
				for dx in range(1, room.w):
					for dy in range(1, room.h):
						grid[room.y-minY+dy][room.x-minX+dx] = Floor()
		return grid


	def generateFastH(self, w, h, rw, rh, n):
		"""
		generates a simpler dungeon of rectangular rooms and halls
		w = the approximate width of the dungeon
		h = the approximate height of the dungeon
		rw, rh = the maximum dimensions of the rooms
		n = the number of main hub rooms
		"""
		rooms = []
		for i in range(0, 30*(w/rw + h/rh)):
			newRoom = RectRoom(rng.randint(1,rw),rng.randint(1,rh),rng.randint(1,rw),rng.randint(1,rh))
			if newRoom.w <= 2 or newRoom.h <= 2:	# discard tiny rooms
				continue
			for other in rooms:
				if other == newRoom:	# discard identical rooms
					continue
			rooms.append(newRoom)

		thereAreIntersections = True	# spaces out the rooms
		while thereAreIntersections:
			thereAreIntersections = False
			for i in range(0,len(rooms)):
				for j in range(0,i):
					room1 = rooms[i]
					room2 = rooms[j]
					if room1.intersect(room2) != None:
						thereAreIntersections = True
						room1.push(room2)	# rooms that intersect will move away from each other
						room2.push(room1)
			for room in rooms:
				room.move()
		for room in rooms:
			room.round()
		
		hubs = []	# discards all but the biggest rooms
		for i in range(n):
			if len(rooms) > 0:
				maxSize = 0
				biggestRoom = 0
				for ndx, room in enumerate(rooms):
					if room.w*room.h > maxSize:
						maxSize = room.w*room.h
						biggestRoom = ndx
				hubs.append(rooms.pop(biggestRoom))

		minX = hubs[0].x	# finds boundaries for the dungeon
		minY = hubs[0].y
		maxX = 0
		maxY = 0
		for room in hubs:
			if room.x < minX:
				minX = room.x
			if room.y < minY:
				minY = room.y
			if room.x+room.w > maxX:
				maxX = room.x+room.w
			if room.y+room.h > maxY:
				maxY = room.y+room.h
		grid = []
		for y in range(minY, maxY+1):
			row = []
			for x in range(minX, maxX+1):
				row.append(Stone())
			grid.append(row)
		for room in hubs:	# creates the dungeon
			for dx in range(1, room.w):
				for dy in range(1, room.h):
					grid[room.y+dy-minY][room.x+dx-minX] = Floor()

		pointList = []
		for room in hubs:
			pointList.append([room.x+room.w/2-minX, room.y+room.h/2-minY])
		tri = Delaunay(np.array(pointList))

		lines = csr_matrix((len(hubs),len(hubs)), dtype=int)	# fills a csr_matrix with the lines defined by the triangles
		for triangle in tri.simplices:							# for each triangle
			for pair in [(0,1),(1,2),(2,0)]:					# for each side
				i = min(triangle[pair[0]], triangle[pair[1]])
				j = max(triangle[pair[0]], triangle[pair[1]])
				if lines[i,j] == 0:							# save it with a weight equal to its length
					lines[i,j] = math.hypot(pointList[i][0]-pointList[j][0], pointList[i][1]-pointList[j][1])
		lines = minimum_spanning_tree(lines)

		done = np.zeros((len(hubs),len(hubs)))
		for j in range(len(hubs)):
			for i in range(j):
				if lines[i,j] != 0 or rng.random() < 0.1:
					self.makeLHall(hubs[i], hubs[j], grid, minX, minY)

		for room in rooms:	# adds in some of the smaller rooms
			if self.accessible(room, grid, minX, minY):	# only the ones that intersect a hallway
				for dx in range(1, room.w):
					for dy in range(1, room.h):
						grid[room.y+dy-minY][room.x+dx-minX] = Floor()
		return grid


	def makeLHall(self, room1, room2, grid, minX, minY):
		x1 = room1.x+room1.w/2-minX
		y1 = room1.y+room1.h/2-minY
		x2 = room2.x+room2.w/2-minX
		y2 = room2.y+room2.h/2-minY
		for x in range(x1, x2, int(math.copysign(1,x2-x1))):
			if grid[y1][x].collides:
				grid[y1][x] = Floor()
		for y in range(y1, y2, int(math.copysign(1,y2-y1))):
			if grid[y][x2].collides:
				grid[y][x2] = Floor()


	def accessible(self, room, grid, minX, minY):
		if room.y-minY < 0 or room.x-minX < 0 or room.y+room.h-minY >= len(grid)-1 or room.x+room.w-minX >= len(grid[0])-1:
			return False
		for dx in range(0, room.w+1):
			for dy in range(0, room.h+1):
				if not grid[room.y-minY+dy][room.x-minX+dx].collides:	# only the ones that intersect a hallway
					return True
		return False


	def clearHall(self, p, grid):	# creates a hallway given an end node
		if grid[p.y][p.x].collides:
			grid[p.y][p.x] = Floor()
		if p.parent != None:
			self.clearHall(p.parent, grid)


	def flowLava(self, x, y, grid, n):
		if n <= 0:
			return
		if x < 0 or y < 0 or y >= len(grid) or x >= len(grid[y]):
			return
		grid[y][x] = Lava()

		dys = range(-4,5)
		dxs = range(-4,5)
		costs = [[inverse(dx**2+dy**2) for dx in dxs] for dy in dys]	# determines how the river flows
		adj = []
		totZ = 0
		for p in [(0,-1),(0,1),(-1,0),(1,0)]:	# for each adjacent tile
			z = 0.0	# count how much lava is near it
			for i in range(len(dys)):	# for each tile adjacent to the adjacent one
				for j in range(len(dxs)):
					try:
						if grid[y+p[1]+dys[i]][x+p[0]+dxs[j]].isLava():
							z = z+costs[i][j]
					except IndexError:
						pass
			z = math.exp(-8*z)
			adj.append((p,z))
			totZ = totZ+z
		r = rng.random()
		for p,z in adj:
			if r < z/totZ:
				self.flowLava(x+p[0], y+p[1], grid, n-1)
				return
			else:
				r = r-z/totZ
		print "JOWEEE"


	def erectPanel(self,x,y,grid):
		r = rng.random()	# r determines the material
		if rng.random() < 0.5:	# horizontal
			for dx in [-1, 0, 1]:
				if r < 0.5:
					grid[y][x+dx] = Metal()
				elif r < 0.8:
					grid[y][x+dx] = Glass()
				elif r < 0.9:
					grid[y][x+dx] = OneWayGlass(1)
				else:
					grid[y][x+dx] = OneWayGlass(3)
			grid[y][x+2] = Metal()
			grid[y][x-2] = Metal()
		else:	# vertical
			for dy in [-1, 0, 1]:
				if r < 0.5:
					grid[y+dy][x] = Metal()
				elif r < 0.8:
					grid[y+dy][x] = Glass()
				elif r < 0.9:
					grid[y+dy][x] = OneWayGlass(0)
				else:
					grid[y+dy][x] = OneWayGlass(2)
			grid[y+2][x] = Metal()
			grid[y-2][x] = Metal()


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


def inverse(x):	# a little function i wrote mostly to get around arithmetic erros
	if x == 0:
		return 5
	else:
		return 1/float(x)


if __name__ == "__main__":
	import doctest
	doctest.testmod()
	for method in ["basic","panel","round","fastH"]:
		test = Dungeon(method)
		print test
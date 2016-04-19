import math
import random as rng
import numpy as np
from scipy.spatial import Delaunay
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

from terrainUtils import *



def generate(w,h,method):
	"""
	generates a dungeon (nested list of blocks) using the given method
	returns the dungeon as a nested list and a list of tuples representing the save points
	w, h = the dimensions of the desired dungeon
	method = a string representing the method I should use
	returns [nested list, int tuple list]
	"""
	if method == "panel":
		return generatePanel(w,h)
	elif method == "piece":
		return generatePiece(w,h, w*h/8)
	elif method == "maze1":
		return generateMazes(w,h, 12, 300, 3, False)
	elif method == "cells":
		return generateCells(w,h, 3, 4, 0.33, 3)
	elif method == "RBFSM":
		return generateRBFSM(w,h)
	elif method == "whole":
		return generateWhole(w/2,h/2)
	else:
		raise TypeError(method+" is not a real thing.")


def generatePanel(w,h):
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

	for x in range(2,w-1,2):
		for y in range(2+2*(x/2%2),h-1,4):	# certain tiles must be metal
			if (x < rx1 or x >= rx2 or y < ry1 or y >= ry2):	# skips the middle area
				grid[y][x] = Metal()

	for x in range(2,w-1,4):	# the nodes of the first round of panels
		for y in range(2,h-1,4):
			if not (x==2 and y==2) and not (x==2 and y==h-2) and not (x==w-2 and y==2) and not (x==w-2 and y==h-2):	#skips the corners
				if (x < rx1 or x >= rx2 or y < ry1 or y >= ry2):	# also skips the middle area
					erectPanel(x,y,grid)

	for x in range(4,w-1,4):
		for y in range(4,h-1,4):
			if (x < rx1 or x >= rx2 or y < ry1 or y >= ry2):
				erectPanel(x,y,grid)

	for x in range(0,w+1):
		grid[0][x] = Metal()
		grid[w][x] = Metal()
	for y in range(0,h+1):
		grid[y][0] = Metal()
		grid[y][h] = Metal()

	return [grid, [(w/2,h/2)]]


def generateRBFSM(w,h):
	"""
	A true labyrinth, it produces a maze of twisty corridors and dead ends
	"""
	grid = []
	for y in range(0,h+1):
		row = []
		for x in range(0,w+1):
			if x <= 0 or x >= w or y <= 0 or y >= h or rng.random() < 0.9:
				row.append(Metal())
			else:
				row.append(Glass())
		grid.append(row)

	randomQueueFlood(w/2+1,h/2+1,grid)

	for x in range(w*3/8, w*5/8):
		for y in range(h*3/8, h*5/8):
			grid[y][x] = Floor()

	return [grid, [(w/2,h/2)]]


def generatePiece(w, h, n):
	"""
	constructs a piecemeal dungeon by using preset features
	w, h = the dimensions of the dungeon
	n = the approximate number of features to generate (actual number will be somewhat less)
	"""
	grid = []
	for y in range(h+1):
		row = []
		for x in range(w+1):
			row.append(Brick())
		grid.append(row)
	for y in range(h/2-2, h/2+3):
		for x in range(w/2-2, w/2+3):
			grid[y][x] = Floor()

	corridoring = False	# whether we just made a corridor. If not, we are free to put rooms wherever we want
	for i in range(n):
		if not corridoring:
			drc = None
			while drc == None:
				wall = (rng.randint(1,w-1), rng.randint(1,h-1))	# pick a random wall
				drc = findWall(wall,grid)
			r = rng.random()
		else:
			wall = (wall[0]+(l)*drc[0], wall[1]+(l)*drc[1])
			while wall[0] > 0 and wall[0] < w and wall[1] > 0 and wall[1] < h and not grid[wall[1]][wall[0]].collides:
				wall = (wall[0]+drc[0], wall[1]+drc[1])
			r = (rng.random()+1)/2
		if r < 0.3:
			l = rng.randint(3,9)
			success = makeCorridor(*wall+(drc, l, grid))	# and try to put something on it
		elif r < 0.4:
			l = rng.randint(3,8)
			success = makeSquigglyCorridor(*wall+(drc, rng.choice([-1,1]), l, grid))
		elif r < 0.8:
			success = makeRoom(*wall+(drc, rng.randint(4,10), rng.randint(4,10), grid))
		elif r < 0.85:
			success = makeFancyRoom(*wall+(drc, 2*rng.randint(2,4), grid))
		elif r < 0.9:
			success = makeColumnRoom(*wall+(drc, 1+2*rng.randint(1,4), 1+2*rng.randint(1,4), grid))
		else:
			success = makeCircleRoom(*wall+(drc, rng.uniform(2,5), grid))
		corridoring = success and r < 0.4
		if success:
			grid[wall[1]][wall[0]] = Door()

	for x in rng.sample(range(1,w), w-1):
		for y in rng.sample(range(1,h), h-1):	# places doors where appropriate
			if grid[y][x].collides:
				adjWall = [(grid[y+p[1]][x+p[0]].collides, x+p[0], y+p[1]) for p in [(0,1),(0,-1),(1,0),(-1,0)]]
				if adjWall[0][0] and adjWall[1][0] and not adjWall[2][0] and not adjWall[3][0] and dist(adjWall[2][1:3],adjWall[3][1:3],grid) >= 50:
					grid[y][x] = Door()
				if adjWall[2][0] and adjWall[3][0] and not adjWall[0][0] and not adjWall[1][0] and dist(adjWall[0][1:3],adjWall[1][1:3],grid) >= 50:
					grid[y][x] = Door()

	x = 1
	while x < w:	# fill in all dead ends
		y = 1
		while y < h:
			if grid[y][x].passable():
				adjWalls = 0
				for p in [(0,1),(0,-1),(1,0),(-1,0)]:
					if not grid[y+p[1]][x+p[0]].passable():
						adjWalls = adjWalls+1
				if adjWalls >= 3:			# if this is a dead end
					grid[y][x] = Brick()	# fill it in
					x = 0					# start over
					y = 0
			y = y+1
		x = x+1

	placeTreasure(0.007, grid)
	return [grid, [(w/2,h/2)]]


def generateMazes(w, h, s, n, doors, mazeAlg):
	"""
	generates a dungeon comprised of rooms and mazes
	w, h = the dimensions of the dungeon
	s = the maximum room size
	n = the approximate number of rooms (actual number will be somewhat less)
	doors = a number that makes more unnecessary doors
	mazeAlg = True for random breadth-first-search, False for random depth-first-search
	"""
	sr = (s-1)/2	# gets the odd "root" of s
	wr = w/2
	hr = h/2

	grid = []
	for y in range(h+1):
		row = []
		for x in range(w+1):
			row.append(Stone())
		grid.append(row)
	for y in range(h/2-3, h/2+4):
		for x in range(w/2-3, w/2+4):
			grid[y][x] = Floor()
			grid[y][x].region = 0

	regionN = 1	# helps keep track of which tiles are connected to others
	for i in range(n):
		rw = 1+2*rng.randint(1,sr)
		rh = 1+2*rng.randint(1,sr)	# generate a bunch of random rooms
		x0 = 1+2*rng.randint(0,wr-(rw-1)/2)
		y0 = 1+2*rng.randint(0,hr-(rh-1)/2)
		if isClear(x0, y0, x0+rw-1, y0+rh-1, grid):
			for x in range(x0,x0+rw):
				for y in range(y0,y0+rh):
					grid[y][x] = Floor()
					grid[y][x].region = regionN
			regionN = regionN+1

	for x in rng.sample(range(1,w,2),w/2):
		for y in rng.sample(range(1,h,2),h/2):
			if grid[y][x].collides:
				if mazeAlg:
					randomQueueFlood(x,y,grid, regionN)
				else:
					randomStackFlood(x,y,grid, regionN)
				regionN = regionN+1

	regions = range(regionN)	# keeps track of which regions have united (the goal is all of them)
	while regions != [regions[0]]*regionN:	# while there are separate regions
		importantWalls = []
		for x in range(1,w):
			for y in range(1,h):
				if x%2 == 1 or y%2 == 1:
					if grid[y][x].collides:
						if not grid[y+1][x].collides and not grid[y-1][x].collides and (regions[grid[y+1][x].region]!=regions[grid[y-1][x].region]):
							importantWalls.append((x, y, regions[grid[y+1][x].region], regions[grid[y-1][x].region]))
						if not grid[y][x+1].collides and not grid[y][x-1].collides and (regions[grid[y][x+1].region]!=regions[grid[y][x-1].region]):
							importantWalls.append((x, y, regions[grid[y][x+1].region], regions[grid[y][x-1].region]))
		for iterationVariable in range(doors):
			if len(importantWalls) > 0:
				x,y,r1,r2 = rng.choice(importantWalls)
				grid[y][x] = Door()
				for i in range(regionN):	# knock out a door and unite the two regions
					if regions[i] == r1:
						regions[i] = r2

	x = 1
	while x < w:	# fill in all dead ends
		y = 1
		while y < h:
			if not grid[y][x].collides:
				adjWalls = 0
				for p in [(0,1),(0,-1),(1,0),(-1,0)]:
					if not grid[y+p[1]][x+p[0]].passable():
						adjWalls = adjWalls+1
				if adjWalls >= 3:			# if this is a dead end
					grid[y][x] = Stone()	# fill it in
					x = 0					# start over
					y = 0
			y = y+1
		x = x+1

	placeTreasure(0.005, grid)
	return [grid, [(w/2,h/2)]]


def generateCells(w, h, deathLim, birthLim, prob, n):
	"""
	generates a round map based on cellular automata
	w, h = the dimensions of the dungeon
	deathLim, birthLim = the limits that command the cellular automation process
	prob = the initial probability of stone
	n = the number of steps
	"""
	grid = []
	for y in range(0,h+1):
		row = [Obsidian()]
		for x in range(1,w):
			if rng.random() < prob:
				row.append(Obsidian())
			else:
				row.append(Floor())
		row.append(Obsidian())
		grid.append(row)
	for x in range(0,w+1):
		grid[0][x] = Obsidian()
		grid[w][x] = Obsidian()

	for i in range(n):
		newGrid = []
		for y in range(0,h+1):		# manually deep-copying because copy.deepcopy creates a nested list that will break pygame.Surface later on.
			row = []
			for x in range(0,w+1):
				row.append(grid[y][x])
			newGrid.append(row)
		for x in range(1,w):
			for y in range(1,h):
				adj = 0
				for dx in [-1,0,1]:
					for dy in [-1,0,1]:
						if grid[y+dy][x+dx].collides:
							adj = adj+1
				if adj > birthLim:
					newGrid[y][x] = Obsidian()
				if adj < deathLim:
					newGrid[y][x] = Floor()
		grid = newGrid

	regions = []
	maxRSize = 0
	maxRIndx = -1
	for x in range(1,w):
		for y in range(1,h):
			if not grid[y][x].collides and not hasattr(grid[y][x], 'region'):	# if this in an unmarked floor
				region = findRegion(x,y,grid)									# get all blocks connected to it
				if len(region) > maxRSize:
					maxRSize = len(region)
					maxRIndx = len(regions)
				regions.append(region)											# and save them as a region
	for i in range(0,len(regions)):
		if i != maxRIndx:
			for x,y in regions[i]:
				grid[y][x] = Obsidian()		# fill in all but the biggest region

	for d in [-1,1]:
		flowLava(w/2, h/2, grid, 2*(w+h), d)	# creates lava rivers

	for x in range(1,w):
		for y in range(1,h):
			if not grid[y][x].collides and rng.random() < .015:	# and some tiny lava lakes
				splatterLava(x,y,grid)

	placeTreasure(0.005, grid)
	return [grid, [(w/2,h/2)]]


def generateWhole(w, h):
	"""
	Generates a huge dungeon incorporating the piece, panel, cellular, and maze algorithms
	w, h = the dimensions of each section
	"""
	sectors = [generate(w,h,method)[0] for method in ["piece","RBFSM","cells","maze1"]]

	grid = []
	for y in range(h+1):
		grid.append(sectors[1][y] + sectors[0][y])	# starts by globbing together the four dungeons
	for y in range(h+1):
		grid.append(sectors[2][y] + sectors[3][y])

	savePoints = [(3*w/2+1,h/2)]
	grid[h/2][3*w/2] = NPC()

	for d in range(1,min(w,h)):			# does a dijkstra-type-thing to find the nearest open block in piece
		done = False
		for t in range(0,d+1):
			x0 = w+2+(t)
			y0 = 1+(d-t)
			if grid[y0][x0].passable():
				for x in range(w,x0):	# and digs a hallway to it
					grid[1][x] = Floor()
				for y in range(1,y0):
					grid[y][x0] = Floor()
				done = True
				break
		if done:
			break
	savePoints.append((w,1))

	for d in range(1,min(w,h)):			# same deal as before but for quadrant 3
		done = False
		for t in range(0,d+1):
			x0 = 1+(t)
			y0 = h+2+(d-t)
			if grid[y0][x0].passable():
				for y in range(h,y0):
					grid[y][1] = Floor()
				for x in range(1,x0):
					grid[y0][x] = Floor()
				done = True
				break
		if done:
			break
	savePoints.append((1,h+1))

	for d in range(1,min(w,h)):			# now do it for the last two sectors!
		done = False
		for t in range(0,d+1):
			x0 = w-(t)
			y0 = 2*h-(d-t)
			if grid[y0][x0].passable():
				for x in range(w,x0,-1):
					grid[2*h][x] = Floor()
				for y in range(2*h,y0,-1):
					grid[y][x0] = Floor()
				done = True
				break
		if done:
			break
	for d in range(1,min(w,h)):
		done = False
		for t in range(0,d+1):
			x0 = w+1+(t)
			y0 = 2*h-(d-t)
			if grid[y0][x0].passable():
				for x in range(w+1,x0, 1):
					grid[2*h][x] = Floor()
				for y in range(2*h,y0,-1):
					grid[y][x0] = Floor()
				done = True
				break
		if done:
			break
	savePoints.append((w+1,2*h))
	# randomizes some things
	if rng.random() < 0.5:	# flip about the x-axis
		grid.reverse()
		for i, tp in enumerate(savePoints):
			savePoints[i] = (tp[0], 2*h+1-tp[1])
	if rng.random() < 0.5:	# flip about the y-axis
		for row in grid:
			row.reverse()
		for i, tp in enumerate(savePoints):
			savePoints[i] = (2*w+1-tp[0], tp[1])
	if rng.random() < 0.5:	# flip about the line y=x
		newGrid = []
		for y in range(0, 2*h+2):
			newRow = []
			for x in range(0, 2*w+2):
				newRow.append(grid[x][y])
			newGrid.append(newRow)
		grid = newGrid
		for i, tp in enumerate(savePoints):
			savePoints[i] = (tp[1], tp[0])

	return [grid, savePoints]
	

def dist(dest, strt, grid):	# A* search
	openQ = [Node(strt[0], strt[1], dest[0], dest[1], None, 0)]
	closQ = []
	while len(openQ) > 0:
		p = openQ.pop()	# take the point with the lowest f (openQ is already sorted)
		adj = []
		if p.x-1 > 0 and grid[p.y][p.x-1].passable():
			adj.append(Node(p.x-1, p.y, dest[0], dest[1], p, 1))
		if p.y-1 > 0 and grid[p.y-1][p.x].passable():
			adj.append(Node(p.x, p.y-1, dest[0], dest[1], p, 1))
		if p.x+1 < len(grid[p.y])-1 and grid[p.y][p.x+1].passable():
			adj.append(Node(p.x+1, p.y, dest[0], dest[1], p, 1))
		if p.y+1 < len(grid)-1 and grid[p.y+1][p.x].passable():
			adj.append(Node(p.x, p.y+1, dest[0], dest[1], p, 1))
		for nxt in adj:
			if nxt.h == 0:	# if we have reached our destination
				return nxt.g
			promising = True	# whether it should be added to the queue
			for p2 in openQ:
				if nxt < p2:
					promising = False	# skip it if there is another node that is objectively better already on either queue
					break
			for p2 in closQ:
				if nxt < p2:
					promising = False
					break
			if promising:
				k = len(openQ)-1
				while k >= 0 and openQ[k].f < nxt.f:	# add it to the queue, sorted from longest to shortest f
					k = k-1
				openQ.insert(k+1, nxt)
		closQ.append(p)
	return -1	# return -1 if there is no path


def findRegion(xs, ys, grid):	# gets all the open blocks connected to this one
	region = []
	queue = [(xs,ys)]
	while len(queue) > 0:
		x0, y0 = queue.pop()
		grid[y0][x0].region = True
		region.append((x0,y0))

		for x,y in [(x0+p[0], y0+p[1]) for p in [(0,1),(0,-1),(1,0),(-1,0)]]:
			if not grid[y][x].collides and not hasattr(grid[y][x],"region"):
				queue.append((x,y))
	return region


def randomQueueFlood(x0, y0, grid, region=0):	# random recursive flood algorithm that creates mazes
	queue = [(x0,y0,x0,y0)]	# the list of nodes that need to be filled as well as where they will be filled from
	while len(queue) > 0:
		x,y,xp,yp = rng.choice(queue)
		queue.remove((x,y,xp,yp))
		if not grid[y][x].collides:	# someone beat us to it
			continue

		grid[yp][xp] = Floor()	# draw the path
		grid[yp][xp].region = region
		grid[y][x] = Floor()
		grid[y][x].region = region

		for p in [(0,1),(0,-1),(1,0),(-1,0)]:
			if y+2*p[1] >= 0 and y+2*p[1] < len(grid) and x+2*p[0] >= 0 and x+2*p[0] < len(grid[y]):
				if grid[y+2*p[1]][x+2*p[0]].collides:
					queue.append((x+2*p[0], y+2*p[1], x+p[0], y+p[1]))


def randomStackFlood(x, y, grid, region=0):	# random recursive flood algorithm that creates mazes
	grid[y][x] = Floor()
	grid[y][x].region = region
	for p in rng.sample([(0,1),(0,-1),(1,0),(-1,0)], 4):
		if y+2*p[1] >= 0 and y+2*p[1] < len(grid) and x+2*p[0] >= 0 and x+2*p[0] < len(grid[y]):
			if grid[y+2*p[1]][x+2*p[0]].collides:	# each segment is at least two long to give it that "a maze"-ing look (get it?)
				grid[y+p[1]][x+p[0]] = Floor()
				grid[y+p[1]][x+p[0]].region = region
				randomStackFlood(x+2*p[0], y+2*p[1], grid, region)


def findWall(coords, grid):	# find out if there is a wall here and return the direction as a tuple
	x,y = coords
	if not grid[y][x].collides:
		return None
	output = None
	for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:	# it must have exactly one neighbor that
		if not grid[y+dy][x+dx].collides:		# does not collide to count as a wall
			if output == None:
				output = (-dx, -dy)	# if you find the non-coliding neighbor, save it
			else:
				return None			# if you find two, it does not count
	return output


def isClear(x0, y0, x1, y1, grid):	# checks the grid to see if a given rectangle (inclusive) is clear of stuff
	for x in range(min(x0,x1)-1, max(x0,x1)+2):
		for y in range(min(y0,y1)-1, max(y0,y1)+2):
			if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[y]) or not grid[y][x].collides:
				return False
	return True


def makeCorridor(x0,y0,d,l,grid):
	"""
	builds a corridor given x0, y0, direction, length, and the grid to edit
	and returns whether it succeeded
	"""
	dx = d[0]*l + (d[0]==0)	# changes 0 and +-1 into 1 and +-l
	dy = d[1]*l + (d[1]==0)	# changes 0 and +-1 into 1 and +-l
	if not isClear(x0+d[0], y0+d[1], x0+d[0]*l, y0+d[1]*l, grid):
		return False
	for x in range(x0+d[0], x0+d[0]+dx, int(math.copysign(1,dx))):
		for y in range(y0+d[1], y0+d[1]+dy, int(math.copysign(1,dy))):
			grid[y][x] = Floor()
	return True


def makeSquigglyCorridor(x0,y0,d,a,l,grid):
	"""
	builds a squiggly corridor given x0, y0, direction, amplitude, length, and the grid to edit
	and returns whether it succeeded
	"""
	if d == (0,1):		# down
		if not isClear(x0,y0+1,x0+a,y0+l+1, grid):
			return False
		for dy in range(1, l+2):
			if (1+dy)%4 > 0:
				grid[y0+dy][x0] = Floor()
			if (3+dy)%4 > 0:
				grid[y0+dy][x0+a] = Floor()
	elif d == (0,-1):	# up
		if not isClear(x0,y0-1,x0+a,y0-l-1, grid):
			return False
		for dy in range(-l-1, 0):
			if (1-dy)%4 > 0:
				grid[y0+dy][x0] = Floor()
			if (3-dy)%4 > 0:
				grid[y0+dy][x0+a] = Floor()
	elif d == (1,0):	# right
		if not isClear(x0+1,y0,x0+l+1,y0+a, grid):
			return False
		for dx in range(1, l+2):
			if (1+dx)%4 > 0:
				grid[y0][x0+dx] = Floor()
			if (3+dx)%4 > 0:
				grid[y0+a][x0+dx] = Floor()
	elif d == (-1,0):	# left
		if not isClear(x0-1,y0,x0-l-1,y0+a, grid):
			return False
		for dx in range(-l-1, 0):
			if (1-dx)%4 > 0:
				grid[y0][x0+dx] = Floor()
			if (3-dx)%4 > 0:
				grid[y0+a][x0+dx] = Floor()
	return True


def makeRoom(x0,y0,d,w,h,grid):
	"""
	builds a rectangular room given x0, y0, direction, width, height, and the grid to edit
	and returns whether it succeeded
	"""
	x1 = x0 + d[0] - (d[0]==0)*rng.randint(0,w-1)
	y1 = y0 + d[1] - (d[1]==0)*rng.randint(0,h-1)
	x2 = x1 + (w-1)*int(math.copysign(1,d[0]))
	y2 = y1 + (h-1)*int(math.copysign(1,d[1]))
	if not isClear(x1,y1,x2,y2, grid):
		return False
	for x in range(min(x1,x2), max(x1,x2)+1):
		for y in range(min(y1,y2), max(y1,y2)+1):
			grid[y][x] = Floor()
	return True


def makeFancyRoom(x0,y0,d,s,grid):
	"""
	builds a fancy room given x0, y0, direction, side-length, and the grid to edit
	and returns whether it succeeded
	"""
	xc = x0 + d[0] + d[0]*s/2
	yc = y0 + d[1] + d[1]*s/2
	if not isClear(xc-s/2,yc-s/2,xc+s/2,yc+s/2, grid):
		return False
	for r in range(s/2,-1,-2):	# I had to use an old fasioned for-loop because range doesn't take floats
		for t in range(-r,r+1):
			grid[int(yc+r)][int(xc+t)] = Floor()	# creates rings
			grid[int(yc-r)][int(xc+t)] = Floor()
			grid[int(yc+t)][int(xc+r)] = Floor()
			grid[int(yc+t)][int(xc-r)] = Floor()
	for r in range(s/2-1,0,-2):
		grid[int(yc+r)][int(xc)] = Floor()			# creates passageways
		grid[int(yc-r)][int(xc)] = Floor()
		grid[int(yc)][int(xc+r)] = Floor()
		grid[int(yc)][int(xc-r)] = Floor()
	return True


def makeColumnRoom(x0,y0,d,w,h,grid):
	"""
	builds a column room given x0, y0, direction, width, height, and the grid to edit
	and returns whether it succeeded
	"""
	x1 = x0 + d[0] - (d[0]==0)*rng.randint(0,w-1)
	y1 = y0 + d[1] - (d[1]==0)*rng.randint(0,h-1)
	x2 = x1 + (w-1)*int(math.copysign(1,d[0]))
	y2 = y1 + (h-1)*int(math.copysign(1,d[1]))
	if not isClear(x1,y1,x2,y2, grid):
		return False
	for dx in range(0, abs(x1-x2)+1):
		for dy in range(0, abs(y1-y2)+1):
			if dx%2 == 0 or dy%2 == 0:
				grid[min(y1,y2)+dy][min(x1,x2)+dx] = Floor()
	return True


def makeCircleRoom(x0,y0,d,r,grid):
	"""
	builds a circular room given x0, y0, direction, radius, and the grid to edit
	and returns whether it succeeded
	"""
	xc = x0 + d[0] + d[0]*int(r)
	yc = y0 + d[1] + d[1]*int(r)
	if not isClear(xc-int(r),yc-int(r),xc+int(r),yc+int(r), grid):
		return False
	for x in range(-int(r), int(r)+1):
		for y in range(-int(r), int(r)+1):
			if math.hypot(x,y) <= r:
				grid[yc+y][xc+x] = Floor()
	return True


def accessible(room, grid, minX, minY):
	if room.y-minY < 0 or room.x-minX < 0 or room.y+room.h-minY >= len(grid)-1 or room.x+room.w-minX >= len(grid[0])-1:
		return False
	for dx in range(0, room.w+1):
		for dy in range(0, room.h+1):
			if not grid[room.y-minY+dy][room.x-minX+dx].collides:	# only the ones that intersect a hallway
				return True
	return False


def flowLava(x, y, grid, n, d):	# make a lava river!
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
		z = 0.0								# count how much lava is near it
		for i in range(len(dys)):
			for j in range(len(dxs)):
				try:
					if type(grid[y+p[1]+dys[i]][x+p[0]+dxs[j]]) == Lava:
						z = z+costs[i][j]
				except IndexError:
					pass
		z = math.exp(-z)
		if p[0] == d or p[1] == -d:	# it likes to flow in a certain direction
			z = 2*z
		adj.append((p,z))
		totZ = totZ+z
	r = rng.random()
	for p,z in adj:
		if r < z/totZ:
			flowLava(x+p[0], y+p[1], grid, n-1, d)
			return
		else:
			r = r-z/totZ
	print "JOWEEE"


def erectPanel(x,y,grid):
	r = rng.random()	# r determines the material
	if rng.random() < 0.5:	# horizontal
		for dx in [-1, 0, 1]:
			if r < 0.65:
				grid[y][x+dx] = Metal()
			elif r < 0.85:
				grid[y][x+dx] = Glass()	# there is a small chance there will be nothing there
			elif r < 0.9 and dx == 0:
				grid[y][x+dx] = Loot(5)
	else:	# vertical
		for dy in [-1, 0, 1]:
			if r < 0.65:
				grid[y+dy][x] = Metal()
			elif r < 0.85:
				grid[y+dy][x] = Glass()
			elif r < 0.9 and dy == 0:
				grid[y+dy][x] = Loot(5)


def splatterLava(x, y, grid):	# makes a little lava puddle
	P = [
	[0.20, 0.40, 0.20],
	[0.40, 1.00, 0.40],
	[0.20, 0.40, 0.20]]

	for i,dx in enumerate([-1,0,1]):
		for j,dy in enumerate([-1,0,1]):
			if not grid[y+dy][x+dx].collides:
				if rng.random() < P[i][j]:
					grid[y+dy][x+dx] = Lava()


def inverse(x):	# a little function i wrote mostly to get around arithmetic erros
	if x == 0:
		return 5
	else:
		return 1/math.sqrt(x)


def placeTreasure(dens, grid):	# scatters treasure blocks across the map
	for y in range(1,len(grid)-1):
		for x in range(1,len(grid[y])-1):
			if grid[y][x].collides:
				continue

			neighbors = [grid[y+p[1]][x+p[0]] for p in [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]]
			wallCount = 1

			wallsHit = 0
			for i in range(len(neighbors)):
				if neighbors[i].collides:
					wallCount = wallCount + 1
				if neighbors[i].passable() and neighbors[(i+1)%len(neighbors)].collides:	# this may only be triggered once
					if wallsHit >= 1:
						wallsHit = 2														# multiple triggerings means this chest may block off a room
						break
					else:
						wallsHit = 1

			if wallsHit < 2 and rng.random() < dens*(wallCount):
				grid[y][x] = Loot(5)
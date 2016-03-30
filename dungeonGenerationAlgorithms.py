import math
import random as rng
from copy import deepcopy
import numpy as np
from scipy.spatial import Delaunay
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

from terrainUtils import *



def generateBasic(w,h,x0,y0,s):
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
	dig(x0,y0,bigGrid, d=w/2+h/2-1)

	fineGrid = []
	for y in range(0,s*h):
		row = []
		for x in range(0,s*w):
			row.append(Brick())
		row.append(Brick())
		fineGrid.append(row)
	row = []
	for x in range(0,s*w+1):
		row.append(Brick())
	fineGrid.append(row)
	for ry in range(0,h):
		for rx in range(0,w):
			if bigGrid[ry][rx].floor == "open":
				for dy in range(1,s):
					for dx in range(1,s):
						fineGrid[s*ry+dy][s*rx+dx] = Floor()

			if bigGrid[ry][rx].left == "door":	# finish the walls
				fineGrid[s*ry+rng.randint(1,s-1)][s*rx] = Door(False)
			elif bigGrid[ry][rx].left == "open":
				for dy in range(1,s):
					fineGrid[s*ry+dy][s*rx] = Floor()
			elif bigGrid[ry][rx].left == "glass":
				for dy in range(1,s):
					fineGrid[s*ry+dy][s*rx] = Glass()
			if bigGrid[ry][rx].top == "door":
				fineGrid[s*ry][s*rx+rng.randint(1,s-1)] = Door(False)
			elif bigGrid[ry][rx].top == "open":
				for dx in range(1,s):
					fineGrid[s*ry][s*rx+dx] = Floor()
			elif bigGrid[ry][rx].top == "glass":
				for dx in range(1,s):
					fineGrid[s*ry][s*rx+dx] = Glass()

	for x in range(1,s*w):
		for y in range(1,s*h):
			if not fineGrid[y][x].collides and rng.random() < .004:	# and some tiny lava lakes
				splatterLava(x,y,fineGrid)
	return fineGrid


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

	return grid


def generateRound(w, h, p):
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

	for d in [-1, 1]:
		flowLava(w/2, h/2, grid, 2*(w+h), d)	# creates lava rivers

	for x in range(1,w):
		for y in range(1,h):
			if not grid[y][x].collides and rng.random() < .01:	# and some tiny lava lakes
				splatterLava(x,y,grid)
	return grid


def generateHalls(w, h, rw, rh, n):
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
			row.append(Brick())
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
					clearHall(nxt, grid)
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
		if accessible(room, grid, minX, minY):	# only the ones that intersect a hallway
			for dx in range(1, room.w):
				for dy in range(1, room.h):
					grid[room.y-minY+dy][room.x-minX+dx] = Floor()
	return grid


def generateFastH(w, h, rw, rh, n):
	"""
	generates a simpler dungeon of rectangular rooms and halls
	w = the approximate width of the dungeon
	h = the approximate height of the dungeon
	rw, rh = the maximum dimensions of the rooms
	n = the number of main hub rooms
	"""
	rooms = []
	for i in range(0, 15*(w/rw + h/rh)):
		newRoom = RectRoom(rng.randint(1,rw),rng.randint(1,rh),rng.randint(1,rw),rng.randint(1,rh))
		if newRoom.w <= 2 or newRoom.h <= 2:	# discard tiny rooms
			continue
		for other in rooms:
			if other == newRoom:	# discard identical rooms
				continue
		rooms.append(newRoom)

	for i in range(10):	# this iteration might make rooms more evenly spaced; I don't actually know if it does anything.
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
			row.append(Brick())
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
				makeLHall(hubs[i], hubs[j], grid, minX, minY)

	for room in rooms:	# adds in some of the smaller rooms
		if accessible(room, grid, minX, minY):	# only the ones that intersect a hallway
			for dx in range(1, room.w):
				for dy in range(1, room.h):
					grid[room.y+dy-minY][room.x+dx-minX] = Floor()
	return grid


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
			row.append(Stone())
		grid.append(row)
	for y in range(h/2-3, h/2+3):
		for x in range(w/2-3, w/2+3):
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

	for x in range(1,w):
		for y in range(1,h):
			if type(grid[y][x]).__name__ == "Door":
				grid[y][x].open()
			if grid[y][x].collides:
				adjWall = [grid[y+p[1]][x+p[0]].collides for p in [(0,1),(0,-1),(1,0),(-1,0)]]
				if (adjWall[0] and adjWall[1] and not adjWall[2] and not adjWall[3]) or (not adjWall[0] and not adjWall[1] and adjWall[2] and adjWall[3]):
					if rng.random() < 0.1:
						grid[y][x] = Door(True)

	x = 1
	while x < w:	# fill in all dead ends
		y = 1
		while y < h:
			if not grid[y][x].collides:
				adjWalls = 0
				for p in [(0,1),(0,-1),(1,0),(-1,0)]:
					if grid[y+p[1]][x+p[0]].collides:
						adjWalls = adjWalls+1
				if adjWalls >= 3:			# if this is a dead end
					grid[y][x] = Stone()	# fill it in
					x = 0					# start over
					y = 0
			y = y+1
		x = x+1
	return grid


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

	regionN = 0	# helps keep track of which tiles are connected to others
	for i in range(n):
		rw = 1+2*rng.randint(1,sr)
		rh = 1+2*rng.randint(1,sr)
		x0 = 1+2*rng.randint(0,wr-(rw-1)/2)
		y0 = 1+2*rng.randint(0,hr-(rh-1)/2)
		if isClear(x0, y0, x0+rw-1, y0+rh-1, grid):
			room = []
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
				grid[y][x] = Door(True)
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
					if grid[y+p[1]][x+p[0]].collides:
						adjWalls = adjWalls+1
				if adjWalls >= 3:			# if this is a dead end
					grid[y][x] = Stone()	# fill it in
					x = 0					# start over
					y = 0
			y = y+1
		x = x+1
	return grid


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
		newGrid = deepcopy(grid)
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

	for d in [-1,1]:
		flowLava(w/2, h/2, grid, 2*(w+h), d)	# creates lava rivers

	for x in range(1,w):
		for y in range(1,h):
			if not grid[y][x].collides and rng.random() < .01:	# and some tiny lava lakes
				splatterLava(x,y,grid)
	return grid


def generateRWalk(w, h, n, t):
	"""
	generates a random dungeon using a drunkard's walk algorithm
	w, h = the dimensions of the dungeon
	n = the number of drunkards
	t = the number of steps each drunkard takes
	"""
	grid = []
	for y in range(h+1):
		row = []
		for x in range(w+1):
			row.append(Bedrock())
		grid.append(row)

	for i in range(n):
		x = (w+1)/2
		y = (w+1)/2
		for step in range(t):
			if grid[y][x].collides:
				grid[y][x] = Floor()
			adj = [(0,1),(0,-1),(1,0),(-1,0)]
			for p in adj:
				if y+p[1] <= 0 or y+p[1] >= h or x+p[0] <= 0 or x+p[0] >= h:
					adj.remove(p)
			p = rng.choice(adj)
			x = x+p[0]
			y = y+p[1]
	return grid


def generateIWalk(w, h, n, t):
	"""
	generates a random dungeon using a modified drunkard's walk algorithm that avoids the edges
	w, h = the dimensions of the dungeon
	n = the number of drunkards
	t = the number of steps each drunkard takes
	"""
	grid = []
	for y in range(h+1):
		row = []
		for x in range(w+1):
			row.append(Bedrock())
		grid.append(row)

	for i in range(n):
		x = (w+1)/2
		y = (w+1)/2
		for step in range(t):
			if grid[y][x].collides:
				grid[y][x] = Floor()
			adj = [(0,-1),(0,1),(-1,0),(1,0)]
			probs = []
			for p in adj:	# for each adjacent tile
				try:
					probs.append(harmonicSum([x+p[0], y+p[1], w-x-p[0], h-y-p[1]]))
				except ZeroDivisionError:
					probs.append(0)
			r = rng.random()
			for i in range(len(probs)):
				if r < probs[i]/sum(probs):
					x = x+adj[i][0]
					y = y+adj[i][1]
					break
				else:
					r = r-probs[i]/sum(probs)
	return grid


def generateRooms(w, h, n, c):
	"""
	generates a dungeon composed entirely of rectangular rooms connected by doorways
	w, h = the dimensions of the dungeon
	n = the approximate number of walls to draw
	c = a number from 0-1 that makes rooms more interconnected
	"""
	grid = []
	for y in range(0,h+1):
		row = []
		for x in range(0,w+1):
			block = Floor()
			block.region = 0
			row.append(block)
		grid.append(row)
	for x in range(0,w+1):
		grid[0][x] = Brick()
		grid[h][x] = Brick()
		#grid[h/2][x] = Brick()
	for y in range(0,h+1):
		grid[y][0] = Brick()
		grid[y][w] = Brick()
		#grid[y][w/2] = Brick()

	regionN = 1
	for i in range(n):
		x0 = rng.randint(2,w-2)
		y0 = rng.randint(2,h-2)
		okay = True
		x1 = x0
		while not grid[y0][x1].collides:	# checks the horizontal room we have to work with
			x1 = x1+1
		x2 = x0-1
		while not grid[y0][x2].collides:
			x2 = x2-1
		y1 = y0
		while not grid[y1][x0].collides:	# checks the vertical room we have to work with
			y1 = y1+1
		y2 = y0-1
		while not grid[y2][x0].collides:
			y2 = y2-1
		if x1-x2 < y1-y2 or (x1-x2 == y1-y2 and rng.random() < 0.5):	# draws the shorter wall here
			for x in range(x2,x1):
				grid[y0][x] = Brick()			# draw a horizontal line
				for y in range(y0,y1):			# and update regions accordingly
					grid[y][x].region = regionN
		else:
			for y in range(y2,y1):
				grid[y][x0] = Brick()			# draw a vertical line
				for x in range(x0,x1):			# and update regions accordingly
					grid[y][x].region = regionN
		regionN += 1

	regions = range(regionN)	# keeps track of which regions have united (the goal is all of them)
	importantWalls = [0]
	while len(importantWalls) > 0:	# while there are rooms that need to be connected
		importantWalls = []
		for x in range(1,w):
			for y in range(1,h):
				if grid[y][x].collides:
					if not grid[y+1][x].collides and not grid[y-1][x].collides and (regions[grid[y+1][x].region]!=regions[grid[y-1][x].region]):
						importantWalls.append((x, y, regions[grid[y+1][x].region], regions[grid[y-1][x].region]))
					if not grid[y][x+1].collides and not grid[y][x-1].collides and (regions[grid[y][x+1].region]!=regions[grid[y][x-1].region]):
						importantWalls.append((x, y, regions[grid[y][x+1].region], regions[grid[y][x-1].region]))
		if rng.random() < c:	# there is a chance to knock out more doors than necessary
			doors = 2
		else:
			doors = 1
		for iterationVariable in range(doors):
			if len(importantWalls) > 0:
				x,y,r1,r2 = rng.choice(importantWalls)
				grid[y][x] = Door()
				grid[y][x].region = r2
				for i in range(regionN):	# knock out a door and unite the two regions
					if regions[i] == r1:
						regions[i] = r2
	return grid


def harmonicSum(lst):
	sum = 0
	for x in lst:
		sum = sum + 1.0/x
	return 1.0/sum


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


def makeTreasure(x0,y0,grid):
	grid[y0][x0] = Loot()


def makeLHall(room1, room2, grid, minX, minY):
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


def accessible(room, grid, minX, minY):
	if room.y-minY < 0 or room.x-minX < 0 or room.y+room.h-minY >= len(grid)-1 or room.x+room.w-minX >= len(grid[0])-1:
		return False
	for dx in range(0, room.w+1):
		for dy in range(0, room.h+1):
			if not grid[room.y-minY+dy][room.x-minX+dx].collides:	# only the ones that intersect a hallway
				return True
	return False


def clearHall(p, grid):	# creates a hallway given an end node
	if grid[p.y][p.x].collides:
		grid[p.y][p.x] = Floor()
	if p.parent != None:
		clearHall(p.parent, grid)


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
		if p[0] == d or p[1] == d:
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
			if r < 0.5:
				grid[y][x+dx] = Metal()
			elif r < 0.75:
				grid[y][x+dx] = Glass()
			elif r < 0.85:
				grid[y][x+dx] = OneWayGlass(1)
			elif r < 0.95:
				grid[y][x+dx] = OneWayGlass(3)	# there is a small chance there will be nothing there
	else:	# vertical
		for dy in [-1, 0, 1]:
			if r < 0.5:
				grid[y+dy][x] = Metal()
			elif r < 0.75:
				grid[y+dy][x] = Glass()
			elif r < 0.85:
				grid[y+dy][x] = OneWayGlass(0)
			elif r < 0.95:
				grid[y+dy][x] = OneWayGlass(2)


def dig(x,y, grid, d=7, bearing=-1):	# starts a tunnel here
	grid[y][x].clear()
	prob = (d/7.0)

	if bearing != 0 and x >= 1 and rng.random() < prob:		# left
		grid[y][x].randomizeLeft()
		dig(x-1, y, grid, d=d-1, bearing=2)
	if bearing != 1 and y >= 1 and rng.random() < prob:		# up
		grid[y][x].randomizeTop()
		dig(x, y-1, grid, d=d-1, bearing=3)
	if bearing != 2 and x < len(grid[0])-1 and rng.random() < prob:	# right
		grid[y][x+1].randomizeLeft()
		dig(x+1, y, grid, d=d-1, bearing=0)
	if bearing != 3 and y < len(grid)-1 and rng.random() < prob:	# down
		grid[y+1][x].randomizeTop()
		dig(x, y+1, grid, d=d-1, bearing=1)


def splatterLava(x, y, grid):	# makes a little lava puddle
	P = [
	[0.25, 0.50, 0.25],
	[0.50, 1.00, 0.50],
	[0.25, 0.50, 0.25]]

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
				if not neighbors[i].collides and neighbors[(i+1)%len(neighbors)].collides:	# this may only be triggered once
					if wallsHit >= 1:
						wallsHit = 2														# multiple triggerings means this chest may block off a room
						break
					else:
						wallsHit = 1

			if wallsHit < 2 and rng.random() < dens*(wallCount):
				grid[y][x] = Loot(5)
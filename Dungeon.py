import dungeonGenerationAlgorithms as dga
from terrainUtils import Null





class Dungeon(object):
	def __init__(self, w, h, method):
		if method == "basic":
			self.grid = dga.generateBasic(w/8,h/8,w/16,h/16,8)
			dga.placeTreasure(0.003, self.grid)
		elif method == "panel":
			self.grid = dga.generatePanel(w,h)
			dga.placeTreasure(0.006, self.grid)
		elif method == "round":
			self.grid = dga.generateRound(w,h, 53)
			dga.placeTreasure(0.007, self.grid)
		elif method == "halls":
			self.grid = dga.generateHalls(w,h, 16,16, 10)
			dga.placeTreasure(0.004, self.grid)
		elif method == "fastH":
			self.grid = dga.generateFastH(w,h, 16,16, 12)
			dga.placeTreasure(0.007, self.grid)
		elif method == "piece":
			self.grid = dga.generatePiece(w,h, w*h/10)
			dga.placeTreasure(0.007, self.grid)
		elif method == "maze1":
			self.grid = dga.generateMazes(w,h, 12, 300, 2, False)
			dga.placeTreasure(0.005, self.grid)
		elif method == "maze2":
			self.grid = dga.generateMazes(w,h, 12, 80, 3, True)
			dga.placeTreasure(0.005, self.grid)
		elif method == "cells":
			self.grid = dga.generateCells(w,h, 3, 4, 0.33, 3)
			dga.placeTreasure(0.004, self.grid)
		elif method == "Rwalk":
			self.grid = dga.generateRWalk(w,h, 8, 1000)
			dga.placeTreasure(0.007, self.grid)
		elif method == "Iwalk":
			self.grid = dga.generateIWalk(w,h, 4, 1000)
			dga.placeTreasure(0.007, self.grid)
		elif method == "rooms":
			self.grid = dga.generateRooms(w,h, 100, 0.5)
			dga.placeTreasure(0.002, self.grid)
		else:
			self.grid = [[]]

		self.nullBlock = Null()

		self.last_action = "You wake up near an underground river."


	def __str__(self):
		output = ""
		for row in self.grid:
			for blk in row:
				output = output+str(blk)
			output = output+"\n"
		return output


	def getBlock(self,x,y):
		if y >= 0 and y < len(self.grid) and x >= 0 and x < len(self.grid[y]):
			return self.grid[y][x]
		else:
			return self.nullBlock


	def countLoot(self):
		count = 0
		for y in range(0,len(self.grid)):
			for x in range(0,len(self.grid[y])):
				if type(self.grid[y][x]).__name__ == "Loot":
					count += 1
		return count


	def getLog(self):
		return self.last_action


	def getWidth(self):
		return len(self.grid[0])

	def getHeight(self):
		return len(self.grid)


if __name__ == "__main__":
	import doctest
	doctest.testmod()
	a = Dungeon(50,50,"fastH")
	print a.grid
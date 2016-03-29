import dungeonGenerationAlgorithms as dga
from terrainUtils import Block





class Dungeon(object):
	def __init__(self, w, h, method):
		if method == "basic":
			self.grid = dga.generateBasic(w/8,h/8,w/16,h/16,8)
		elif method == "panel":
			self.grid = dga.generatePanel(w,h)
		elif method == "round":
			self.grid = dga.generateRound(w,h, 53)
		elif method == "halls":
			self.grid = dga.generateHalls(w,h, 16,16, 10)
		elif method == "fastH":
			self.grid = dga.generateFastH(w,h, 16,16, 12)
		elif method == "piece":
			self.grid = dga.generatePiece(w,h, w*h/10)
		elif method == "maze1":
			self.grid = dga.generateMazes(w,h, 12, 500, 0.5, False)
		elif method == "maze2":
			self.grid = dga.generateMazes(w,h, 12, 50, 0.9, True)
		elif method == "cells":
			self.grid = dga.generateCells(w,h, 3, 4, 0.33, 3)
		elif method == "Rwalk":
			self.grid = dga.generateRWalk(w,h, 8, 1000)
		elif method == "Iwalk":
			self.grid = dga.generateIWalk(w,h, 4, 1000)
		elif method == "rooms":
			self.grid = dga.generateRooms(w,h, 100, 0.1)
		else:
			self.grid = [[]]

		dga.placeTreasure(0.006, self.grid)

		self.nullBlock = Block()

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


	def getLog(self):
		return self.last_action


	def getWidth(self):
		return len(self.grid[0])

	def getHeight(self):
		return len(self.grid)



if __name__ == "__main__":
	import doctest
	doctest.testmod()
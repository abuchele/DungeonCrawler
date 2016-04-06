import dungeonGenerationAlgorithms as dga
from terrainUtils import Null
import entities




class Dungeon(object):
	def __init__(self, w, h, method = "whole", player = entities.Player(0,0)):
		self.w = w
		self.h = h

		thing = dga.generate(w,h,method)
		self.grid = thing[0]

		self.nullBlock = Null()
		self.player = entities.Player(*thing[1])

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

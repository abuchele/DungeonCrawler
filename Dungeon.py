import dungeonGenerationAlgorithms as dga
from terrainUtils import Null
import entities




class Dungeon(object):
	def __init__(self, w, h, method = "whole", player = entities.Player("grid", 0,0), filename = None):
		self.w = w
		self.h = h

		thing = dga.generate(w,h,method)

		self.grid = thing[0]
		# startcoords = *thing[1][0] #doesnt work
		print thing[1][0]
		self.nullBlock = Null()
		self.player = entities.Player(self.grid, *thing[1][0])

		self.last_action = "You wake up near an underground river."

		self.last_save = 0
		self.savePoints = thing[1] + [(None,None)]


	def __str__(self):
		output = "{:03d} {:03d}\n".format(self.player.x,self.player.y)
		for row in self.grid:
			for blk in row:
				output = output+str(blk)
			output = output+"\n"
		return output


	def update(self):
		if self.player.x == self.savePoints[self.last_save][0] and self.player.y == self.savePoints[self.last_save][1]:
			print "Saving... (jk not rely)"
			self.last_save += 1


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
	a = Dungeon(50, 50, "fastH")
	print a.grid

import dungeonGenerationAlgorithms as dga
from terrainUtils import Null
import entities
import pickle
import random as rng




class Dungeon(object):
	def __init__(self, w, h, method="whole"):
		self.w = w
		self.h = h

		thing = dga.generate(w,h,method)

		self.grid = thing[0]

		self.nullBlock = Null()
		self.player = entities.Player(self.grid, *(thing[1][0]))

		self.last_action = "You wake up near an underground river."

		self.last_save = 0
		self.savePoints = thing[1] + [(None,None)]

		self.state = "R"	# R for running, P for paused, and D for dialogue
		self.monsterlist = [] #contains all the monster objects
		self.monstercoords = {} #contains key/value pair of (x,y) and list of monsters at that coordinate


	def __str__(self):
		output = ""
		for row in self.grid:
			for blk in row:
				output = output+str(blk)
			output = output+"\n"
		return output

	def generateMonsters(self, last_save, monsterNumber = 200):
		count = 0
		for y in range(0,self.h-1):
			for x in range(0,self.w-1):
				if not self.grid[y][x].collides() and count<monsterNumber and rng.random()<float(monsterNumber)/5000:
					if rng.randint(0,1) == 0:
						zombie = entities.Zombie(x,y,self.Player,self.grid)
						newlist = self.monstercoords.get((x,y),[])
						newlist.append(zombie)
						self.monstercoords[(x,y)] = newlist
						self.monsterlist.append[zombie]
						count +=1
					else:
						ghost = entities.Ghost(x,y,self.Player,self.grid)
						newlist = self.monstercoords.get((x,y),[])
						newlist.append(ghost)
						self.monstercoords[(x,y)] = newlist
						self.monsterlist.append[ghost]
						count +=1

	def update(self):
		if self.state == "R":	# it doesn't update if the game is paused
			if self.player.x == self.savePoints[self.last_save][0] and self.player.y == self.savePoints[self.last_save][1]:
				self.save("saves/last_save.dun")
				self.last_save += 1
				self.generateMonsters(self.last_save)

			if type(self.getBlock(self.player.x, self.player.y)).__name__ == "Lava":	# you can jump over one block of lava
				if self.getBlock(*self.player.facingCoordinates()).collides:			# if there is no block in front of you
					print self.player.effected("killed")
				else:
					self.player.x,self.player.y = self.player.facingCoordinates()		# also please try not to jump into more lava
					if type(self.getBlock(self.player.x, self.player.y)).__name__ == "Lava":
						print self.player.effected("killed")

			if rng.random() < 0.006:
				self.last_action = rng.choice(
					["You catch a waft of something rotting.",
					"A cold breeze blows through.",
					"You hear a faint, distant moan.",
					"A cold chill runs down your spine.",
					"A bit of moisture drips onto your shoulder.",
					"You think you hear screaming."])


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


	def interp_action(self, action):	# interprets an action (should be a string!)
		if len(action) <= 0:
			return
		elif action[0] == "$":
			if action[1] == "D":
				self.state = "D"
			else:
				raise TypeError("What the heck does %{} mean?!".format(action[1]))
		else:
			self.last_action = action


	def save(self, filename):
		file = open(filename, 'w')	# just pickles this dungeon to a file
		pickle.dump(self, file)
		file.close()


	def getLog(self):
		return self.last_action


	def pause(self):
		self.state = "P"


	def resume(self):
		self.state = "R"


	def getWidth(self):
		return len(self.grid[0])

	def getHeight(self):
		return len(self.grid)


def load(filename):
	file = open(filename, 'r')
	output = pickle.load(file)
	file.close()
	return output


if __name__ == "__main__":
	import doctest
	doctest.testmod()
	a = Dungeon(50,50,"fastH")
	print a.grid
	print 

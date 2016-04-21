import dungeonGenerationAlgorithms as dga
from terrainUtils import Null
import entities
import pickle
import random as rng
from dialogue.textutil import TextUtility
import pygame
import eventList




class Dungeon(object):
	def __init__(self, w, h, method="whole"):
		self.w = w
		self.h = h

		thing = dga.generate(w,h,method)

		self.grid = thing[0]

		self.nullBlock = Null()
		
		self.player = entities.Player(self.grid, *(thing[1][0]))
		self.player_name = "Ray"


		self.last_action = "You wake up near an underground river."
		self.current_convo = ""
		self.current_interactee = None

		self.last_save = 0
		self.savePoints = thing[1] + [(None,None)]

		self.state = "R"	# R for running, P for paused, and D for dialogue

		self.checklist = eventList.Checklist()

		# self.monsterlist = [] #contains all the monster objects
		self.monstercoords = {} #contains key/value pair of (x,y) and list of monsters at those coordinates
		self.player = entities.Player(self.grid, self.monstercoords, *(thing[1][0]))
		self.generateMonsters()

		self.activemonsterlist = []
		self.activemonstercoords = {}
		self.text = None	# the class that will help to organize the dialogue
		self.lnInd = 0		# the line number in this conversation
		self.lines = None	# the list of surfaces that represent this conversation


	def __str__(self):
		output = ""
		for row in self.grid:
			for blk in row:
				output = output+str(blk)
			output = output+"\n"
		return output

	def generateMonsters(self, monsterNumber = 1000):
		"""
		Fills the world with monsters of various kinds
		"""
		mr_E = entities.MrE(self.grid, self.savePoints[0][0], self.savePoints[0][1]-1, self.player, self.checklist)
		
		self.monstercoords[(mr_E.x, mr_E.y)] = [mr_E]	# the first npc
		# self.monsterlist.append(mr_E)

		count = 0
		for y in rng.sample(range(0,self.h-1), self.h-1):		# spawns a bunch of other numbers on non-colliding spaces
			for x in rng.sample(range(0,self.w-1), self.w-1):
				if not self.grid[y][x].collides:
					if rng.randint(0,1) == 0:
						zombie = entities.Zombie(x,y,self.player,self.grid, self.monstercoords)
						newlist = self.monstercoords.get((x,y),[])
						newlist.append(zombie)
						self.monstercoords[(x,y)] = newlist
						# self.monsterlist.append(zombie)
						count +=1
					else:
						ghost = entities.Ghost(x,y,self.player,self.grid, self.monstercoords)
						newlist = self.monstercoords.get((x,y),[])
						newlist.append(ghost)
						self.monstercoords[(x,y)] = newlist
						# self.monsterlist.append(ghost)
						count +=1

				if count >= monsterNumber:
					return

	def update(self):
		if self.state == "R":	# it doesn't update if the game is paused
			self.player.update()

			if self.player.x == self.savePoints[self.last_save][0] and self.player.y == self.savePoints[self.last_save][1]:
				self.save("saves/last_save.dun")
				self.last_save += 1

			if type(self.getBlock(self.player.x, self.player.y)).__name__ == "Lava":	# you can jump over one block of lava
				if self.getBlock(*self.player.facingCoordinates()).collides:			# if there is no block in front of you
					print self.player.effected("killed")
				else:
					self.player.x,self.player.y = self.player.facingCoordinates()		# also please try not to jump into more lava
					if type(self.getBlock(self.player.x, self.player.y)).__name__ == "Lava":
						print self.player.effected("killed")

			for dy in range(-8,9):
				for dx in range(-8,9):
					monsters = self.monstercoords.get((self.player.x+dx,self.player.y+dy),[])
					for monster in monsters:
						monster.update()

			for dy in range(-8,9):
				for dx in range(-8,9):
					monsters = self.monstercoords.pop((self.player.x+dx,self.player.y+dy),[]) #this is a list of monsters
					# self.activemonsterlist += monsters
					for monster in monsters:
						# self.activemonsterlist.append(monster)
						try:
							newlist = self.monstercoords[(monster.x,monster.y)]
						except KeyError:
							newlist = []
						newlist.append(monster)
						self.monstercoords[(monster.x,monster.y)] = newlist
						# if not monster.seen:
						# 	newlist1 = self.activemonstercoords[(monster.x,monster.y)]
						# 	newlist1.remove(monster)
						# 	self.activemonstercoords[(monster.x,monster.y)] = newlist1
							 #this changes monster.x and monster.y but monstercoords still has the original position as key.
							
						# print "Aggro:", monster.aggro
						# print "Seen:", monster.seen


			if rng.random() < 0.003:
				self.last_action = rng.choice(
					["You catch a waft of something rotting.",
					"A cold breeze blows through.",
					"You hear a faint, distant moan.",
					"A cold chill runs down your spine.",
					"A bit of moisture drips onto your shoulder.",
					"You think you hear screaming.",
					"Something moves in the corner of your eye.",
					"You think you hear footsteps."])


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
		elif action[0] == "$": #Special Interaction
			if action[1] == "D": #Dialogue.  i.e. $D0001
				self.start_dialogue(int(action[2:]))
			else:
				raise TypeError("What the heck does ${} mean?".format(action[1]))
		else:
			self.last_action = action


	def start_dialogue(self, conv_id):	# enters dialogue mode
		self.state = "D"
		self.current_convo = conv_id
		self.text = TextUtility()
		self.lines = self.text.text_wrapper(conv_id, (20,20,660,150), (0,0,0))
		self.lnInd = 0
		pygame.key.set_repeat()


	def advance_dialogue(self):	# moves to the next line
		self.lnInd += 1
		if self.lnInd >= len(self.lines):	# if the dialogue is over
			self.do_post_dialogue_action()
			self.state = "R"				# resume the game
			self.text = None				# clear these variables
<<<<<<< HEAD
			self.lines = None				#because they take up too much space
			self.current_convo = None
			pygame.key.set_repeat(150,150)
=======
			self.lines = None				# because they take up too much space
			pygame.key.set_repeat(200,200)
>>>>>>> 137b883e58648e06bc52041c78c7a1bae7a33965

	def do_post_dialogue_action(self):
		if isinstance(self.current_interactee, entities.NPC):
			self.current_interactee.post_dialogue_action(self.current_convo)

	def currentParagraph(self):				# the surface that represents the current bit of dialogue
		return self.lines[self.lnInd]


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

import dungeonGenerationAlgorithms as dga
from terrainUtils import Null
import entities
import pickle
import random as rng
from dialogue.textutil import TextUtility
import pygame
import eventList
import copy
import time
import math



class Dungeon(object):
	def __init__(self, w, h, method="whole"):
		self.w = w
		self.h = h

		self.terminal = True

		thing = dga.generate(w,h,method)

		self.grid = thing[0]

		self.nullBlock = Null()

		self.monstercoords = {} #contains key/value pair of (x,y) and monster at those coordinates

		self.last_action = "You wake up near an underground river."
		self.current_convo = ""
		self.current_interactee = None

		self.last_save = 0
		self.savePoints = thing[1] + [(None,None)]

		self.state = "R"	# R for running, P for paused, and D for dialogue

		self.checklist = eventList.Checklist()

		self.player = entities.Player(self, self.monstercoords, *(thing[1][0]))

		self.generateMonsters()

		self.text = None	# the class that will help to organize the dialogue
		self.lnInd = 0		# the line number in this conversation
		self.lines = None	# the list of surfaces that represent this conversation
		self.current_interactee = self.mr_E
		self.save("saves/last_save.dun")
		self.interp_action(self.mr_E.interact(self.player)) 

	def __str__(self):
		output = ""
		for row in self.grid:
			for blk in row:
				output = output+str(blk)
			output = output+"\n"
		return output

	def generateMonsters(self, monsterFrequencies =[0.05,0.05,0.05,0.05,1.00]):
		"""
		Fills the world with monsters of various kinds
		"""
		mr_E = entities.MrE(self, self.savePoints[0][0], self.savePoints[0][1]-1, self.player, self.checklist)
		self.mr_E = mr_E

		kx, ky = self.savePoints[1]
		if abs(kx-self.w) > abs(ky-self.h):
			kx = int(math.floor(kx + math.copysign(0.5, self.mr_E.x-kx)))	# calculates where to place kerberoge
			ky = int(math.floor(ky + math.copysign(2.5, self.mr_E.y-ky)))
		else:
			kx = int(math.floor(kx + math.copysign(2.5, self.mr_E.x-kx)))	# it depends on the direction
			ky = int(math.floor(ky + math.copysign(0.5, self.mr_E.y-ky)))
		kerberoge = entities.Kerberoge(self, kx, ky, self.player, self.checklist)

		self.monstercoords[(mr_E.x, mr_E.y)] = mr_E	# the first npc
		self.monstercoords[(kx, ky)] = kerberoge    # the second npc

		for y in range(0,self.h-1):		# spawns a bunch of other numbers on non-colliding spaces
			for x in range(0,self.w-1):
				block = self.grid[y][x]
				if not block.collides and not self.monstercoords.has_key((x,y)) and rng.random() < monsterFrequencies[block.biome]:
					if block.biome == 0:
						newMonst = entities.Zombie(x,y,self.player,self,self.monstercoords)
					elif block.biome == 1:
						if rng.random() < 0.4:
							newMonst = entities.Zombie(x,y,self.player,self,self.monstercoords)
						else:
							newMonst = entities.Ghost(x,y,self.player,self, self.monstercoords)
					elif block.biome == 2:
						if rng.random() < 0.4:
							newMonst = entities.Zombie(x,y,self.player,self,self.monstercoords)
						elif rng.random() < 0.1:
							newMonst = entities.Ghost(x,y,self.player,self, self.monstercoords)
						else:
							newMonst = entities.Demon(x,y,self.player,self, self.monstercoords)
					elif block.biome == 3:
						newMonst = entities.Skeleton(x,y,self.player,self, self.monstercoords)
					elif block.biome == 4:
						newMonst = entities.Nike(self, x,y, self.player, self.checklist)
					else:
						continue

					self.monstercoords[(x,y)] = newMonst

	def update(self):
		if self.state == "R":	# it doesn't update if the game is paused
			self.player.update()

			if self.player.x == self.savePoints[self.last_save][0] and self.player.y == self.savePoints[self.last_save][1]:
				self.save("saves/last_save.dun")
				self.last_save += 1

			if type(self.getBlock(self.player.x, self.player.y)).__name__ == "Lava":	# you can jump over one block of lava
				if not self.player.canMoveTo(*self.player.facingCoordinates()):			# if there is no block in front of you
					self.player.effected("submerged in lava")
				else:
					self.player.x,self.player.y = self.player.facingCoordinates()		# also please try not to jump into more lava
					if type(self.getBlock(self.player.x, self.player.y)).__name__ == "Lava":
						self.player.effected("submerged in lava")
			elif self.monstercoords.has_key((self.player.x,self.player.y)):				# you can jump over one jumpable monster
				if self.player.canMoveTo(*self.player.facingCoordinates()):				# if there is no block in front of you
					self.player.x,self.player.y = self.player.facingCoordinates()

			if self.player.health <= 0:
				self.state = "K"

			old_monstercoords = copy.copy(self.monstercoords) 
			for dy in range(-8,9):			# move all the monsters
				for dx in range(-8,9):
					monster = old_monstercoords.pop((self.player.x+dx,self.player.y+dy), None) #this makes sure each monster only updates once
					if monster != None:
						self.monstercoords.pop((monster.x,monster.y))
						monster.update()
						if monster.health > 0:
							self.monstercoords[(monster.x,monster.y)] = monster
						else:
							self.checklist.state["killcount"] = self.checklist.state.get("killcount",0) + 1


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
		self.text = TextUtility(self.player)
		self.lines = self.text.text_wrapper(conv_id, (20,20,660,150), (0,0,0))
		self.lnInd = 0
		#pygame.key.set_repeat()


	def advance_dialogue(self):	# moves to the next line
		self.lnInd += 1
		if self.lnInd >= len(self.lines):	# if the dialogue is over
			self.text = None				# clear these variables
			self.lines = None				#because they take up too much space
			self.state = "R"				# resume the game
			self.do_post_dialogue_action()
			self.current_convo = None
			#pygame.key.set_repeat(100,100)

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

	def menu_pause(self):
		self.state = "M"

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

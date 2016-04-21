#The eventlist is the checklist that determines and saves all the data on what interactions
#The player has done, i.e. talking to people, some stat tracking, etc.
class Checklist():
	def __init__(self):
		#universal things
		world = 0 #Current world completed/bosses defeated
		killcount = 0 #monsters killed
		self.state = {"player_Named":False,"tutorial_Dialogue002_Finished":False,"tutorial_Dialogue004_Finished":False,
		"tutorial_Dialogue005_Finished":False,"tutorial_Dialogue006_Finished":False,"tutorial_quest":False,"tutorial_quest_confirm":False,
		"kerberoge_start":False, "kerberoge_defeated":False}
		#World1
		# self.player_Named = False #Has the player entered a name? 
		# self.tutorial_Dialogue002_Finished = False # If finished dialogue 2.  Can't leave room otherwise
		# self.tutorial_Dialogue004_Finished = False # If finished dialogue 4.
		# self.tutorial_Dialogue005_Finished = False # If finished dialogue 5.
		# self.tutorial_Dialogue006_Finished = False # If finished dialogue 6.  If true, player can go outside
		# self.tutorial_quest = False #Kill 3 monsters
		# self.tutorial_quest_confirm = False #Talk to Mr.E after finishing the quest.
		# self.kerberoge_start = False
		# self.kerberoge_defeated = False
		"""So basically, the player starts off the game talking to Mr.E, dialogue 0001.  Then after the
		player talks to Mr.E and enters their name, Player_named is set to true.  This allows Mr.E to 
		go to the next dialogue, 0002.  If the player attempts to leave before finishing dialogue 4, 
		Mr.E will play Dialogue 0003.  After Dialogue 0004 is finished, the player can go outside
		to kill monsters.  Once it is true, it triggers Dialogue 005.  Once dialogue 5 is finished, 
		The player can trigger dialogue 6.  Once that is finished, the player can go outside.  
		Once the player kills enough monsters, the quest will be finished.  If this is true, then 
		Mr. E will have dialogue 0007, and then mark the quest confirm as true."""  
	
	def eventcomplete(eventname): #eventname is string
		self.state[eventname] = True
	def checkeventstate(eventname):
		return self.state[eventname]
#The eventlist is the checklist that determines and saves all the data on what interactions
#The player has done, i.e. talking to people, some stat tracking, etc.
class Checklist():
	def __init__(self):
		#universal things
		
		
		self.state = {
		"world":0, #Current world completed/bosses defeated
		"killcount":0, #monsters killed
		
		#World1
		"player_Named":False, #Has the player entered a name? 
		"tutorial_Dialogue002_Finished":False,
		"tutorial_Dialogue004_Finished":False,
		"tutorial_Dialogue005_Finished":False,
		"tutorial_Dialogue006_Finished":False, #If true, player can go outside
		"tutorial_quest_finished":False, #Kill 3 Monsters (possibly flash a quest complete)
		"tutorial_quest_confirmed_finished":False, #Talk to Mr. E
		"kerberoge_start":False, "kerberoge_defeated":False
		#World2
		
		}
		
		"""So basically, the player starts off the game talking to Mr.E, dialogue 0001.  Then after the
		player talks to Mr.E and enters their name, Player_named is set to true.  This allows Mr.E to 
		go to the next dialogue, 0002.  If the player attempts to leave before finishing dialogue 4, 
		Mr.E will play Dialogue 0003.  After Dialogue 0004 is finished, the player can go outside
		to kill monsters.  Once it is true, it triggers Dialogue 005.  Once dialogue 5 is finished, 
		The player can trigger dialogue 6.  Once that is finished, the player can go outside.  
		Once the player kills enough monsters, the quest will be finished.  If this is true, then 
		Mr. E will have dialogue 0007, and then mark the quest confirm as true."""  
	
	def eventcomplete(self, eventname): #eventname is string
		self.state[eventname] = True
	def checkeventstate(self, eventname):
		return self.state[eventname]
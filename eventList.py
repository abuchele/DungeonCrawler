#The eventlist is the checklist that determines and saves all the data on what interactions
#The player has done, i.e. talking to people, some stat tracking, etc.
class Checklist():
	def __init__(self):
		#universal things
		world = 0 #Current world completed/bosses defeated
		killcount = 0 #monsters killed

		#World1
<<<<<<< HEAD
		Player_Named = False #Has the player entered a name? 
		Tutorial_Dialogue002_Finished = False # If finished dialogue 2.  Can't leave room otherwise
		Tutorial_Dialogue004_Finished = False # If finished dialogue 4.
		Tutorial_Dialogue005_Finished = False # If finished dialogue 5.
		Tutorial_Dialogue006_Finished = False # If finished dialogue 6.  If true, player can go outside
		Tutorial_quest = False #Kill 3 monsters
		Tutorial_quest_confirm = False #Talk to Mr.E after finishing the quest.
		Kerberoge_start = False
		Kerberoge_defeated = False
		#So basically, the player starts off the game talking to Mr.E, dialogue 0001.  Then after the
		#player talks to Mr.E and enters their name, Player_named is set to true.  This allows Mr.E to 
		#go to the next dialogue, 0002.  If the player attempts to leave before finishing dialogue 4, 
		#Mr.E will play Dialogue 0003.  After Dialogue 0004 is finished, the player can go outside
		#to kill monsters.  Once it is true, it triggers Dialogue 005.  Once dialogue 5 is finished, 
		#The player can trigger dialogue 6.  Once that is finished, the player can go outside.  
		#Once the player kills enough monsters, the quest will be finished.  If this is true, then 
		#Mr. E will have dialogue 0007, and then mark the quest confirm as true.  
=======
		met_Mr_E = False		# the first dialogue
		tutorial_Dialogue_Finished = False #If they can leave the room.  If not, Mr. E plays id=0003
		tutorial_quest = False #Kill 3 monsters
		tutorial_quest_confirm = False #Talk to Mr.E after finishing the quest.
>>>>>>> 0ec5965132ffae78d92f61d504ee31fcc40d32af

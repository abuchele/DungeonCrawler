#The eventlist is the checklist that determines and saves all the data on what interactions
#The player has done, i.e. talking to people, some stat tracking, etc.
class checklist():
	def __init__(self):
		#universal things
		world = 0 #Current world completed

		#World1
		Tutorial_Dialogue_Finished = False #If they can leave the room.  If not, Mr. E plays id=0003

import pygame

class TextUtility(object):

	def __init__(self):

		if pygame.font.get_init() != True: #Initialize the font module.  
			pygame.font.init()

		self.myFont = pygame.font.SysFont("serif",24) #Default Font

		text = open("dialogue/conversation.txt", "r") #Import the Conversation File.  
		self.conversation = text.read()

		#Every Conversation has its own ID, tentatively from 0000 to 9999.
		#Every change in character speech ends with a $$.  
		#Every Conversation ends with "end_{convo_id}"

	
	def special_font(filename="", size=20): #Changes the font if the character uses a special font.
		if filename and size:				 
			self.myFont = pygame.font.Font(filename, size)

	def pull(self, convo_id): #Pulls a conversation by ID, returns a list of the lines by character
		"""
		Pulls a conversation by ID, returns a list of the lines by character
		>>> a = TextUtility()
		>>> a.pull(0)
		['Console: This is the text test conversation.', 'Player: What does it mean?', "Console: This shouldn't be used for anything but testing."]
		"""
		dialogue_list = []
		start = self.conversation.index("id="+str(convo_id)) + 7 #Finds start of dialogue
		end = self.conversation.index("end_"+str(convo_id)) - 1 #Finds end of dialogue
		convo = self.conversation[start:end]
		
		while len(convo) > 0:
			line = convo[1:convo.index("$$")]
			dialogue_list.append(line)
			convo = convo[convo.index("$$")+2:]

		return dialogue_list

	def text_wrapper(self, convo_id, rect, color):
		""" Returns a list of surfaces to be displayed in the box.  
			Requires a method that will draw it and progress the conversation game-side.
			Also requires a rect tuple parameter, the size of the text box, and
			a color tuple, the color of the text. 
		"""
		n = 4	# the number of lines per box 
		x, y, w, h = rect

		dialogue_list = self.pull(convo_id) #Get the list of dialogue lines
		chat_list = [] #The list of resulting dialogues from breaking up the dialogue to fit.  

		for line in dialogue_list: #breaks up the dialogues into lines.
			words = line.split()
			line_list = [] #The pictures of the lines of text

			curr_line = ""
			while len(words) > 0:
				next_word = words.pop(0)								# look at the next word
				if self.myFont.size(curr_line+" "+next_word)[0] > w:	# if this word would make the line too wide
					image = self.myFont.render(curr_line, True, color)	# take the line as it is
					line_list.append(image)
					curr_line = next_word
				else:													# otherwise
					curr_line = curr_line+" "+next_word					# keep adding to this line

			line_list.append(self.myFont.render(curr_line, True, color))	# at the end, add whatever is left over
			chat_list.append(line_list) #Nested list - first level is of dialogues, second level is of lines.

		#Now I assume that we can fit two lines of text in the rectangle.  So now I gotta surface these
		#and then subdivide each conversation into twos, so each list will be a dialogue or part for a
		#separate person.  I guess this is just a rearranging.  
		final_chat_list = []
		
		for characterLines in chat_list:
			textBlock = []
			for line in characterLines:					# for each line
				textBlock.append(line)					# add it to the block
				if len(textBlock) >= n:					# if the block is big enough
					final_chat_list.append(textBlock)	# set it aside
					textBlock = []						# and start making a new block
			final_chat_list.append(textBlock)

		return final_chat_list

		

if __name__ == '__main__':
	import doctest
	doctest.testmod()
	text = TextUtility()
	text.pull(0000)
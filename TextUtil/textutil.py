import pygame
from pygame import *

class textutil(object):

	def __init__(self):

		if pygame.font.get_init() != True: #Initialize the font module.  
			pygame.font.init()

		self.font = None #Default Font, to be decided later.

		text = open("conversation.txt", "r") #Import the Conversation File.  
		self.conversation = text.read()

		#Every Conversation has its own ID, tentatively from 0000 to 9999.
		#Every change in character speech ends with a $$.  
		#Every Conversation ends with "end_{convo_id}"

	
	def special_font(filename="default", size=20): #Changes the font if the character uses a special font.
		if filename and size:				 
			font = pygame.font.Font(filename, size)

	def pull(self, convo_id): #Pulls a conversation by ID, returns a list of the lines by character
		dialogue_list = []
		start = self.conversation.index("id="+str(convo_id)) + 7 #Finds start of dialogue
		end = self.conversation.index("end_"+str(convo_id)) - 1 #Finds end of dialogue
		convo = self.conversation[start:end]
		
		while len(convo) > 0:
			line = convo[0:convo.index("$$")]
			dialogue_list.append(line)
			convo = convo[convo.index("$$")+2:]

		return dialogue_list

	def text_wrapper(self, convo_id, rect, color): #Returns a list of surfaces to be displayed in the box.  
						#Requires a method that will draw it and progress the conversation game-side.
						#Also requires a rect object parameter.  
		lines_per_box = 3
		y = rect.top
		fontHeight = font.size("Tg")[1]
		line_spacing = 2

		dialogue_list = self.pull(convo_id) #Get the list of dialogue lines
		chat_list = [] #The list of resulting dialogues from breaking up the dialogue to fit.  

		for i in range(len(dialogue_list)): #breaks up the dialogues into lines.  
			dialogue = dialogue_list[i]
			line_list = [] #The literal lines for each dialogue text.  
			while len(dialogue) > 0:
				length = 1
				while font.size(dialogue[:length]) > rect.width and i < len(dialogue):
					length+=1 #Gets the maximum width of the line.
				image = font.render(dialogue[:length], aa, color) #renders the line
				line_list.append(image)
				
				dialogue = dialogue[length:] #Remove added text.
			chat_list.append(line_list) #Nested list - first is of dialogues, second is of lines.

#Now I assume that we can fit two lines of text in the rectangle.  So now I gotta surface these
#and then subdivide each conversation into twos, so each list will be a dialogue or part for a
#separate person.  I guess this is just a rearranging.  
		final_chat_list = []
		
		for i in range(len(chat_list))
			queue = [] #cutting down from back, needs to be reversed. 
			temp_list = chat_list[i]
			x = len(temp_list)
			while x > 0:
				if x%2 == 1:
					queue.append(temp_list[x-1]) #Last Element
					temp_list = temp_list[:x-1]
				queue.append(temp_list[x-3:x-1])
				temp_list = temp_list[:x-3]
			queue = queue.reverse()
			final_chat_list.append(queue)

		return final_chat_list

		

if __name__ == '__main__':
	text = textutil()
	text.pull(0000)
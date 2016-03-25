class Tile(object):
	def __init__(self):
		self.color = (0,0,0)
		self.collides = False

class Floor(Tile):
	def __init__(self):
		self.color = (50,50,50)
		self.collides = False
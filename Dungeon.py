import dungeonGenerationAlgorithms as dga





class Dungeon(object):
	def __init__(self, w, h, method):
		if method == "basic":
			self.grid = dga.generateBasic(w/8,h/8,w/16,h/16,8)
		elif method == "panel":
			self.grid = dga.generatePanel(w,h)
		elif method == "round":
			self.grid = dga.generateRound(w,h, 53)
		elif method == "halls":
			self.grid = dga.generateHalls(w,h, 16,16, 10)
		elif method == "fastH":
			self.grid = dga.generateFastH(w,h, 16,16, 12)
		elif method == "piece":
			self.grid = dga.generatePiece(w,h, w*h/10)
		elif method == "maze1":
			self.grid = dga.generateMazes(w,h, 12, 500, 0.5)
		elif method == "maze2":
			self.grid = dga.generateMazes(w,h, 10, 100, 0.9)
		elif method == "cells":
			self.grid = dga.generateCells(w,h, 3, 4, 0.33, 3)
		elif method == "Rwalk":
			self.grid = dga.generateRWalk(w,h, 8, 1000)
		elif method == "Iwalk":
			self.grid = dga.generateIWalk(w,h, 4, 1000)
		else:
			self.grid = [[]]

		dga.placeTreasure(0.001, self.grid)

	def __str__(self):
		output = ""
		for row in self.grid:
			for blk in row:
				output = output+str(blk)
			output = output+"\n"
		return output



if __name__ == "__main__":
	import doctest
	doctest.testmod()
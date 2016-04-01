from Dungeon import Dungeon
from time import sleep


for method in ["panel","piece","cells","maze1"]:
	test = Dungeon(72, 72, method)
	print test
	print test.countLoot()

	print ""
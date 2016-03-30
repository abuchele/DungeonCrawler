from Dungeon import Dungeon
from time import sleep


for method in ["basic","panel","piece","rooms","Rwalk","cells","maze1","maze2","fastH"]:
	test = Dungeon(72, 72, method)
	print test
	print test.countLoot()
	sleep(1)
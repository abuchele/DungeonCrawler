from Dungeon import Dungeon
from time import sleep


#for method in ["basic","panel","piece","rooms","Rwalk","cells","maze1","maze2","fastH"]:
for method in ["maze1","maze2"]:
	test = Dungeon(72, 72, method)
	print test
	sleep(1)
from Dungeon import Dungeon
from time import sleep


for method in ["basic","panel","piece","Rwalk","cells","maze1","fastH"]:
	test = Dungeon(72, 72, method)
	print test
	sleep(1)
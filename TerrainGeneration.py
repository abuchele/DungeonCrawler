from Dungeon import Dungeon
from time import sleep


for method in ["basic","panel","piece","Iwalk","cells","mazes","fastH"]:
	test = Dungeon(72, 72, method)
	print test
	sleep(3)
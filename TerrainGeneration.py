from Dungeon import Dungeon
from time import sleep
import pickle


method = "whole"
test = Dungeon(2*72, 2*72, method)
print test
f = open("saves/pregeneratedDungeon.txt", 'w')
pickle.dump(test, f)
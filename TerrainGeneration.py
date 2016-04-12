from coreMechanics import Dungeon
from time import sleep
import pickle


method = "whole"
test = Dungeon(120, 120, method=method)
print test
f = open("saves/pregeneratedDungeon.txt", 'w')
pickle.dump(test, f)
f.close()
"""
To-do:

Sprites for different entities
"""

from random import randint

grid = 0

class Entity(object):
    def __init__(self, grid, health=30,speed=1, accuracy=2, flatDamage = 2, damageRange=2, damageMod=2, vision=3, armor=10, phasing = False):
        # self.xpos = xpos
        # self.ypos = ypos
        self.grid = grid        
        self.speed = speed
        self.health = health
        self.accuracy = accuracy
        self.flatDamage = flatDamage
        self.damageRange = damageRange
        self.damageMod = damageMod
        self.vision = vision #sight radius
        self.armor = armor
        self.phasing = phasing
    def attackRoll(self): #1d20+accuracy, if it exceeds armor class it's a hit
        return randint(1,20)+self.accuracy #roll a 20-sided dice and add accuracy to the roll - average is 10.5 + accuracy
    def damage(self):
        return randint(1,self.damageRange)+self.flatDamage #roll a damageRange-sided dice and add flatDamage to the roll
    def attack(this,that):
        if this.attackRoll() >= that.armor:
            damage = this.damage()
            that.health -= damage
            return "{} hits {} for {} damage!".format(str(this),str(that),damage)
        return "{} misses {}!".format(str(this),str(that))

class Player(Entity):
    def __init__(self,x,y, direction="U", health = 100, inventory = None, name = "Mustafa the Magnificient"):
        Entity.__init__(self,grid)
        self.x = x
        self.y = y
        # self.history = (xpos,ypos, xpos, ypos)
        self.direction = direction #direction can be U for up, D for down, L for left, R for right
        # self.speed = speed
        self.health = health
        self.inventory = inventory
        self.name = name
    def __str__(self):
        return self.name

class Monster(Entity):
    def __init__(self): #speed =1,  flatDamage=0, armor=0):
        Entity.__init__(self,grid)
        self.aggro = False
        self.seen = False #With large numbers of monsters, we want them idle when out of player vision

    def passiveMove(self):
        # if self.seen = True:
        direction = [(1,0),(0,1),(-1,0),(0,-1)]
        if self.grid[self.x+1,self.y].collides():
            direction.remove((1,0))
        if self.grid[self.x,self.y+1].collides():
            direction.remove((0,1))
        if self.grid[self.x-1,self.y].collides():
            direction.remove((-1,0))
        if self.grid[self.x,self.y-1].collides():
            direction.remove((0,-1))
        move = direction[randint(0,3)]
        self.x+=move[0]
        self.y+=move[1]
    def aggressiveMove(self,that):
        pass



class Zombie(Monster):
    def __init__(self,x,y):
        Monster.__init__(self)
        self.x = x
        self.y = y
        self.health = 30
        self.accuracy = 3
        self.damageRange = 3
        self.flatDamage = 2
        self.armor = 8
        self.speed = 1
    def __str__(self):
        return "Zombie"

class Ghost(Monster):
    def __init__(self,x,y):
        Monster.__init__(self)
        self.x = x
        self.y = y
        self.health = 20
        self.accuracy = 4
        self.damageRange = 2
        self.flatDamage = 1
        self.armor = 10
        self.speed = 1
        self.phasing = True
    def __str__(self):
        return "Ghost"        


a = Player(0,0)
b = Zombie(1,1)
c = Ghost(2,2)
print b.attack(a)
print a.attack(b)
print c.attack(a)
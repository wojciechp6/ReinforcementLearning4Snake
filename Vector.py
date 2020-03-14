from math import sqrt
class Vector():
    def __init__(self,x,y):
        self.x=x
        self.y=y

    @property
    def mag(self):
        return sqrt(self.x*self.x+self.y*self.y)

    @property
    def norm(self):
        m = mag()
        return Vector(self.x / m, self.y / m)

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x+other.x,self.y+other.y)

    def __substract__(self, other):
        return Vector(self.x-other.x,self.y-other.y)
    
    def __eq__(self, other):
       return True if self.x == other.x and self.y == other.y else False

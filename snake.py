import arcade
from Vector import Vector
from arcade import color
import sys
from random import randrange
import math
import numpy
import random
import copy
import time

#cellSize = 30
#areaSize = Vector(10, 10)


movesArray = []


class SnakeGame(arcade.Window):
    def __init__(self, areaSize = Vector(10, 10), cellSize = 30):
        super().__init__(1000, 600)
        self.snake = [Vector(areaSize.x//2, areaSize.y//2), Vector(areaSize.x//2, areaSize.y//2-1), Vector(areaSize.x//2, areaSize.y//2-2), Vector(areaSize.x//2, areaSize.y//2-3), Vector(areaSize.x//2, areaSize.y//2-4)]
        self.snakeDir = Vector(0, 1)
        self.applePos = Vector(2, 8)
        self.areaSize = areaSize
        self.cellSize = cellSize

    def Step(self, direction, generate=False):
        global snake, applePos, snakeDir

        for i in reversed(range(1, len(self.snake))):
            self.snake[i] = self.snake[i-1]

        self.snakeDir = self.RelativeDir(direction)
        self.snake[0] += self.snakeDir

        if self.snake[0] == self.applePos:
            self.olddist = 99999999
            while True:
                self.applePos = Vector(randrange(0, self.areaSize.x, 1),
                                  randrange(0, self.areaSize.y, 1))
                
                if not self.applePos in self.snake:
                    break
            self.snake.append(self.snake[-1])

        alive = not self.snake[0] in self.snake[1:] and self.WithinArea(self.snake[0])
        left = self.snake[0] + self.RelativeDir(-1) in self.snake or not self.WithinArea(self.RelativeDir(-1))
        right = self.snake[0] + self.RelativeDir(1) in self.snake or not self.WithinArea(self.RelativeDir(1))
        forward = self.snake[0] + self.RelativeDir(0) in self.snake or not self.WithinArea(self.RelativeDir(0))

        angle = math.atan2(self.applePos.x - self.snake[0].x, self.applePos.y - self.snake[0].y) - math.atan2(self.snakeDir.x, self.snakeDir.y)
        angle /= 3.14
        if angle > 1: angle -= 2
        elif angle < -1: angle += 2

        length = Vector(self.applePos.x - self.snake[0].x, self.applePos.y - self.snake[0].y).mag
        
        if not alive:
            self.Death(direction, not generate, not generate)
            
        self.oldState = (left, right, forward, angle, length)
        return alive, left, right, forward, angle, length
    
    def Death(self, move, log=False, call = True):
        global snake, snakeDir
        self.snake = [Vector(self.areaSize.x//2, self.areaSize.y//2), 
                    Vector(self.areaSize.x//2, self.areaSize.y//2-1), 
                    Vector(self.areaSize.x//2, self.areaSize.y//2-2), 
                    Vector(self.areaSize.x//2, self.areaSize.y//2-3), 
                    Vector(self.areaSize.x//2, self.areaSize.y//2-4)]
        self.snakeDir = Vector(0, 1)
        self.olddist = 999999999

        if hasattr(self, "deathCallback") and call:
            self.deathCallback(self.oldState, move)
        
        if log:
            pass
            left = self.snake[0] + self.RelativeDir(-1) in self.snake
            right = self.snake[0] + self.RelativeDir(1) in self.snake
            forward = self.snake[0] + self.RelativeDir(0) in self.snake

    def RelativeDir(self, direction):
        global snakeDir
        if direction == 0:
            return self.snakeDir

        res = Vector(0, 0)
        if self.snakeDir.y != 0:
            res.x = self.snakeDir.y * direction
            res.y = 0
        else:
            res.y = -self.snakeDir.x * direction
            res.x = 0
        return res

    def WithinArea(self, vec):
        return (vec.x >= 0 and vec.x <= self.areaSize.x) and (vec.y >= 0 and vec.y <= self.areaSize.y)

    olddist = 999999
    isalive = True
    def on_draw(self):
        global cellSize, areaSize, snake, applePos
        
        arcade.set_background_color(color.WHITE)
        arcade.start_render()

        self._draw_cell(self.applePos.x, self.applePos.y, arcade.color.ROSEWOOD)
        
        for s in self.snake[1:]:
            self._draw_cell(s.x, s.y, arcade.color.GREEN)
        
        self._draw_cell(self.snake[0].x, self.snake[0].y, arcade.color.ORANGE)
        
        if hasattr(self, "debug"):
            if self.debug != "":
                arcade.draw_text("debug:\n {}".format(self.debug), 10, 50, color.RED)

        if hasattr(self, "updateCallback"):
            self.updateCallback()

    def _draw_cell(self, x, y, color):
        arcade.draw_circle_filled(x*self.cellSize, y*self.cellSize, self.cellSize/2, color)
                
    def Generate(self, iters):
        global snake
        states = []
        inps = []
        results = []
        for _ in range(iters+1):
            inp = random.randint(-1, 1)
            alive, left, right, forward, angle, dist = self.Step(inp, True)
            good = 1 if dist < self.olddist else 0
            good = -1 if not alive else good

            results.append(good)
            states.append([left, right, forward, angle])
            inps.append(inp)
            self.olddist = dist
            
        return results[1:], inps[1:], states[:-1]

    def Move(self):
        global snakeDir, snake
        s = self.snake[0]
        d = self.snakeDir
        inp = random.randint(-1, 1)

        _, _, _, _, _, dist = self.Step(inp)
        good = dist < self.olddist
        snakeDir = d
        snake[0] = s
        
        if good:
            self.Step(inp)
            print(dist)
            self.olddist = dist

    def RandomDirection(self):
        return Vector(random.randint(0, 1)*2-1, 0) if random.randint(0, 1) == 0 else Vector(0, random.randint(0, 1)*2-1)

    def on_key_press(self, key, modifiers):
        self.speed = 0.05
        if key == arcade.key.UP:
            self.Step(0)
        elif key == arcade.key.LEFT:
            self.Step(-1)
        elif key == arcade.key.RIGHT:
            self.Step(1)
        elif key == arcade.key.SPACE:
            self.speed = 1
            

def main():
    window = SnakeGame(1024, 600, "snek")
    #window.updateCallback = window.Move
    arcade.run()


if __name__ == "__main__":
    main()

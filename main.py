
import snake
from snakenn import SnakeNeuralNetwork
from Vector import Vector
import arcade


snak = snake.SnakeGame(Vector(30, 20))
nn = SnakeNeuralNetwork(snak, 0)
snak.updateCallback = nn.Update

arcade.run()
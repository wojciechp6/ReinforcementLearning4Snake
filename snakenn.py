import tensorflow as tf, numpy as np, time, random
import snake
from Vector import Vector


class SnakeNeuralNetwork():
    global state, inpu
    state = [True, 0, 0, 0, 0, 0]
    inpu = 0
    memory, gameMemory = [], []
    games = 0

    e = 0.0
    e_min = 0.05
    e_factor = 0.995

    def __init__(self, snake, start_game = 0):
        self.games = start_game
        self.snak = snake

        self.model = self._create_model()
        if start_game > 0:
            self.model.load_weights("snak_weights_{}.hdf5".format(start_game))

    def _create_model(self):
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Dense(50, input_shape=(4,)))
        model.add(tf.keras.layers.Activation("relu"))
        model.add(tf.keras.layers.Dense(3))
        model.compile(tf.keras.optimizers.Adam(lr=0.005), "mean_squared_error", ['accuracy'])
        return model

    def Update(self, n = 50):
        global state, snak, e

        if random.random() > self.e:
            s = state[1:5]
            results = self.model.predict(np.array(s, ndmin=2))[0]
        else:
            results = np.random.rand(3)

        newState = self.snak.Step(np.argmax(results)-1)
        newState = [x for x in newState]
        
        reward, discount = self.Rate(state, results, newState)
        self.AddToMemory(state, results, newState, reward, discount)
        state = newState

        if state[0] == False: self.Death(state, results)
        if n > 0: self.Update(n-1)

    def Death(self, state, inp):
        self.games += 1

        self._trim_memory(self.gameMemory)
        
        self.gameMemory = self.RewardDiscount(self.gameMemory)
        self.memory.extend(self.gameMemory)
        self.gameMemory.clear()

        if self.games % 10 == 0:
            self.Reinforce(self.memory)

        if self.games % 500 == 0:
            model.save("snak_weights_{}.hdf5".format(games))
            print("-------------saved {}---------------".format(self.games))
    
    def _trim_memory(self, memory):
        if len(memory) > 200000:
            memory = memory[10000:]

    def Rate(self, state, inp, newState):
        if newState[0] == False:
            reward = -1
            discount = True
        elif newState[5] == 0:
            reward = 1
            discount = True 
        elif np.argmax(inp) != 1:
            reward = -0.1
            discount = True 
        else: 
            reward = 0
            discount = False 
        return reward, discount

    def AddToMemory(self, state, inp, newState, reward, discount):
        self.gameMemory.append([state[1:5], inp, reward, newState[1:5], discount])

    def RewardDiscount(self, gameMem, discount = 0.9):
        discountedReward = 0
        for i in reversed(range(len(gameMem))):
            value = gameMem[i][2] if gameMem[i][-1] else 0
            discountedReward = discountedReward * discount + value
            gameMem[i][2] = discountedReward
        return gameMem

    def Reinforce(self, memory):
        if len(memory) < 500: return
        s, i, r, ns = [], [], [], []
        for c in range(1000):
            c = random.choice(memory)
            s.append(c[0])
            i.append(c[1])
            r.append(c[2])
            ns.append(c[3])

        res = self.model.predict(np.array(s, ndmin=2))
        res2 = self.model.predict(np.array(ns, ndmin=2))
        ni = []
        for idx, val in enumerate(res):
            inp = i[idx]
            if r[idx] == 0:
                maxValIdx = np.argmax(inp)
                val[maxValIdx] = r[idx] + 0.99 * max(res2[idx])
            else:
                maxValIdx = np.argmax(inp)
                val[maxValIdx] = r[idx]
            ni.append(val)

        self.model.fit(np.array(s, ndmin=2), np.array(ni, ndmin=2), batch_size=1000, verbose=0)
        self._update_e()
        
    def _update_e(self):
        self.e = max(self.e * self.e_factor, self.e_min)
        self.snak.e = self.e


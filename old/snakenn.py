import tensorflow as tf, numpy as np, time, random
import snake

global state, inpu
state = [True, 0, 0, 0, 0, 0]
inpu = 0
memory, gameMemory = [], []
games = 10000

e = 0.5
e_min = 0.05
e_factor = 0.995

def Update(n = 50):
    global state, snak, e
    #time.sleep(snak.speed)

    if random.random() > e:
        s = state[1:5]
        results = model.predict(np.array(s, ndmin=2))[0]
    else:
        results = np.random.rand(3)

    newState = snak.Step(np.argmax(results)-1)
    newState = [x for x in newState]
    
    AddToMemory(state, results, newState)
    state = newState

    if state[0] == False: Death(state, results)
    if n > 0: Update(n-1)

def Death(state, inp):
    global games, snak, gameMemory
    games += 1

    #gameMemory = RewardDiscount(gameMemory)
    memory.extend(gameMemory)
    gameMemory.clear()

    if len(memory) > 200000:
        for _ in range(1000):
            memory.pop(0)

    if games % 10 == 0:
        Reinforce()

    if games % 500 == 0:
        model.save("snak_weights_{}.hdf5".format(games))
        print("-------------saved {}---------------".format(games))

def AddToMemory(state, inp, newState):
    global gameMemory
    if newState[0] == False:
        reward = -1
        n = 1
    elif newState[5] == 0:
        reward = 1
        n = 1
    elif np.argmax(inp) != 1:
        reward = 0#-0.02
        n = 1
    else: 
        reward = 0
        n = 1
        
    #for _ in range(n):
    #if reward != 0:
    gameMemory.append([state[1:5], inp, reward, newState[1:5]])


def RewardDiscount(gameMem, discout = 0.97):
    discountedReward = 0
    for i in reversed(range(len(gameMem))):
        discountedReward = discountedReward * discout + gameMem[i][2]
        gameMem[i][2] = discountedReward
    return gameMem

def Reinforce():
    global e
    if len(memory) < 500: return
    s, i, r, ns = [], [], [], []
    for c in range(1000):
        c = random.choice(memory)
        s.append(c[0])
        i.append(c[1])
        r.append(c[2])
        ns.append(c[3])

    res = model.predict(np.array(s, ndmin=2))
    res2 = model.predict(np.array(ns, ndmin=2))
    ni = []
    for idx, val in enumerate(res):
        inp = i[idx]
        if r[idx] == 0:
            maxValIdx = np.argmax(inp)
            #val = np.zeros(3)
            val[maxValIdx] = r[idx] + 0.99 * max(res2[idx])
        else:
            maxValIdx = np.argmax(inp)
            val[maxValIdx] = r[idx]
        ni.append(val)
    # r2 = np.zeros((len(r), 3))
    # for i, x in enumerate(r):
    #     r2[i,0] = x

    model.fit(np.array(s, ndmin=2), np.array(ni, ndmin=2), batch_size=1000)

    e = max(e * e_factor, e_min)
    snak.e = e

def rewardLoss(reward, pred):
    return -(tf.log(pred))

model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(30, input_shape=(4,)))
model.add(tf.keras.layers.Activation("relu"))
#model.add(tf.keras.layers.Dense(100))
#model.add(tf.keras.layers.Activation("relu"))
#model.add(tf.keras.layers.Dense(10, tf.keras.layers.Activation("linear")))
model.add(tf.keras.layers.Dense(3))
# model.add(tf.keras.layers.Dense(3, tf.keras.layers.Activation("softmax")))
model.compile(tf.keras.optimizers.Adam(lr=0.005), "mean_squared_error", ['accuracy'])
model.load_weights("snak_weights_{}.hdf5".format(games))

global snak
snak = snake.SnakeGame(1000, 600)
snak.updateCallback = Update
#snak.deathCallback = Death

isGood, inp, states = snak.Generate(1000)

# inp = [x for g, x in zip(isGood, inp) if g != 0]
# states = [x for g, x in zip(isGood, states) if g != 0]
# isGood = [x for x in isGood if x != 0]

for i, x in enumerate(isGood): 
    #isGood[i] = (x + 1)/2
    if x == -1: 
        isGood[i] = -1
    elif x == 1:
        isGood[i] = 1

inp2 = []
for i, x in enumerate(inp):
    a = np.zeros(3)
    a[x+1] = isGood[i]
    inp2.append(a)

# for i, x in enumerate(states):
#     x.extend(inp2[i])

#[print(states[i], isGood[i]) for i, x in enumerate(isGood) if x == -1]

#raise Exception()


states = np.array(states)
inp = np.array(inp2)

#model.fit(states, inp, 1000, 10)

import arcade
snak.speed = 0.0
arcade.run()
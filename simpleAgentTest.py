import requests
import random
import math as m

def runCommand(command):
    print("running cmd %s" % command)
    response = requests.post(url, bytes(command, "utf-8"))
    return response.text


url = 'http://localhost:9000/command'
i = 0

runCommand("say starting")

startPos = [40, 64, 127]

for k in range(0,7):
    # pos = [0, 95, -165]
    pos = startPos
    d = random.random() * m.pi * 2

    for i in range(0, 32):
        test = runCommand("execute if block %i %i %i air" % tuple(pos))
        print(test)
        if test == "1":
            pos[1] -= 1
            if(runCommand("execute if block %i %i %i air" % tuple(pos)) != "1"):
                pos[1] += 1
        else:
            pos[1] += 1
        print(runCommand("setblock %i %i %i oak_log" % tuple(pos)))

        # pos[random.randint(0,1) * 2] += -1 + random.randint(0,1) * 2
        vrc = 1.6
        actD = d - vrc + random.random() * vrc * 2
        qpi = (m.pi / 2)
        # actD = round(d / qpi) * qpi
        pos[0] += round(m.cos(actD))
        pos[2] += round(m.sin(actD))


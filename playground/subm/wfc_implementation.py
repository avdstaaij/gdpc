import numpy as np
import random

def hash(tile, dir=None): 
    # manually specify test area
    x = y = w = h = 0
    if(dir != None): 
        x1 = [1, 0, 0, 0][dir] * (tile.shape[0] - 1)
        y1 = [0, 0, 0, 1][dir] * (tile.shape[1] - 1)
        x2 = x1 + [0, 1, 0, 1][dir] * (tile.shape[0] - 1) + 1
        y2 = y1 + [1, 0, 1, 0][dir] * (tile.shape[1] - 1) + 1
    else: 
        x1 = y1 = 0
        x2 = tile.shape[0]
        y2 = tile.shape[1]

    area = tile[y1:y2, x1:x2]
    return str(area.flatten())
 
def createPropagator(tiles): 
    n = len(tiles)
    propagator = np.zeros((n, 4, n), dtype=int)
    for i in range(n): 
        for dir in range(4):
            hash1 = hash(tiles[i], dir)
            for j in range(n): 
                propagator[i][dir][j] = hash1 == hash(tiles[j], (dir+2) % 4)

    return propagator


xr = [[1,0],[0,-1],[-1,0],[0,1]]
yr = [[0,1],[1,0],[0,-1],[-1,0]]
t = [[0,0],[0,1],[1,1],[1,0]]


def expandRotations(tiles):
    if tiles.shape[1] != tiles.shape[2]:
        return tiles # not square! TODO could still do 180 rots

    newTiles = []
    for tile in tiles: 
        hashes = []
        for d in range(4): 
            tile = np.rot90(tile)
            hashRotated = hash(tile)

            if(not hashRotated in hashes): 
                newTiles.append(tile)
                hashes.append(hashRotated)

    return np.array(newTiles)

deltas = [[1,0], [0,-1], [-1,0], [0,1]]
cacheTileHashes = None
cachedPropagator = None

def runWFC(tiles, w, h, initialTile=0):
    generator = wfcGenerator(tiles, w, h, initialTile)
    image = next(generator)
    try:
        while True:
            next(generator)
    except StopIteration:
        pass
    return image

def wfcGenerator(tiles, w, h, initialTile=0): 
    global cacheTileHashes, cachedPropagator, deltas
    n = len(tiles)
    propagator = None
    if(not cachedPropagator is None and not cacheTileHashes is None and len(cacheTileHashes) == len(tiles)): 
        same = True
        for i in range(n): 
            if(hash(tiles[i]) != cacheTileHashes[i]): 
                same = False
                break


        if(same): 
            propagator = cachedPropagator

    
    if(propagator is None): 
        propagator = cachedPropagator = createPropagator(tiles)
        cacheTileHashes = [hash(tile) for tile in tiles] 

    inBounds = lambda p : p[0]>=0 and p[1]>=0 and p[0]<w and p[1]<h
    possibilitySpace = np.ones((w, h, n), dtype=np.int)
    # buffer that contains number of possible tiles at the positions (inverse of constraint)
    # positions where the possibility space is collapsed to 0 or a tile is already placed have value n+1
    possibilityBuffer = np.ones((w, h), dtype=np.int) * n 

    # edge precondition
    edgeTile = 0
    for x in range(w):
        possibilitySpace[x][0] *= propagator[edgeTile][3]
        possibilitySpace[x][h-1] *= propagator[edgeTile][1]

    for y in range(h):
        possibilitySpace[0][y] *= propagator[edgeTile][0]
        possibilitySpace[w-1][y] *= propagator[edgeTile][2]

    tileW = tiles.shape[1]
    tileH = tiles.shape[2]
    image = np.ones((w * tileW, h * tileH), np.int) * initialTile
    yield image
    while(True): 
        yield image # always the same image! but we still yield it just in case
        # find random maximum constrained position
        minVal = int(np.amin(possibilityBuffer))

        if minVal == n+1:
            break

        tupleList = np.where(possibilityBuffer == minVal)
        listOfCordinates = list(zip(tupleList[0], tupleList[1]))
        p = np.array(listOfCordinates[random.randint(0, len(listOfCordinates) - 1)])

        # replace
        superposition = possibilitySpace[tuple(p)]
        possibleIndeces = np.where(superposition == 1)[0]
        tileIndex = possibleIndeces[random.randrange(len(possibleIndeces))]
        # tileIndex = possibleIndeces[0]
        possibilitySpace[tuple(p)] = np.zeros(n) # reset to 0
        possibilityBuffer[tuple(p)] = n+1
        imgP = p * [tileW, tileH]
        image[imgP[1] : imgP[1]+tileH, imgP[0] : imgP[0] + tileW] = tiles[tileIndex] # "place" the tile
        
        # update neighbors with propagator
        for d in range(4): 
            delta = deltas[d]
            p2 = p + delta
            if(not inBounds(p2)):
                continue
            possibilitySpace[tuple(p2)] *= propagator[tileIndex,d]
            bufVal = np.count_nonzero(possibilitySpace[tuple(p2)])
            bufVal = bufVal if bufVal > 0 else n+1
            possibilityBuffer[tuple(p2)] = bufVal
    yield image # one final time!

def testHash(tile, dir): 
    print(hash(tile, dir))
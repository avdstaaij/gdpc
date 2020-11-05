from math import ceil, log2
from bitarray import BitArray
from io import BytesIO
import requests
import nbt

def getChunks(x, z, dx, dz, rtype = 'text'):
    print("getting chunks %i %i %i %i " % (x, z, dx, dz))
    
    url = 'http://localhost:9000/chunks?x=%i&z=%i&dx=%i&dz=%i' % (x, z, dx, dz)
    print(url)
    acceptType = 'application/octet-stream' if rtype == 'bytes' else 'text/raw'
    response = requests.get(url, headers={"Accept": acceptType})
    print(response.status_code)
    if response.status_code >= 400:
        print(response.text)
    
    if rtype == 'text':
        return response.text
    elif rtype == 'bytes':
        return response.content

class CachedSection:
    def __init__(self, palette, blockStatesBitArray):
        self.palette = palette
        self.blockStatesBitArray = blockStatesBitArray

class WorldSlice:
    # TODO format this to blocks
    def __init__(self, rect):
        self.rect = rect
        self.chunkRect = (rect[0] >> 4, rect[1] >> 4, (rect[2] >> 4) + 1, (rect[2] >> 4) + 1)

        bytes = getChunks(*self.chunkRect, rtype='bytes')
        file_like = BytesIO(bytes)

        self.nbtfile = nbt.nbt.NBTFile(buffer=file_like)

        # heightmaps
        self.heightmap = [[0 for z in range(rect[3])] for x in range(rect[2])]
        self.heightmap2 = [[0 for z in range(rect[3])] for x in range(rect[2])]

        # Sections are in x,z,y order!!! (reverse minecraft order :p)
        self.sections = [[[None for i in range(16)] for z in range(self.chunkRect[3])] for x in range(self.chunkRect[2])]

        for x in range(self.chunkRect[2]):
            for z in range(self.chunkRect[3]):
                chunkID = x + z * self.chunkRect[2]
                chunkSections = self.nbtfile['Chunks'][chunkID]['Level']['Sections']

                # heightmap
                hms = self.nbtfile['Chunks'][chunkID]['Level']['Heightmaps']
                # hmRaw = hms['MOTION_BLOCKING']
                hmRaw = hms['MOTION_BLOCKING_NO_LEAVES']
                hmRaw2 = hms['OCEAN_FLOOR']
                # hmRaw = hms['WORLD_SURFACE']
                heightmapBitArray = BitArray(9, 16*16, hmRaw)
                heightmapBitArray2 = BitArray(9, 16*16, hmRaw2)
                for cz in range(16):
                    for cx in range(16):
                        try:
                            self.heightmap[x * 16 + cx][z * 16 + cz] = heightmapBitArray.getAt(cz * 16 + cx)
                        except IndexError:
                            pass
                        try:
                            self.heightmap2[x * 16 + cx][z * 16 + cz] = heightmapBitArray2.getAt(cz * 16 + cx)
                        except IndexError:
                            pass

                for section in chunkSections:
                    y = section['Y'].value
                    
                    if not ('BlockStates' in section) or len(section['BlockStates']) == 0:
                        continue

                    palette = section['Palette']
                    rawBlockStates = section['BlockStates']
                    bitsPerEntry = max(4, ceil(log2(len(palette))))
                    blockStatesBitArray = BitArray(bitsPerEntry, 16*16*16, rawBlockStates)

                    self.sections[x][z][y] = CachedSection(palette, blockStatesBitArray)




    def getBlockAt(self, blockPos):
        # chunkID = relativeChunkPos[0] + relativeChunkPos[1] * self.chunkRect[2]

        # section = self.nbtfile['Chunks'][chunkID]['Level']['Sections'][(blockPos[1] >> 4)+1]

        # if not ('BlockStates' in section) or len(section['BlockStates']) == 0:
        #     return -1 # TODO return air compound

        # palette = section['Palette']
        # blockStates = section['BlockStates']
        # bitsPerEntry = max(4, ceil(log2(len(palette))))
        chunkX = (blockPos[0] >> 4) - self.chunkRect[0]
        chunkZ = (blockPos[2] >> 4) - self.chunkRect[1]
        chunkY = blockPos[1] >> 4
        # bitarray = BitArray(bitsPerEntry, 16*16*16, blockStates) # TODO this needs to be 'cached' somewhere
        cachedSection = self.sections[chunkX][chunkZ][chunkY]

        if cachedSection == None:
            return None # TODO return air compound instead

        bitarray = cachedSection.blockStatesBitArray
        palette = cachedSection.palette
        
        blockIndex = (blockPos[1] % 16) * 16*16 + (blockPos[2] % 16) * 16 + blockPos[0] % 16
        return palette[bitarray.getAt(blockIndex)]
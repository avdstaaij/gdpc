import math
from math import ceil, log2
from bitarray import BitArray
from io import BufferedReader, BytesIO
import requests
import random
import math as m
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

# print(getChunks(0, 0, 2, 2))
bytes = getChunks(0, 0, 2, 2, rtype='bytes')
print(len(bytes))

print(bytes)
# print(getChunks(0, 0, 2, 2, rtype='text'))
print("")
file_like = BytesIO(bytes)

nbtfile = nbt.nbt.NBTFile(buffer=file_like)

print(nbtfile['Chunks'])
print(nbtfile['Chunks'][0]['Level']['Sections'])
sections = nbtfile['Chunks'][0]['Level']['Sections']

def sectionIsEmpty(section):
    return not ('BlockStates' in section) or len(section['BlockStates']) == 0

for section in sections:
    if not sectionIsEmpty(section):
        palette = section['Palette']
        blockStates = section['BlockStates']
        bitsPerEntry = max(4, ceil(log2(len(palette))))
        bitarray = BitArray(bitsPerEntry, 16*16*16, blockStates)
        
        def printBlock(blockStateID):
            print(palette[blockStateID])

        bitarray.getAll(printBlock)


pass
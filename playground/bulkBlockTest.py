import requests

# buffer for the request body
blockBuffer = ""


# write a block update to the buffer
def registerSetBlock(x, y, z, str):
    global blockBuffer
    blockBuffer += '~%i ~%i ~%i %s \n' % (x, y, z, str)

# send the buffer to the server and clear it
def sendBlocks(x, y, z):
    global blockBuffer
    url = 'http://localhost:9000/blocks?x=%i&y=%i&z=%i' % (x, y, z)
    response = requests.put(url, blockBuffer)
    blockBuffer = ""
    return response.text



# for i in range (8):
for y in range(24):
    for x in range(24):
        for z in range(24):
            registerSetBlock(x, y, z, 'minecraft:quartz_block')

sendBlocks(74, 68, -89)
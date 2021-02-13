import requests
from multiprocessing.dummy import Pool

MAX_SIZE = 2048

pool = Pool(MAX_SIZE)

futures = []

# for x in range(10):
#     futures.append(pool.apply_async(requests.get, ['http://example.com/']))
# futures is now a list of 10 futures.


def setBlockAsync(x, y, z, str):
    checkPool()
    url = 'http://localhost:9000/blocks?x=%i&y=%i&z=%i' % (x, y, z)
    futures.append(pool.apply_async(requests.put, [url, str]))
    # print('setting block %s at %i %i %i' % (str, x, y, z))
    # print("%i, %i, %i: %s - %s" % (x, y, z, response.status_code, response.text))

# def getBlock(x, y, z):
#     url = 'http://localhost:9000/getblock?x=%i&y=%i&z=%i' % (x, y, z)
#     futures.append(pool.apply_async(requests.get, [url]))
#     return response.text
#     # print(url)
#     # print("%i, %i, %i: %s - %s" % (x, y, z, response.status_code, response.text))

def checkPool():
    global futures
    if len(futures) >= MAX_SIZE:
        processRequests()

def processRequests():
    global futures
    for future in futures:
        # print(future.get())
        future.get()
    futures = []


from gevent import monkey
monkey.patch_all()

import time
from worldLoader import WorldSlice, setBlock
import grequests
from requests_threads import AsyncSession


rect = (-33, 27, 8, 8)
ry = 69
# slice = WorldSlice(rect)

session = AsyncSession(n=64)

async def _main():
    for i in range(32):
        x = rect[0]
        y = i + ry
        z = rect[1]
        block = "minecraft:stone"

        urls = []
        for dx in range(0, rect[2]):
            for dz in range(0, rect[3]):
                urls.append('http://localhost:9000/setblock?x=%i&y=%i&z=%i' % (x + dx, y, z + dz))

        rs = []
        for url in urls:
            rs.append(await session.post(url, data=block))
        # print(rs)


if __name__ == '__main__':
    t0 = time.perf_counter()
    try:
        session.run(_main)
    except:
        pass
    print(time.perf_counter() - t0)

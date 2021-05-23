import interfaceUtils as iu
import direct_interface as di

if __name__ == "__main__":
    print("Testing a bug in worldLoader.getBlockCompoundAt")
    print("blocks are accessed at the wrong Y indexes")

    buildarea = iu.requestBuildArea()
    center = ((buildarea[0]+buildarea[3])//2,
              (buildarea[2]+buildarea[5])//2)

    # Creating world datafiles
    iu.makeGlobalSlice()
    ws = iu.globalWorldSlice

    x,z = center

    error = False
    for _x in range(x-1, x+2):
        for _z in range(z-1, z+2):
            for i in range(0,128):
                bws = ws.getBlockAt(_x, i, _z)
                bdi = di.getBlock(_x, i, _z)
                if (bws != bdi and bws != 'minecraft:void_air'):
                    print("{}: ws: {}, di: {}".format((_x,i,_z), bws, bdi))
                    error = True

    if (not error):
        print("It seems like no bug was found! :-)")

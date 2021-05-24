#! /usr/bin/python3
"""### Test various aspects of the framework automatically.

The tests contained in this file include:

-

It is not meant to be imported.
"""

__all__ = []
__version__ = "v4.3_dev"

import random
import sys
import time

import direct_interface
import geometry
import interface
import lookup
import toolbox

# import timeit

# import mapUtils
# import visualizeMap
# import worldLoader
# import example
# import bitarray


class TestException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

    # inherited __repr__ from OrderedDict is sufficient


def verifyPaletteBlocks():
    """Check blockColours blocks."""
    print(f"\n{lookup.TCOLORS['yellow']}Running blockColours palette test...")

    print(f"\t{lookup.TCOLORS['gray']}Preparing...", end="\r")
    tester = interface.Interface()
    counter = 0
    badcounter = 0
    passed = []
    tocheck = [block for i in lookup.PALETTE.values()
               for block in i] + list(lookup.MAPTRANSPARENT)
    print(f"\t{lookup.TCOLORS['gray']}Preparing done.")

    for block in tocheck:
        if block in passed:
            badcounter += 1
            print()
            print(f"\t\t{lookup.TCOLORS['gray']}{block} is duplicated")
        elif not tester.placeBlock(0, 0, 0, block).isnumeric():
            badcounter += 1
            print()
            print(tester.placeBlock(0, 0, 0, block))
            print(f"\t\t{lookup.TCOLORS['orange']}Cannot verify {block}")
        counter += 1
        passed.append(block)
        print(f"\t{lookup.TCOLORS['blue']}{counter}"
              f"{lookup.TCOLORS['CLR']} blocks verified.", end='\r')
    tester.placeBlock(0, 0, 0, 'air')
    if badcounter > 0:
        raise TestException(f"{lookup.TCOLORS['red']}{badcounter}/"
                            f"{lookup.TCOLORS['gray']}{counter}"
                            f"{lookup.TCOLORS['red']} blocks duplicate "
                            "or could not be verified.\n"
                            f"{lookup.TCOLORS['orange']}"
                            "Please check you are running"
                            f" on Minecraft {lookup.VERSION}")

    print(f"{lookup.TCOLORS['green']}"
          f"All {counter} blocks successfully verified!")


def testSynchronisation():
    print(f"\n{lookup.TCOLORS['yellow']}Running synchronization test...")
    print(f"\t{lookup.TCOLORS['gray']}Testing y-indexes...", end='\r')

    buildarea = interface.requestBuildArea()
    center = ((buildarea[0] + buildarea[3]) // 2,
              (buildarea[2] + buildarea[5]) // 2)

    # Creating world datafiles
    ws = interface.makeGlobalSlice()

    x, z = center

    error = False
    for _x in range(x - 1, x + 2):
        for _z in range(z - 1, z + 2):
            for i in range(0, 128):
                bws = ws.getBlockAt(_x, i, _z)
                bdi = direct_interface.getBlock(_x, i, _z)
                if (bws != bdi and bws != 'minecraft:void_air'):
                    print("{}: ws: {}, di: {}".format((_x, i, _z), bws, bdi))
                    error = True

    if error:
        raise TestException("Worldslice's blocks do not align in the Y-axis.")

    print("\tTesting y-indexes done.")
    print(f"{lookup.TCOLORS['green']}Synchronization test complete!")


def testShapes():
    """**Check shape construction**."""
    # TODO: Fill me!
    print(f"\n{lookup.TCOLORS['yellow']}Running shape test..."
          f"{lookup.TCOLORS['gray']}")
    geometry.placeVolume(63, 159, 63, 0, 128, 0, 'air')

    # placeLine
    geometry.placeLine(0, 128, 0, 0, 128, 0, 'red_concrete')            # 0D

    geometry.placeLine(0, 128, 16, 15, 128, 16, 'red_concrete')         # 1D x
    geometry.placeLine(0, 128, 16, 0, 143, 16, 'red_concrete')          # 1D y
    geometry.placeLine(0, 128, 16, 0, 128, 31, 'red_concrete')          # 1D z

    geometry.placeLine(0, 128, 32, 15, 143, 32, 'red_concrete')         # 2D++0
    geometry.placeLine(0, 128, 32, 0, 143, 47, 'red_concrete')          # 2D0++
    geometry.placeLine(0, 128, 32, 15, 128, 47, 'red_concrete')         # 2D+0+
    geometry.placeLine(15, 143, 47, 0, 128, 47, 'red_concrete')         # 2D--0
    geometry.placeLine(15, 143, 47, 15, 128, 32, 'red_concrete')        # 2D0--
    geometry.placeLine(15, 143, 47, 0, 143, 32, 'red_concrete')         # 2D-0-

    geometry.placeLine(0, 128, 48, 7, 135, 55, 'red_concrete')          # 3D+++
    geometry.placeLine(15, 143, 63, 7, 135, 55, 'red_concrete')         # 3D---
    interface.globalinterface.placeBlock(7, 135, 55, 'gold_block')

    # placeVolume
    geometry.placeVolume(16, 128, 0, 16, 128, 0, 'orange_concrete')       # 0D

    geometry.placeVolume(16, 128, 16, 31, 128, 16,
                         'orange_concrete')     # 1D x
    geometry.placeVolume(16, 128, 16, 16, 143, 16,
                         'orange_concrete')     # 1D y
    geometry.placeVolume(16, 128, 16, 16, 128, 31,
                         'orange_concrete')     # 1D z

    geometry.placeVolume(16, 128, 32, 31, 143, 32,
                         'orange_concrete')     # 2D xy
    geometry.placeVolume(16, 128, 32, 16, 143, 47,
                         'orange_concrete')     # 2D yz
    geometry.placeVolume(16, 128, 32, 31, 128, 47,
                         'orange_concrete')     # 2D xz

    geometry.placeVolume(16, 128, 48, 31, 143, 63, 'orange_concrete')     # 3D

    # placeCuboid
    geometry.placeCuboid(32, 128, 0, 32, 128, 0, 'yellow_concrete')     # 0D
    geometry.placeCuboid(32, 144, 0, 32, 144, 0, 'yellow_stained_glass',
                         hollow=True)

    geometry.placeCuboid(32, 128, 16, 47, 128, 16, 'yellow_concrete')   # 1D x
    geometry.placeCuboid(32, 144, 16, 47, 144, 16, 'yellow_stained_glass',
                         hollow=True)
    geometry.placeCuboid(32, 128, 16, 32, 143, 16, 'yellow_concrete')   # 1D y
    geometry.placeCuboid(32, 144, 16, 32, 159, 16, 'yellow_stained_glass',
                         hollow=True)
    geometry.placeCuboid(32, 128, 16, 32, 128, 31, 'yellow_concrete')   # 1D z
    geometry.placeCuboid(32, 144, 16, 32, 144, 31, 'yellow_stained_glass',
                         hollow=True)

    geometry.placeCuboid(32, 128, 32, 47, 143, 32, 'yellow_concrete')   # 2D xy
    geometry.placeCuboid(32, 144, 32, 47, 159, 32, 'yellow_stained_glass',
                         hollow=True)
    geometry.placeCuboid(32, 128, 32, 32, 143, 47, 'yellow_concrete')   # 2D yz
    geometry.placeCuboid(32, 144, 32, 32, 159, 47, 'yellow_stained_glass',
                         hollow=True)
    geometry.placeCuboid(32, 128, 32, 47, 128, 47, 'yellow_concrete')   # 2D xz
    geometry.placeCuboid(32, 144, 32, 47, 144, 47, 'yellow_stained_glass',
                         hollow=True)

    geometry.placeCuboid(32, 128, 48, 47, 143, 63, 'yellow_concrete')   # 3D
    geometry.placeCuboid(32, 144, 48, 47, 159, 63, 'yellow_stained_glass',
                         hollow=True)

    # placeCylinder axis = x
    geometry.placeCylinder(48, 128, 0, 48, 128, 0, 'lime_concrete')     # 0D
    geometry.placeCylinder(48, 144, 0, 48, 144, 0, 'lime_stained_glass',
                           hollow=True)

    geometry.placeCylinder(48, 128, 16, 63, 128, 16, 'lime_concrete')   # 1D x
    geometry.placeCylinder(48, 144, 16, 63, 144, 16, 'lime_stained_glass',
                           hollow=True)
    geometry.placeCylinder(48, 128, 16, 48, 143, 16, 'lime_concrete')   # 1D y
    geometry.placeCylinder(48, 144, 16, 48, 159, 16, 'lime_stained_glass',
                           hollow=True)
    geometry.placeCylinder(48, 128, 16, 48, 128, 31, 'lime_concrete')   # 1D z
    geometry.placeCylinder(48, 144, 16, 48, 144, 31, 'lime_stained_glass',
                           hollow=True)

    # 2D xy (z axis)
    geometry.placeCylinder(48, 128, 32, 63, 143, 32, 'lime_concrete', axis='z')
    geometry.placeCylinder(48, 144, 32, 63, 159, 32, 'lime_stained_glass',
                           hollow=True, axis='z')
    # 2D yz (x axis)
    geometry.placeCylinder(48, 128, 32, 48, 143, 47, 'lime_concrete', axis='x')
    geometry.placeCylinder(48, 144, 32, 48, 159, 47, 'lime_stained_glass',
                           hollow=True, axis='x')
    # 2D xz (default axis)
    geometry.placeCylinder(48, 128, 32, 63, 128, 47, 'lime_concrete')
    geometry.placeCylinder(48, 144, 32, 63, 144, 47, 'lime_stained_glass',
                           hollow=True)

    # 3D x axis
    geometry.placeCylinder(48, 128, 48, 63, 143, 63, 'lime_concrete', axis='x')
    geometry.placeCylinder(48, 144, 48, 63, 159, 63, 'lime_stained_glass',
                           hollow=True, axis='x')
    # 3D default axis
    geometry.placeCylinder(48, 128, 48, 63, 143, 63, 'lime_concrete')
    geometry.placeCylinder(48, 144, 48, 63, 159, 63, 'lime_stained_glass',
                           hollow=True)
    # 3D z axis
    geometry.placeCylinder(48, 128, 48, 63, 143, 63, 'lime_concrete', axis='z')
    geometry.placeCylinder(48, 144, 48, 63, 159, 63, 'lime_stained_glass',
                           hollow=True, axis='z')

    reply = input(f"\t{lookup.TCOLORS['blue']}\aHave all shapes generated "
                  f"correctly? (y/*): {lookup.TCOLORS['CLR']}")

    if reply != 'y':
        raise TestException(f"Shapes were failed:\n"
                            f"\t{reply}")

    geometry.placeVolume(63, 159, 63, 0, 128, 0, 'air')
    print(f"{lookup.TCOLORS['green']}Shape test complete!")


def testBooks():
    """**Check book creation and storage**."""
    print(f"\n{lookup.TCOLORS['yellow']}Running book test...")
    TITLE = 'Testonomicon'
    AUTHOR = 'Dr. Blinkenlights'
    DESCRIPTION = 'All is doomed that enters here.'
    DESCRIPTIONCOLOR = 'aqua'

    CRITERIA = ('Lectern is at 0 255 0 and displays correctly?',
                'Lectern is facing east?', 'Book is legible?',
                'Book contents is correct?', 'Final page is displayed?')

    text = ('New line:\n'
            'Automatic sentence line breaking\n'
            'Automatic_word_line_breaking\n'
            '\\cCenter-aligned\n'
            '\\rRight-aligned\n'
            'New page:\f'
            '§6gold text§r\n'
            '§k█§r < obfuscated text§r\n'
            '§lbold§r text§r\n'
            '§mstriked§r text§r\n'
            '§nunderlined§r text§r\n'
            '§oitalic§r text§r\n'
            '\f\\\\s╔══════════╗\\\\n'
            '║                      `║\\\\n'
            '║                      `║\\\\n'
            '║:   Preformatted  :║\\\\n'
            '║         Page       `║\\\\n'
            '║                      `║\\\\n'
            '║                      `║\\\\n'
            '║        ☞⛏☜       .║\\\\n'
            '║                      `║\\\\n'
            '║                      `║\\\\n'
            '║                      `║\\\\n'
            '║                      `║\\\\n'
            '║                      `║\\\\n'
            '╚══════════╝')

    print(f"\t{lookup.TCOLORS['gray']}Writing book...", end="\r")
    book = toolbox.writeBook(text, TITLE, AUTHOR,
                             DESCRIPTION, DESCRIPTIONCOLOR)
    print("\tWriting book done.")

    print("\tPlacing lectern...", end="\r")
    toolbox.placeLectern(0, 255, 0, book, 'east')
    print("\tPlacing lectern done.")

    print("\tPrompting user...", end="\r")
    for no, prompt in enumerate(CRITERIA):
        reply = input(f"\t{lookup.TCOLORS['blue']}\a{no+1}/{len(CRITERIA)} "
                      f"{prompt} (y/*): {lookup.TCOLORS['CLR']}")
        if reply == '' or reply[0].lower() != 'y':
            raise TestException(f"Book criteria #{no} was failed:\n"
                                f"\t{prompt}: {reply}")
    print(f"{lookup.TCOLORS['green']}Book test complete!")
    interface.globalinterface.placeBlock(0, 255, 0, "air")


def testCache():
    """**Check Interface cache functionality**."""
    print(f"\n{lookup.TCOLORS['yellow']}Running Interface cache test...")
    SIZE = 16
    PALETTES = (("birch_fence", "stripped_birch_log"),
                ("dark_oak_fence", "stripped_dark_oak_log"))

    def clearTestbed():
        """Clean testbed for placement from memory."""
        print("\t\tWiping blocks...", end="\r")
        geometry.placeVolume(0, 1, 0, SIZE - 1, 1, SIZE - 1,
                             "shroomlight", tester)
        tester.sendBlocks()
        print("\n\t\tWiping blocks done.")

    def placeFromCache():
        """Replace all removed blocks from memory."""
        print("\t\tReplacing blocks from memory...", end="\r")
        tester.caching = True
        for x, z in toolbox.loop2d(SIZE, SIZE):
            tester.placeBlock(x, 1, z, tester.getBlock(x, 1, z))
        tester.sendBlocks()
        tester.caching = False
        print("\n\t\tReplacing blocks from memory done.")

    def checkDiscrepancies():
        """Check test bed and comparison layer for discrepancies."""
        for x, z in toolbox.loop2d(SIZE, SIZE):
            print("\t\tTesting...▕" + (10 * x // SIZE) * "█"
                  + (10 - 10 * x // SIZE) * "▕", end="\r")

            for palette in PALETTES:
                if tester.getBlock(x, 1, z) == "minecraft:shroomlight":
                    raise TestException(
                        f"{lookup.TCOLORS['red']}Block at "
                        f"{lookup.TCOLORS['orange']}{x} 0 {z} "
                        f"{lookup.TCOLORS['red']}was no longer in memory.")
                if (tester.getBlock(x, 0, z) == palette[0]
                        and tester.getBlock(x, 1, z) != palette[1]):
                    raise TestException(
                        f"{lookup.TCOLORS['red']}Cache test failed at "
                        f"{lookup.TCOLORS['orange']}{x} 0 {z}"
                        f"{lookup.TCOLORS['red']}.")
        print("\t\tTesting...▕██████████")
        print(f"\t{lookup.TCOLORS['darkgreen']}No discrepancies found.")

    def muddle():
        for i in range(4 * SIZE):
            print("\t\tMuddling...▕" + (10 * i // SIZE) * "█"
                  + (10 - 10 * i // SIZE) * "▕", end="\r")
            x = random.randint(0, SIZE - 1)
            z = random.randint(0, SIZE - 1)
            if random.choice([True, False]):
                type = random.choice(PALETTES)
                tester.caching = True
                tester.placeBlock(x, 1, z, type[1])
                tester.caching = False
                tester.placeBlock(x, 0, z, type[0])
                tester.sendBlocks()
            else:
                tester.caching = True
                tester.getBlock(x, 1, z)
                tester.caching = False
        print("\t\tMuddling...▕██████████")
        print("\t\tMuddling complete.")

    # ---- preparation
    print(f"\t{lookup.TCOLORS['gray']}Preparing...", end="\r")
    tester = interface.Interface(buffering=True, bufferlimit=SIZE ** 2)
    geometry.placeVolume(0, 2, 0, SIZE - 1, 2, SIZE - 1, "bedrock", tester)
    geometry.placeVolume(0, 0, 0, SIZE - 1, 1, SIZE - 1, "air", tester)
    tester.sendBlocks()
    tester.cache.maxsize = (SIZE ** 2)
    print("\tPerparing done.")

    # ---- test block scatter
    print("\tScattering test blocks...", end="\r")
    for x, z in toolbox.loop2d(SIZE, SIZE):
        print("\tPlacing pattern...▕" + (10 * x // SIZE) * "█"
              + (10 - 10 * x // SIZE) * "▕", end="\r")
        type = random.choice(PALETTES)
        tester.caching = True
        tester.placeBlock(x, 1, z, type[1])
        tester.caching = False
        tester.placeBlock(x, 0, z, type[0])
    tester.sendBlocks()
    print("\tPlacing pattern...▕██████████")
    print("\tScattering test blocks done.")

    # ---- first run (caching through placeBlock)
    print(f"\t{lookup.TCOLORS['gray']}First run: Cache updated via placeBlock")

    clearTestbed()
    placeFromCache()
    checkDiscrepancies()

    # ---- second run (caching through getBlock)
    print(f"\t{lookup.TCOLORS['gray']}Second run: Cache updated via getBlock")

    tester.cache.clear
    tester.caching = True
    for x, z in toolbox.loop2d(SIZE, SIZE):
        print("\t\tReading...▕" + (10 * x // SIZE) * "█"
              + (10 - 10 * x // SIZE) * "▕", end="\r")
        tester.getBlock(x, 1, z)
    tester.caching = False
    print("\t\tReading...▕██████████")
    print("\t\tCache refilled.")

    clearTestbed()
    placeFromCache()
    checkDiscrepancies()

    # ---- third run (randomized get-/placeBlock)
    print(f"\t{lookup.TCOLORS['gray']}Third run: "
          "Cache updated via random methods")

    muddle()
    clearTestbed()
    placeFromCache()
    checkDiscrepancies()

    # ---- fourth run (using WorldSlice)
    print(f"\t{lookup.TCOLORS['gray']}Fourth run: "
          "Cache updated via WorldSlice")

    muddle()

    print("\t\tGenerating global slice...", end="\r")
    d0 = time.perf_counter()
    interface.makeGlobalSlice()
    dt = time.perf_counter()
    print(f"\t\tGenerated global slice in {(dt-d0):.2f} seconds.")

    clearTestbed()
    placeFromCache()
    checkDiscrepancies()

    # ---- cleanup
    print(f"{lookup.TCOLORS['green']}Cache test complete!")
    geometry.placeVolume(0, 0, 0, SIZE, 1, SIZE, "bedrock", tester)
    interface.globalWorldSlice = None
    interface.globalDecay = None


if __name__ == '__main__':
    AUTOTESTS = (verifyPaletteBlocks, testCache, testSynchronisation)
    MANUALTESTS = (testBooks, testShapes)
    tests = AUTOTESTS + MANUALTESTS

    if len(sys.argv) > 1:
        if sys.argv[1] == '--manual':
            tests = MANUALTESTS
    else:
        tests = AUTOTESTS

    print(f"Beginning test suite for version "
          f"{lookup.TCOLORS['blue']}{__version__}: {len(tests)} tests")
    interface.setBuildArea(0, 0, 0, 255, 255, 255)
    failed = 0
    errors = ""
    for test in tests:
        try:
            test()
        except TestException as e:
            errors += f"{lookup.TCOLORS['red']}> {test.__name__}() failed.\n" \
                + f"{lookup.TCOLORS['gray']}Cause: {e}\n"
            failed += 1
    print(f"\n{lookup.TCOLORS['CLR']}\aTest suite completed with "
          f"{lookup.TCOLORS['orange']}{failed}"
          f"{lookup.TCOLORS['CLR']} fails!\n")
    if errors != "":
        print(f"==== Summary ====\n{errors}{lookup.TCOLORS['CLR']}")

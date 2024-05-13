# Tutorial: Building a house

## Introduction

This tutorial will go through the step-by-step process of building a house with
GDPC. It will pass over most of the main components of the library, explaining
them as they come along. The house will be built on the ground at a spot that
can be specified in-game, and will have some simple randomization.


## Preparing a world

First, we'll create a Minecraft world to build in. Any world will do, but the
following settings may help:

- **Game Mode:** Creative.
- **Difficulty:** Peaceful.
- **Allow Cheats:** ON.
- **More world options / World Type:** Single Biome.\
  By default, this will create a plains-only world, which is quite useful for
  testing.


## The Editor object

Nearly every GDPC program will begin with creating an {class}`.Editor` object.
This object will serve as the main point of communication between GDPC and the
GDMC-HTTP mod, and therefore, the Minecraft world.

We will enable the Editor's buffering mode by setting {python}`buffering = True`.
This will cause the Editor to collect batches of block changes before sending
them all to the GDMC-HTTP interface at once. This significantly improves
performance, and is highly recommended in all cases where it does not matter
that the world changes are staggered.

```{code-block} python

from gdpc import Editor, Block

editor = Editor(buffering=True)
```


## Working with the build area

The GDMC HTTP interface includes a concept called the *build area*. This is a 3D
box that can be set with a command in-game and then retrieved from code. It's a
convenient way to control where your program operates, and the standard way of
doing so in the GDMC competition. We'll be using it as well.

```{note}
In GDPC, the build area is merely a suggestion: its bounds are not enforced. It
is up to you to request the build area and adhere to it. Future versions may
however add (optional) enforcement.
```

To set the build area, we will use the in-game `/setbuildarea` command. It takes
six arguments: `xFrom`, `yFrom`, `zFrom`, `xTo`, `yTo`, `zTo` -- The
coordinates of two corners (inclusive). The command supports Minecraft's
[Relative coordinate notation](https://minecraft.wiki/Coordinates#Commands):
`~10` indicates "the player's position in that axis, plus 10 blocks". In
Minecraft, the Y-coordinate indicates height, so you usually want to keep
`yFrom` and `yTo` static.

Set the build area to a 64x256x64 box starting at our current (X,Z)-position and
spanning from Y=0 to Y=255 with the following command:

```
/setbuildarea ~ 0 ~ ~64 255 ~64
```

```{image} ../images/setbuildarea-example.png
:width: 10000
```

```{tip}
You can re-use the command at a different location by pressing {keys}`Up` while
the chat is open.
```

We can now retrieve the specified build area in our program with
{meth}`Editor.getBuildArea`. This function returns the build area as a
{class}`Box` object, which is a simple wrapper around an offset and a size.

```{code-block} python
:emphasize-lines: 5-6

from gdpc import Editor, Block

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()
print(buildArea)
```

If you run the program, it should print the box you just specified in-game.


## Building the floor

For now, we'll build the house up in the air (Y=100) -- We'll look at finding
the ground later. We'll start with a floor of stone bricks:

```{code-block} python
:emphasize-lines: 7-11

from gdpc import Editor, Block

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()

y = 100

for x in range(buildArea.offset.x, buildArea.offset.x + 5):
    for z in range(buildArea.offset.z, buildArea.offset.z + 5):
        editor.placeBlock((x, y, z), Block("stone_bricks"))
```

The {meth}`.Editor.placeBlock` function takes two mandatory arguments: the
position where to place a block (a 3D vector) and the block to place
(a {class}`.gdpc.Block` object).

```{note}
In GDPC, anything that "acts like a vector" will work for vector parameters. If
GDPC *returns* a vector, it will always be a
[PyGLM](https://github.com/Zuzu-Typ/PyGLM) vector object, which has useful
`.x` `.y` `.z` attributes.
For more info, see [Vectors](../overview/vectors.md).
```


## Using a geometry helper

Looping through the floor coordinates is fine and all, but we can make it
simpler using a helper function from {mod}`gdpc.geometry`! This module contains
functions for building all kinds of geometrical shapes. We'll use
{func}`.placeCuboid`, which places a solid box of blocks between two given
corners (inclusive).

```{code-block} python
:emphasize-lines: 2, 9-12

from gdpc import Editor, Block
from gdpc.geometry import placeCuboid

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()

y = 100
x = buildArea.offset.x
z = buildArea.offset.z

placeCuboid(editor, (x, y, z), (x+4, y, z+4), Block("stone_bricks"))
```

## Clearing the area

Before we go further, we'll add some code to clear out the area around our
house.
To "remove" blocks in the world, you can place `Block("air")` on top of
them:

```{code-block} python
:emphasize-lines: 12-13

from gdpc import Editor, Block
from gdpc.geometry import placeCuboid

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()

y = 100
x = buildArea.offset.x
z = buildArea.offset.z

# Clear out the area
placeCuboid(editor, (x, y, z), (x+4, y+6, z+4), Block("air"))

placeCuboid(editor, (x, y, z), (x+4, y, z+4), Block("stone_bricks"))
```


## Building the main shape

Next, we'll build the walls and ceiling. We can use a trick here: we can place
a hollow box with {func}`.geometry.placeCuboidHollow` and then overwrite
the floor with `placeCuboid()`.

```{code-block} python
:emphasize-lines: 2, 15-17

from gdpc import Editor, Block
from gdpc.geometry import placeCuboid, placeCuboidHollow

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()

y = 100
x = buildArea.offset.x
z = buildArea.offset.z

# Clear out the area
placeCuboid(editor, (x, y, z), (x+4, y+6, z+4), Block("air"))

# Build main shape
placeCuboidHollow(editor, (x, y, z), (x+4, y+4, z+4), Block("oak_planks"))
placeCuboid(editor, (x, y, z), (x+4, y, z+4), Block("stone_bricks"))
```


## Adding a roof

Now, let's move on to the roof! A common building technique for roofs is to use
stairs blocks. Unlike the blocks we've used so far, stairs blocks can have
different configurations: they can face in multiple directions, and can even be
upside-down. In Minecraft, basic block configurations like these are usually
denoted using key-value properties called
[block states](https://minecraft.wiki/w/Block_states). One way to view
a block's block states is to press {keys}`F3` and look at it. The block ID and
block states will be shown at the bottom right, below "Targeted Block".

```{figure} ../images/f3-block.png
:width: 34em
:align: center

Block info shown by the {keys}`F3` view. We've higlighted the block ID in
red and the block states in yellow.
```

In GDPC, you can specify the block states of a {class}`.Block` instance bye
passing a dict as the second parameter:

```python
block = Block("oak_stairs", {"facing": "east", "half": "bottom"})
```

```{note}
Blocks can also have a third property called *block entity data*, which we won't
go into here. For more info, see [Blocks](../overview/blocks.md).
```

Now, let's build the roof. This one will be a little more complicated, since the
roof will be diagonal. We'll also move the house one block over in the X and Z
directions to make space for some overhang.

```{code-block} python
:emphasize-lines: 9-10, 19-30

from gdpc import Editor, Block
from gdpc.geometry import placeCuboid, placeCuboidHollow

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()

y = 100
x = buildArea.offset.x + 1
z = buildArea.offset.z + 1

# Clear out the area
placeCuboid(editor, (x, y, z), (x+4, y+6, z+4), Block("air"))

# Build main shape
placeCuboidHollow(editor, (x, y, z), (x+4, y+4, z+4), Block("oak_planks"))
placeCuboid(editor, (x, y, z), (x+4, y, z+4), Block("stone_bricks"))

# Build roof: loop through distance from the middle
for dx in range(1, 4):
    yy = y + 6 - dx

    # Build row of stairs blocks
    leftBlock  = Block("oak_stairs", {"facing": "east"})
    rightBlock = Block("oak_stairs", {"facing": "west"})
    placeCuboid(editor, (x+2-dx, yy, z-1), (x+2-dx, yy, z+5), leftBlock)
    placeCuboid(editor, (x+2+dx, yy, z-1), (x+2+dx, yy, z+5), rightBlock)

# build the top row of the roof
placeCuboid(editor, (x+2, y+5, z-1), (x+2, y+5, z+5), Block("oak_planks"))
```


## Finding the ground

It's now time to actually place the house on the ground, which means we need to
find it. There are multiple ways to go about this. For example, you could scan
the world from top to bottom with {meth}`.Editor.getBlock`. However, the easiest
method is probably by using a *heightmap*. Minecraft itself keeps track of
several [heightmaps](https://minecraft.wiki/w/Heightmap), to which GDPC provides
access via the {class}`.WorldSlice` class.

The `WorldSlice` class acts as a snapshot of the world, and allows for very fast
block retrieval once it's been loaded. For this tutorial, however, we'll only
use its heightmap feature.

You can explicitly construct a `WorldSlice` instance, but the recommended way is
to use {meth}`.Editor.loadWorldSlice`, which will make it available as
{attr}`.Editor.worldSlice`. This way, you can also configure the `Editor` to use
the `WorldSlice` as a cache for block retrieval. By default,
`Editor.loadWorldSlice()` will load the specified build area.

```{code-block} python
:emphasize-lines: 8-9

from gdpc import Editor, Block
from gdpc.geometry import placeCuboid, placeCuboidHollow

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()

# Load world slice of the build area
editor.loadWorldSlice(cache=True)

# (...)
```

The heightmaps are available as a dictionary of 2D
[numpy](https://numpy.org/doc/stable/) arrays indexed with (X,Z)-coordinates,
with `[0,0]` indicating the height at the start of WorldSlice (in our case, the
build area). We'll use the "MOTION_BLOCKING_NO_LEAVES" heightmap, which stores
the heights of the highest blocks that block motion or contain a fluid but which
are not leaves. That's usually what we consider "the ground" (tree trunks are an
exception).

```{code-block} python
:emphasize-lines: 6-7

# (...)

# Load world slice of the build area
editor.loadWorldSlice(cache=True)

# Get heightmap
heightmap = editor.worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

# (...)
```

We'll place the house such that the midpoint is flush with the ground. The
heightmap values actually contain the Y-level of one block _above_ the highest
one, so we subtract one from the value.

```{code-block} python
:emphasize-lines: 8-12, 17

from gdpc import Editor, Block
from gdpc.geometry import placeCuboid, placeCuboidHollow

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()

# Load world slice of the build area
editor.loadWorldSlice(cache=True)

# Get heightmap
heightmap = editor.worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

x = buildArea.offset.x + 1
z = buildArea.offset.z + 1

y = heightmap[3,3] - 1

# Clear out the area
placeCuboid(editor, (x, y, z), (x+4, y+6, z+4), Block("air"))

# Build main shape
placeCuboidHollow(editor, (x, y, z), (x+4, y+4, z+4), Block("oak_planks"))
placeCuboid(editor, (x, y, z), (x+4, y, z+4), Block("stone_bricks"))

# Build roof: loop through distance from the middle
for dx in range(1, 4):
    yy = y + 6 - dx
    leftBlock  = Block("oak_stairs", {"facing": "east"})
    rightBlock = Block("oak_stairs", {"facing": "west"})
    placeCuboid(editor, (x+2-dx, yy, z-1), (x+2-dx, yy, z+5), leftBlock)
    placeCuboid(editor, (x+2+dx, yy, z-1), (x+2+dx, yy, z+5), rightBlock)

# build the top row of the roof
placeCuboid(editor, (x+2, y+5, z-1), (x+2, y+5, z+5), Block("oak_planks"))
```

```{important}
If you've been using the same build area, now would be a good time to start
moving and changing it between steps. Otherwise, the house will build on top of
the previous one!
```


## Adding randomization

One of the advantages of building a house piece-by-piece like this, is that it's
easy to add in variation. We're going to randomize the following three aspects
of the house:

- Its height
- Its depth
- Its materials

First off, the height and depth. We'll use Python's {func}`random.randint`
function to randomly set `height` and `depth` variables within a set range, and
replace some of our hardcoded values with them:

```{code-block} python
:emphasize-lines: 1, 20-21, 24, 27-28, 32, 37-38, 41-42

from random import randint
from gdpc import Editor, Block
from gdpc.geometry import placeCuboid, placeCuboidHollow

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()

# Load world slice of the build area
editor.loadWorldSlice(cache=True)

# Get heightmap
heightmap = editor.worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

x = buildArea.offset.x + 1
z = buildArea.offset.z + 1

y = heightmap[3,3] - 1

height = randint(3, 7)
depth  = randint(3, 10)

# Clear out the area
placeCuboid(editor, (x, y, z), (x+4, y+height+2, z+depth), Block("air"))

# Build main shape
placeCuboidHollow(editor, (x, y, z), (x+4, y+height, z+depth), Block("oak_planks"))
placeCuboid(editor, (x, y, z), (x+4, y, z+depth), Block("stone_bricks"))

# Build roof: loop through distance from the middle
for dx in range(1, 4):
    yy = y + height + 2 - dx

    # Build row of stairs blocks
    leftBlock  = Block("oak_stairs", {"facing": "east"})
    rightBlock = Block("oak_stairs", {"facing": "west"})
    placeCuboid(editor, (x+2-dx, yy, z-1), (x+2-dx, yy, z+depth+1), leftBlock)
    placeCuboid(editor, (x+2+dx, yy, z-1), (x+2+dx, yy, z+depth+1), rightBlock)

# build the top row of the roof
yy = y + height + 1
placeCuboid(editor, (x+2, yy, z-1), (x+2, yy, z+depth+1), Block("oak_planks"))
```


As for the materials, we'll randomize them in two ways: for the walls, we'll
randomly pick from a few options using Python's {func}`random.choice` function.
For the floor, we'll use another feature of GDPC: random block palettes. We can
pass a *list* of blocks instead of a single one to any block-placing function,
and GDPC will automatically sample the palette randomly. This can be useful for
achieving a more "rugged" look.

```{code-block} python
:emphasize-lines: 1, 23-37, 43-44

from random import randint, choice
from gdpc import Editor, Block
from gdpc.geometry import placeCuboid, placeCuboidHollow

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()

# Load world slice of the build area
editor.loadWorldSlice(cache=True)

# Get heightmap
heightmap = editor.worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

x = buildArea.offset.x + 1
z = buildArea.offset.z + 1

y = heightmap[3,3] - 1

height = randint(3, 7)
depth  = randint(3, 10)

# Random floor palette
floorPalette = [
    Block("stone_bricks"),
    Block("cracked_stone_bricks"),
    Block("cobblestone"),
]

# Choose wall material
wallBlock = choice([
    Block("oak_planks"),
    Block("spruce_planks"),
    Block("white_terracotta"),
    Block("green_terracotta"),
])
print(f"Chosen wall block: {wallBlock}")

# Clear out the area
placeCuboid(editor, (x, y, z), (x+4, y+height+2, z+depth), Block("air"))

# Build main shape
placeCuboidHollow(editor, (x, y, z), (x+4, y+height, z+depth), wallBlock)
placeCuboid(editor, (x, y, z), (x+4, y, z+depth), floorPalette)

# Build roof: loop through distance from the middle
for dx in range(1, 4):
    yy = y + height + 2 - dx

    # Build row of stairs blocks
    leftBlock  = Block("oak_stairs", {"facing": "east"})
    rightBlock = Block("oak_stairs", {"facing": "west"})
    placeCuboid(editor, (x+2-dx, yy, z-1), (x+2-dx, yy, z+depth+1), leftBlock)
    placeCuboid(editor, (x+2+dx, yy, z-1), (x+2+dx, yy, z+depth+1), rightBlock)

# build the top row of the roof
yy = y + height + 1
placeCuboid(editor, (x+2, yy, z-1), (x+2, yy, z+depth+1), Block("oak_planks"))
```



## Finishing touches


It's time to put in some finishing touches. First, we'll add a door so we can
actually enter the house. For multi-block objects such as doors and beds, you
only need to place one block and the entire object will get placed. We'll also
make an adjustment to put the door at the ground level instead of the house
midpoint.

```{code-block} python
:emphasize-lines: 3, 7-12

(...)

y = heightmap[3,1] - 1

(...)

# Add a door
doorBlock = Block("oak_door", {"facing": "north", "hinge": "left"})
editor.placeBlock((x+2, y+1, z), doorBlock)

# Clear some space for the door
placeCuboid(editor, (x+1, y+1, z-1), (x+3, y+3, z-1), Block("air"))
```


Next, we'll extend the floor of the house so it integrates better on uneven
terrain. An easy and often sufficient method is to just extend it a set amount
of blocks downward.
% A more accurate way would be to use a heightmap to place only the needed
% blocks. We'll use yet another method, GDPC's replacement feature. It allows us
% to specify specific blocks to replace -- in this case, air.

```{code-block} python
:emphasize-lines: 5

(...)

# Build main shape
placeCuboidHollow(editor, (x, y, z), (x+4, y+height, z+depth), wallBlock)
placeCuboid(editor, (x, y, z), (x+4, y-5, z+depth), floorPalette)

(...)
```

Finally, we'll add some upside-down stairs blocks to the front and back of the
roof to make it look just a little nicer.

```{code-block} python
:emphasize-lines: 13-18

(...)

# Build roof: loop through distance from the middle
for dx in range(1, 4):
    yy = y + height + 2 - dx

    # Build row of stairs blocks
    leftBlock  = Block("oak_stairs", {"facing": "east"})
    rightBlock = Block("oak_stairs", {"facing": "west"})
    placeCuboid(editor, (x+2-dx, yy, z-1), (x+2-dx, yy, z+depth+1), leftBlock)
    placeCuboid(editor, (x+2+dx, yy, z-1), (x+2+dx, yy, z+depth+1), rightBlock)

    # Add upside-down accent blocks
    leftBlock  = Block("oak_stairs", {"facing": "west", "half": "top"})
    rightBlock = Block("oak_stairs", {"facing": "east", "half": "top"})
    for zz in [z-1, z+depth+1]:
        editor.placeBlock((x+2-dx+1, yy, zz), leftBlock)
        editor.placeBlock((x+2+dx-1, yy, zz), rightBlock)

(...)
```

All together:

```{code-block} python
:emphasize-lines: 18, 44, 56-61, 67-72

from random import randint, choice
from gdpc import Editor, Block
from gdpc.geometry import placeCuboid, placeCuboidHollow

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()

# Load world slice of the build area
editor.loadWorldSlice(cache=True)

# Get heightmap
heightmap = editor.worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

x = buildArea.offset.x + 1
z = buildArea.offset.z + 1

y = heightmap[3,1] - 1

height = randint(3, 7)
depth  = randint(3, 10)

# Random floor palette
floorPalette = [
    Block("stone_bricks"),
    Block("cracked_stone_bricks"),
    Block("cobblestone"),
]

# Choose wall material
wallBlock = choice([
    Block("oak_planks"),
    Block("spruce_planks"),
    Block("white_terracotta"),
    Block("green_terracotta"),
])
print(f"Chosen wall block: {wallBlock}")

# Clear out the area
placeCuboid(editor, (x, y, z), (x+4, y+height+2, z+depth), Block("air"))

# Build main shape
placeCuboidHollow(editor, (x, y, z), (x+4, y+height, z+depth), wallBlock)
placeCuboid(editor, (x, y, z), (x+4, y-5, z+depth), floorPalette)

# Build roof: loop through distance from the middle
for dx in range(1, 4):
    yy = y + height + 2 - dx

    # Build row of stairs blocks
    leftBlock  = Block("oak_stairs", {"facing": "east"})
    rightBlock = Block("oak_stairs", {"facing": "west"})
    placeCuboid(editor, (x+2-dx, yy, z-1), (x+2-dx, yy, z+depth+1), leftBlock)
    placeCuboid(editor, (x+2+dx, yy, z-1), (x+2+dx, yy, z+depth+1), rightBlock)

    # Add upside-down accent blocks
    leftBlock  = Block("oak_stairs", {"facing": "west", "half": "top"})
    rightBlock = Block("oak_stairs", {"facing": "east", "half": "top"})
    for zz in [z-1, z+depth+1]:
        editor.placeBlock((x+2-dx+1, yy, zz), leftBlock)
        editor.placeBlock((x+2+dx-1, yy, zz), rightBlock)

# build the top row of the roof
yy = y + height + 1
placeCuboid(editor, (x+2, yy, z-1), (x+2, yy, z+depth+1), Block("oak_planks"))

# Add a door
doorBlock = Block("oak_door", {"facing": "north", "hinge": "left"})
editor.placeBlock((x+2, y+1, z), doorBlock)

# Clear some space for the door
placeCuboid(editor, (x+1, y+1, z-1), (x+3, y+3, z-1), Block("air"))
```

Of course, there's lots more that we could do, such as windows, lighting and
furniture, but we'll leave that as an exercise to the reader :).


## Bonus: placing multiple houses


We've now finished the code for generating a single house, but there's one more
thing we will look at: placing multiple of them. GDPC has a very powerful,
though also complex, system for applying building logic at different locations:
the *transformation system*.

The transformation system allows you to "transform" your frame of reference
for placing blocks, so that you can always build using local coordinates instead
of global ones. The idea is based on the use of transformation matrices in
3D graphics APIs.
The system allows you to not only translate, but also rotate and flip your frame
of reference. And importantly, blocks that have an orientation (such as stairs
blocks) will get appropriately transformed as well!

- Transformation system


## Further reading

...

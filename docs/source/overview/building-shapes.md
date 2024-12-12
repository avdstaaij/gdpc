{#building-shapes}
# Building shapes






## Introduction


<!-- GDPC has a feature for this that is more performant than repeated
{meth}`.Editor.placeBlock` calls, as well as several helper functions for
building common geometrical shapes. -->


<!--  Although you could build such single-block shapes using repeated
{meth}`.Editor.placeBlock` calls,
GDPC also provides several more convenient and performant alternatives.
 -->


<!-- Although you can build anything with repeated
{meth}`.Editor.placeBlock` calls,
GDPC provides several alternatives for building single-block shapes that are more convenient and performant. -->


<!-- GDPC provides several features for building single-block shapes that are more
convenient and performant than repeated {meth}`.Editor.placeBlock` calls. -->



<!-- When using GDPC, you may commonly want to place large shapes of the same
block,
such as when constructing the walls of a building or when clearing out an area.

GDPC provides several features for building single-block shapes that are more
convenient and performant than repeated {meth}`.Editor.placeBlock` calls. -->

When using GDPC, you may commonly want to place blocks in large, regular shapes.
GDPC provides several features for building shapes that are more convenient,
and sometimes more performant, than repeated {meth}`.Editor.placeBlock` calls.



## The geometry module

<!-- When using GDPC, you may often want to place large geometrical sections of
blocks instead of placing them one by one. The {mod}`.geometry` module
contains various utility functions for this purpose.
Here are a few examples: -->


The highest-level tool for building shapes is the {mod}`.geometry` module.
It contains functions for building all kinds of common geometrical shapes.
The code snippet below shows a few examples:

<!-- The snippet below shows a few examples: -->

```{code-block} python
import numpy as np
from glm import ivec3
from gdpc import Editor, Block, geometry
from gdpc.vector_tools import addY

editor = Editor()

buildArea = editor.getBuildArea()
buildRect = buildArea.toRect()

worldSlice = editor.loadWorldSlice(buildRect)

heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
meanHeight = int(np.mean(heightmap))
groundCenter = addY(buildRect.center, meanHeight)

# Place a cuboid shape
geometry.placeCuboid(
    editor,
    groundCenter + ivec3(-3, -10, -23), # Corner 1
    groundCenter + ivec3( 4,  20, -16), # Corner 2
    Block("blue_concrete")
)

# Place a cylinder
geometry.placeFittingCylinder(
    editor,
    groundCenter + ivec3(-3, -10, -10), # Corner 1
    groundCenter + ivec3( 4,  20, -3), # Corner 2
    Block("lime_concrete")
)

# Place a diagonal line
geometry.placeLine(
    editor,
    groundCenter + ivec3(-3, 10,  3), # Endpoint 1
    groundCenter + ivec3( 4, 17, 10), # Endpoint 1
    Block("yellow_concrete"),
    width=1
)

# Place a cuboid that is striped along the Z axis (axis 2)
geometry.placeStripedCuboid(
    editor,
    groundCenter + ivec3(-3, -10, 16), # Corner 1
    groundCenter + ivec3( 4,  20, 23), # Corner 2
    Block("purple_concrete"),
    Block("magenta_concrete"),
    axis=2
)

# Place an outline around the build area
geometry.placeRectOutline(editor, buildRect, 100, Block("red_concrete"))
```

The result:

```{image} ../images/geometry-example.png
:width: 10000
```

You can find the full list of geometry functions in the
[API reference](../api/gdpc.geometry).


## Vector-generating functions

```{code-block} python
# For most of the geometry functions, it is also possible to get the points at which they place
# blocks directly. Various point-generating functions, not unlike loop2D and loop3D, can be found in
# the vector_tools module.

print("Line points:")
for point in line3D((0,0,0), (1,3,5)):
    print(tuple(point))

print("Circle points:")
for point in circle((0,0), 5):
    print(tuple(point))
```

TODO


## Efficiently building custom shapes

TODO

```{code-block} python

# It is worth noting that Editor.placeBlock() can actually be called with sequence (technically
# speaking, an Iterable) of points instead of just one. This is slightly more efficient than
# calling Editor.placeBlock() in a loop, making it a good way to define your own geometry functions.
#
# Do note that the functions from the geometry module use a few more optimization tricks, so they
# should be preferred over this method where possible.

cylinder = fittingCylinder(
    groundCenter + ivec3(-17, 15, -17),
    groundCenter + ivec3( 17, 16,  17),
    tube=True
)

editor.placeBlock(cylinder, Block("orange_concrete"))
```

```{note}
The reason why this method of building is more efficient than repeated
`placeBlock()` calls is twofold:
1. The blocks are placed using a single request to the GDMC HTTP interface.
   (Though this also happens for repeated calls if you use `Editor`'s buffering
   mode, which is explained in [Overview - Improving performance](#improving-performance).)
2. Block transformation is performed only once. (Block transformation is
   explained in [Overview - The transformation system](#the-transformation-system).)

Some functions from the `geometry` module are even more efficient, because they
transform only the shape's key points rather than all points. This is also
explained in
[Overview - The transformation system](#the-transformation-system).
```

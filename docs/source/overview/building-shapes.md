# Building shapes

## Introduction

When using GDPC, you may commonly want to place blocks in large, regular shapes.
GDPC provides several features for building shapes that are more convenient,
and often more performant, than repeated {meth}`.Editor.placeBlock` calls.



## The geometry module

```{figure} ../images/geometry-example.png
:width: 10000
Examples of shapes from the {mod}`geometry` module.
```

The highest-level tool for building shapes is the {mod}`.geometry` module.
It contains functions for building all kinds of common geometrical shapes.
The example code snippet below builds the shapes shown in the above image:

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
    groundCenter + ivec3( 4,  20,  -3), # Corner 2
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

You can find the full list of geometry functions in the
[API reference](../api/gdpc.geometry).


## Vector-generating functions

For most of the `geometry` functions, there is also a corresponding
[generator function](https://docs.python.org/3/glossary.html#term-generator)
in the {mod}`.vector_tools` module that yields the points of the shape directly
(as pyGLM vectors):

```{code-block} python
from gdpc.vector_tools import line3D

for point in line3D((0,0,0), (1,3,5)):
    print(tuple(point))

# Result:
# (0, 0, 0)
# (0, 1, 1)
# (0, 1, 2)
# (1, 2, 3)
# (1, 2, 4)
# (1, 3, 5)
```

The `vector_tools` module also contains a few 2D shape generators, such as
{func}`circle` and {func}`line2D`. For more info, see the
[API reference](../api/gdpc.vector_tools).


## Efficiently building custom single-block shapes

To build a custom single-block shape more efficiently, you can call
{meth}`.Editor.placeBlock` with an
[Iterable](https://docs.python.org/3/glossary.html#term-iterable) (e.g. a list)
of vector-likes that define the shape:

```{code-block} python
from gdpc import Editor, Block

editor = Editor()

myShape = [
    (2,100,0),
    (1,100,1),
    (3,100,1),
    (0,100,2),
    (4,100,2),
    (0,100,3),
    (2,100,3),
    (4,100,3),
    (1,100,4),
    (3,100,4)
]

editor.placeBlock(myShape, Block("red_concrete"))
```

```{tip}
To build the same shape at different locations, you could write a function that
generates the shape from a given starting point, or use GDPC's transformation
system
([Overview - The transformation system](#the-transformation-system)).
```

```{note}
The reason why this method of building is more efficient than repeated
`placeBlock()` calls is twofold:
1. The blocks are placed using a single request to the GDMC HTTP interface.
   (Though you can also gain this benefit using `Editor`'s buffering mode, which
   is explained in
   [Overview - Improving Editor performance](#improving-editor-performance).)
2. Block transformation is performed only once. (Block transformation is
   explained in
   [Overview - The transformation system](#the-transformation-system).)

Some functions from the `geometry` module are even more efficient, because they
transform only the shape's "key points" rather than all points. This is also
explained in
[Overview - The transformation system](#the-transformation-system).
```

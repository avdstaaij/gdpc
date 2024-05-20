# The transformation system

## Introduction

GDPC's most powerful feature is probably its transformation system. It is
however also one of its more complex features.

The transformation system allows you to "transform" your frame of reference
for placing blocks, so that you can always build using local coordinates instead
of global ones. The concept is based on the use of transformation matrices in
3D graphics APIs.

If you're programming, say, a house function, you could just always build the
house at (0,0,0) with its door pointing north, and then later call the function
with different transformations to place the house at any position and under any
rotation.

## The Transform class

At the core of the transformation system lies the {class}`.Transform` class,
which acts more or less like a transformation matrix. It represents a
transformation of space, or more simply, an operation to apply to vectors.
Transforms consist of three components:

- A *translation* vector (a 3D integer vector).
- A *rotation* around the Y-axis (0, 1, 2 or 3).
- A *flip* vector (a 3D boolean vector).

```python
transform = Transform((1,2,3), 1, (True, False, False))
```

The first component is translation. Applying a translation to a vector means
simply adding the translation to that vector: translating (1,2,3) by (1,1,0)
results in (2,3,3).

Transforms can be applied to vectors using the ``*`` operator or the
{meth}`.Transform.apply` method.

```python
translation = Transform((1,1,0))

vec = ivec3(1,2,3)

result = translation * vec

print(tuple(result)) # (2, 3, 3)
```

The second component is rotation around the Y-axis. Only multiples of 90 degree
rotations are supported. The options are 0 (no rotation),
1 (90 degree rotation), 2 (180 degree rotation) and 3 (270 degree rotation).
A 90 degree rotation rotates (1,0,0) to (0,0,1). In Minecraft's right-handed
coordinate system, this is clockwise.

```python
rotate1 = Transform(rotation=1)
rotate2 = Transform(rotation=2)
rotate3 = Transform(rotation=3)

vec = ivec3(1,2,3)

rotated1 = rotate1 * vec
rotated2 = rotate2 * vec
rotated3 = rotate3 * vec

print(tuple(rotated1)) # (-3, 2, 1)
print(tuple(rotated2)) # (-1, 2, -3)
print(tuple(rotated3)) # (3, 2, -1)
```

The third component is a flip/mirror vector. Flipping in an axis inverts the
sign in that axis.

```python
flipX  = Transform(flip=(True, False, False))
flipXY = Transform(flip=(True, True, False))

vec = ivec3(1,2,3)

flippedX  = flipX  * vec
flippedXY = flipXY * vec

print(tuple(flippedX))  # (-1, 2, 3)
print(tuple(flippedXY)) # (-1, -2, 3)
```

When a Transform object contains multiple components, it flips first, rotates
second and translates third.

Transforms can be composed using the `@` operator or the
{meth}`.Transform.compose` method. There is also an `@=` operator and a
corresponding {meth}`~.Transform.push` method. Note that transformations are
not commutative: the order in which you compose them matters.

```python
# Rotate first, then translate
t1 = Transform(translation=(1,1,1)) @ Transform(rotation=1)

# Translate first, then rotate
t2 = Transform(rotation=1) @ Transform(translation=(1,1,1))

print(t1) # translation=(1, 1, 1), rotation=1, flip=(False, False, False)
print(t2) # translation=(-1, 1, 1), rotation=1, flip=(False, False, False)
```

The Transform class supports various other math operations. See the reference
for {class}`.Transform` for more info.


## Editor.transform

{class}`.Editor` objects have a {attr}`~.Editor.transform` attribute that
represents that editor's "point of view". It is applied to all block placement
and retrieval positions. You can modify this transform to change your local
coordinate system.

A basic usage of Editor.transform is to translate to the build area. Here, we
translate only in the XZ plane.

```python
buildArea = editor.getBuildArea()
buildRect = buildArea.toRect()

editor.transform @= Transform(translation=addY(buildRect.offset))
```

Now, when you place a block at (1,100,1), you place it at the *local* (1,100,1)
position. If the build area started at X=10, Z=20, this would be the
global position (11,100,21).

```python
position = (1,100,1)

print(tuple(buildRect.offset)) # (10, 20)
print(tuple(editor.transform * position)) # (11, 100, 21)

# Place a block at local position (10, 100, 20) / global position (11, 100, 21)
editor.placeBlock(position, Block("red_concrete"))
```

Note that this carries over to all functions that use the editor to get or
place blocks, including, for example, all geometry functions.

```python
from gdpc.geometry import placeBox
placeBox(editor, Box((1,100,3), (3,3,3)), Block("blue_concrete"))
```

The main application of {attr}`.Editor.transform` is to build a structure
defined in local coordinates at any position.

```python
# Define a staircase function. Note that no position argument is needed.
def buildStaircase(editor):
    """Build a 3x3x3 staircase."""
	baseBlock  = Block("cobblestone")
	stairBlock = Block("oak_stairs", {"facing": "south"})
    for z in range(3):
        for y in range(z):
            placeBox(editor, Box((0,y,z), (3,1,1)), baseBlock)
        placeBox(editor, Box((0,z,z), (3,1,1)), stairBlock)

# Build the staircase at local coordinates (5,100,1).
# Notice how we're stacking two "local coordinate systems" on top of each other.
transform = Transform((5,100,1))
editor.transform.push(transform) # Transform.push() is equivalent to @=
buildStaircase(editor)
editor.transform.pop(transform)  # Transform.pop() reverses Transform.push()
```

The pattern of pushing a transform, doing something and then popping it off
again is very common, so there is a context manager to make it easier.

{meth}`.Editor.pushTransform` creates a context that reverts all changes to the
Editor's transform on exit.
```python
with editor.pushTransform():
    editor.transform @= Transform((5,100,5))
    buildStaircase(editor)
```

If you pass a Transform object as argument, it is pushed to Editor.transform on
entry.
```python
with editor.pushTransform(Transform((5,100,9))):
    buildStaircase(editor)
```

On top of that, since it is also very common to use Transforms that only
translate, you can also pass a vector to Editor.pushTransform() directly, which
will be interpreted as a translation.
```python
with editor.pushTransform((5,100,13)):
    buildStaircase(editor)
```

Of course, translating points is fairly easy. You could also just give
`buildStairs()` a position parameter and always work with global coordinates.
However, things are not so easy when you want to rotate or flip a structure. The
reason is that, in Minecraft, sometimes *individual blocks* need to be rotated
or flipped as well. Certain blocks, such as stairs, have an orientation that
needs to be modified. These orientations are usually stored in block states.

GDPC's transformation system can automatically deal with most of these
oriented blocks.

```python
# Build the staircase at "(9,100,1)", but rotated. Notice how the stairs blocks
# are rotated as well.
with editor.pushTransform(Transform((9,100,1+2), rotation=3)):
    buildStaircase(editor)

# Build the staircase at "(9,100,5)", but flipped.
with editor.pushTransform(Transform((9,100,5+2), flip=(False, False, True))):
    buildStaircase(editor)
```

When using a rotating or flipping transform, note that structures will extend in
a different direction. For example, a structure extending to positive Z will
extend to negative Z when flipped in the Z-axis. This is why there are
correcting +2's in the translations of the previous transforms.

GDPC's {mod}`.transform` module contains some helper functions that perform these
corrections for you.

```python
# Build the staircase at (9,100,9), but rotated.
transform = rotatedBoxTransform(Box((9,100,9), (3,3,3)), 1)
with editor.pushTransform(transform):
    buildStaircase(editor)

# Build the staircase at (9,100,13), but flipped.
transform = flippedBoxTransform(Box((9,100,13), (3,3,3)), (False, False, True))
with editor.pushTransform(transform):
    buildStaircase(editor)

# Build a checkerboard-patterned floor under all structures so you can more
# easily count blocks.
placeCheckeredBox(
    editor,
    Box((0,99,0), (13,1,17)),
    Block("gray_concrete"), Block("light_gray_concrete")
)
```


## Final notes

You can also transform an individual Block manually, which may sometimes be
useful.

```python
block = Block("oak_stairs", {"facing": "north"})
block = block.transformed(rotation=1)
print(f"\nRotated block 1: {block}") # oak_stairs[facing=east]
```

A final thing to keep in mind is that the transformation system can only
transform oriented blocks if you explicitly specify the orientation. If you
simply create stairs block without specifying a facing value, Minecraft assigns
a default one ("north" in this case) on placement. However, GDPC's
transformation system does not see or modify this default value. This limitation
might be resolved in a future version.

```python
block = Block("oak_stairs") # No facing value specified.
block = block.transformed(rotation=1)
print(block) # oak_stairs - Still no facing value, so the default is still used.
```

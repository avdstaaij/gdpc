{#vectors}
# Vectors

## Vectors in GDPC

Many functions in GDPC deal with positions or directions in 2D or 3D space,
either as parameters or as return values. Rather than using separate X, Y and Z
numbers for these purposes, GDPC uses *vectors*: single objects that describe
a 2D or 3D point.

<!--
Although GDPC has tools for vector math, which we will describe further below,
you do not need to know any vector math to use the library. All you need to know
is how to pass vectors to GDPC and how it returns them. -->

### Vectors as parameters

An example of a function with a vector parameter is `Editor.placeBlock()`.
Its first parameter, `position`, should be set to a single object that
represents a 3D vector. For example, the call below places a block at
`X=0`, `Y=80`, `Z=0`:

<!-- Instead of having separate `x`, `y` and `z` parameters, it has a single
`position` parameter that should be set to an object that represents a 3D
vector. For example, the call below places a block at `X=0`, `Y=80`, `Z=0`: -->


<!-- In the `Editor.placeBlock()` call below, `(0,80,0)` is an example a 3D vector.
It describes the position `X=0`, `Y=80`, `Z=0`. -->

```python
editor.placeBlock((0,80,0), Block("stone"))
```

<!-- In this case, we used the Python tuple `(0,80,0)` to represent a vector.
However, GDPC actually accepts any object that "behaves" like a vector as
arguments to its functions. This means that the following calls all work: -->

GDPC accepts any object that "behaves" like a vector as arguments to its
functions. This means that the following calls all work:

```python
editor.placeBlock((0,80,0),           Block("stone"))
editor.placeBlock([0,80,0],           Block("stone"))
editor.placeBlock(np.array([0,80,0]), Block("stone"))
```

GDPC refers to objects that "behave" like a vector as *vector-likes*. Depending
on the function, a different kind of vector-like may be needed.
The required type of vector-likes for vector parameters is documented via type
hints, which you can view in the [API reference](../api/index). There are
currently four types:

- {class}`.Vec2iLike` - A vector-like of two integers.

- {class}`.Vec3iLike` - A vector-like of three integers.

- {class}`.Vec2bLike` - A vector-like of two booleans

- {class}`.Vec3bLike` - A vector-like of three booleans.

The exact requirements for an object `vec` to be considered a vector-like are
as follows:
<!-- An object `vec` has to meet the following requirements to be a vector-like: -->

- Its elements must be accessible via indexing: {python}`y = vec[1]`.
- Its elements must be accessible via iteration: {python}`for component in vec:`
- Its length must be gettable: {python}`length = len(vec)`.
- It must have the correct length (depends on the type).
- Its elements must have the correct type (depends on the type).

If you pass a vector-like with elements of the wrong type, such as a vector of
floats where is vector of integers is needed, the elements will be converted to
the correct type. Passing a vector of the wrong length usually results in an
exception.

```{note}
The motivation behind the vector-like system in GDPC, is that it allows you to
make use of specialized vector classes (such as those from
[numpy](https://numpy.org/),
[pygame](https://www.pygame.org) or
[pyGLM](https://pypi.org/project/PyGLM/)
),
while imposing as few requirements as possible, and still allowing you to pass
separate `x`/`y`/`z` numbers with just slightly more syntax.
Many libraries define their own vector types, but GDPC allows you to use
whichever you like.
```

### Vectors as return values

When a GDPC function returns a vector, it always returns a vector class from the
[pyGLM](https://pypi.org/project/PyGLM/) package.
These vectors support vector math operators, which can often simplify code, and
have handy `.x`, `.y` and `.z` attributes. PyGLM also provides many performant
vector math functions. Refer to the
[pyGLM documentation](https://pypi.org/project/PyGLM/) for more details.
Here is a small example of the syntax:

<!-- TODO: mention pyGLM vector math functions -->

```python
from glm import ivec3

v1 = ivec3(1,2,3)
v2 = ivec3(1,0,1)

print(v1.x) # 1

sum_v = v1 + v2
print(sum_v) # ivec3(2,2,4)

scaled_v = 2 * v1
print(scaled_v) # ivec3(2,4,6)
```

The pyGLM vectors fulfill the requirements to be vector-likes, so you can
pass them right back to GDPC.

If you prefer to work with separate `x`, `y` and `z` variables, you can always
"unpack" any returned pyGLM vectors:

```python
vec = ivec3(1,2,3)
x, y, z = vec
```

You can also convert pyGLM vectors to tuples with `tuple()`. This can be useful
if you want to index a numpy array with a pyGLM vector or if you want a cleaner
`print()` output.

```python
vec = ivec3(1,2,3)

array = np.zeros((5,5,5))
array[tuple(vec)] = 1 # Set array[1,2,3] to 1.

print(tuple(vec)) # (1,2,3)
```


## Vector tools

GDPC provides various vector utilities in the {mod}`.vector_tools` module.
Like all GDPC functions, you can call them with any vector-like type, though
they will always return pyGLM vectors.

There are four categories of vector utilities:
*constants*, *general vector utilities*, *the Rect and Box classes*, and
*shape-generating functions*. We will summarize and give some examples for each
category.

### Constants

The {mod}`.vector_tools` module contains various vector constants
(all pyGLM vectors) that may simplify computations. For example:

```python
from glm import ivec3
from gdpc.vector_tools import SOUTH, Y, XZ

pos = ivec3(0,0,0)
pos = pos + 1 * SOUTH + 2 * Y + 3 * XZ
print(pos) # ivec3(3,2,4)
```

### General utilities

The {mod}`.vector_tools` module contains lots of general vector manipulation
utilities. For example:

```python
from glm import ivec2, ivec3
from gdpc.vector_tools import addY, dropY, perpendicular, toAxisVector2D

# addY() turns a 2D vector into a 3D one by adding a Y component.
vec = ivec2(1,3)
vec = addY(vec, 2)
print(vec) # ivec3(1,2,3)

# dropY() does the reverse.
vec = ivec3(4,5,6)
vec = dropY(vec)
print(vec) # ivec2(4,6)

# perpendicular() returns a vector that is perpendicular to the given one.
vec = perpendicular((1,0))
print(vec) # ivec2(0,-1)

# toAxisVector2D() returns the axis-aligned vector closest to the given one.
vec = toAxisVector2D((11,2))
print(vec) # ivec2(1,0)
```

### Rect and Box

The {mod}`.vector_tools` module contains the {class}`.Rect` and {class}`.Box`
classes.
A `Rect` represents a 2D rectangle, defined by and offset and a size (both 2D
vectors), and a `Box` is the analogue in 3D. There are several GDPC functions
that take a `Rect` or `Box` as parameter or return one.

Here is an example that shows some of `Rect`'s features (`Box` works the same):

```python
from gdpc.vector_tools import Rect

rect = Rect((1,2), (5,5)) # offset = (1,2), size = (5,5)

print(rect.offset) # ivec2(1,2)
print(rect.size)   # ivec2(5,5)
print(rect.end)    # ivec2(6,7)
print(rect.center) # ivec2(3,4)
print(rect.area)   # 25

print(rect.contains((3,3))) # True

# Loop through all internal points
for vec in rect:
   print(vec) # ivec2(1,2), ivec2(1,3), ..., ivec2(5,6)

# Create a rect with the given corners
rect = Rect.between((1,5), (3,2))
print(rect) # Rect((1,2), (3,4))

# Create a rect containing the given points
rect = Rect.bounding([(1,1), (1,3), (2,2)])
print(rect) # Rect((1,1), (2,3))
```

### Shape-generating functions

Finally, the {mod}`.vector_tools` module contains several functions that
generate the points of a geometric shape. For example:

```python
from gdpc.vector_tools import loop3D, line3D, circle

# loop3D() loops over a 3D box defined by a begin and an end.
# It's essentially a 3D variant of python's built-in range() function.
for vec in loop3D((1,2,3), (5,5,5)):
   print(vec) # ivec3(1,2,3), ivec3(1,2,4), ivec3(1,3,3), ..., ivec3(4,4,4)

# line3D generates the points of a 3D line defined by two endpoints (inclusive).
for vec in line3D((1,2,3), (5,5,5)):
   print(vec) # ivec3(1,2,3), ivec3(2,3,4), ivec3(3,4,4), ivec3(4,4,4), ivec3(5,5,5)

# circle() generates the points of a 2D circle defined by a center and diameter.
for vec in circle((5,5), 5):
   print(vec) # ivec2(7,4), ivec2(7,5), ivec2(7,6), ivec2(6,7), ...
```

```{note}
For *building* geometrical shapes, see
[Overview - Building shapes](#building-shapes).
```

{#minecrafts-coordinate-system}
## Minecraft's coordinate system

When working with vectors in the context of a Minecraft world, you should be
aware that Minecraft's coordinate system has some unusual properties:

1. Minecraft's coordinate system is right-handed with Y pointing up.
   This means that, when facing towards the positive Z direction, the positive X
   direction points to the *left*, not to the right. If you use GDPC to build a
   structure while assuming that Z points forward and X points to the right,
   this may cause the structure to be a mirrored version of what you intended.

2. Minecraft performs rotations in what is normally considered the *left-handed*
   way, even though its coordinate system is right-handed. That is, things like
   sign rotations or the command `/execute rotated` rotate from positive X
   towards positive Z. All GDPC functions that perform some kind of rotation,
   such as {func}`.rotate3D`, follow Minecraft's convention.

<!-- TODO: Image -->

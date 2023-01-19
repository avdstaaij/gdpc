"""Various vector utilities"""


from typing import Any, Iterable, List, Optional, Set, Tuple, Union, overload
from dataclasses import dataclass, field
import math

from more_itertools import powerset
import numpy as np
from scipy import ndimage
import skimage.segmentation
import glm
from glm import ivec2, ivec3, vec2, vec3, bvec2, bvec3

from .utility import non_zero_sign


# ==================================================================================================
# General
# ==================================================================================================


UP    = ivec3( 0, 1, 0)
DOWN  = ivec3( 0,-1, 0)
EAST  = ivec3( 1, 0, 0)
WEST  = ivec3(-1, 0, 0)
NORTH = ivec3( 0, 0,-1)
SOUTH = ivec3( 0, 0, 1)
X     = ivec3( 1, 0, 0)
Y     = ivec3( 0, 1, 0)
Z     = ivec3( 0, 0, 1)
XY    = ivec3( 1, 1, 0)
XZ    = ivec3( 1, 0, 1)
YZ    = ivec3( 0, 1, 1)
XYZ   = ivec3( 1, 1, 1)

DIAGONALS_2D = (
    ivec2( 1,  1),
    ivec2( 1, -1),
    ivec2(-1,  1),
    ivec2(-1, -1),
)

DIAGONALS_3D = (
    ivec3( 1,  1,  0),
    ivec3( 1,  0,  1),
    ivec3( 0,  1,  1),
    ivec3( 1, -1,  0),
    ivec3( 1,  0, -1),
    ivec3( 0,  1, -1),
    ivec3(-1,  1,  0),
    ivec3(-1,  0,  1),
    ivec3( 0, -1,  1),
    ivec3(-1, -1,  0),
    ivec3(-1,  0, -1),
    ivec3( 0, -1, -1),
    ivec3( 1,  1,  1),
    ivec3( 1,  1, -1),
    ivec3( 1, -1,  1),
    ivec3(-1,  1,  1),
    ivec3( 1, -1, -1),
    ivec3(-1, -1,  1),
    ivec3(-1,  1, -1),
    ivec3(-1, -1, -1),
)


@overload
def dropDimension(vec: vec3, dimension: int) -> vec2: ...
@overload
def dropDimension(vec: ivec3, dimension: int) -> ivec2: ...
@overload
def dropDimension(vec: bvec3, dimension: int) -> bvec2: ...

def dropDimension(vec, dimension):
    """Returns <vec> without its <dimension>-th component"""
    if dimension == 0: return vec.yz
    if dimension == 1: return vec.xz
    if dimension == 2: return vec.xy
    raise ValueError(f'Invalid dimension "{dimension}"')


@overload
def addDimension(vec: vec2, dimension: int, value: float=0) -> vec3: ...
@overload
def addDimension(vec: ivec2, dimension: int, value: int=0) -> ivec3: ...
@overload
def addDimension(vec: bvec2, dimension: int, value: bool=0) -> bvec3: ...

def addDimension(vec, dimension, value=0):
    """Inserts <value> into <vec> at <dimension> and returns the resulting 3D vector"""
    l = list(vec)
    if isinstance(l[1], float): return  vec3(*l[:dimension], value, *l[dimension:])
    if isinstance(l[0], int):   return ivec3(*l[:dimension], value, *l[dimension:])
    if isinstance(l[0], bool):  return bvec3(*l[:dimension], value, *l[dimension:])
    raise TypeError("<vec> has in invalid type.")


@overload
def dropY(vec: vec3) -> vec2: ...
@overload
def dropY(vec: ivec3) -> ivec2: ...
@overload
def dropY(vec: bvec3) -> bvec2: ...

def dropY(vec):
    """Returns [vec] without its y-component (i.e., projected on the XZ-plane)"""
    return vec.xz


@overload
def addY(vec: vec2, y: float) -> vec3: ...
@overload
def addY(vec: ivec2, y: int) -> ivec3: ...
@overload
def addY(vec: bvec2, y: bool) -> bvec3: ...

def addY(vec, y=0):
    """Returns a 3D vector (vec.x, y, vec.y)"""
    return ivec3(vec.x, y, vec.y)


@overload
def setY(vec: vec3, y: float) -> vec3: ...
@overload
def setY(vec: ivec3, y: int) -> ivec3: ...
@overload
def setY(vec: bvec3, y: bool) -> bvec3: ...

def setY(vec, y=0):
    """Returns [vec] with its y-component set to [y]"""
    return ivec3(vec.x, y, vec.z)


@overload
def trueMod(vec: vec2, modulus: float) -> vec2: ...
@overload
def trueMod(vec: ivec2, modulus: int) -> ivec2: ...
@overload
def trueMod(vec: vec3, modulus: float) -> vec3: ...
@overload
def trueMod(vec: ivec3, modulus: int) -> ivec3: ...

def trueMod(vec, modulus):
    """Returns the true value of <v> modulo <modulus>, as opposed to <v> % <modulus> which may yield
    negative numbers."""
    result = vec % modulus
    for i in range(len(result)): # pylint: disable=consider-using-enumerate
        if result[i] < 0:
            result[i] += modulus
    return result


@overload
def perpendicular(vec: vec2) -> vec2: ...
@overload
def perpendicular(vec: ivec2) -> ivec2: ...

def perpendicular(vec):
    """Returns the vector perpendicular to [vec] that points to the right of [vec] and has the same
    length as [vec]."""
    if isinstance(vec,  vec2): return  vec2(vec.y, -vec.x)
    if isinstance(vec, ivec2): return ivec2(vec.y, -vec.x)
    raise ValueError()


def rotate(vec: ivec2, rotation: int):
    """Returns [vec], rotated by [rotation]"""
    if rotation == 0: return vec
    if rotation == 1: return ivec2(-vec.y,  vec.x)
    if rotation == 2: return ivec2(-vec.x, -vec.y)
    if rotation == 3: return ivec2( vec.y, -vec.x)
    raise ValueError("Rotation must be in {0,1,2,3}")


def rotateXZ(vec: ivec3, rotation: int):
    """Returns [vec], rotated in the XZ-plane by [rotation]"""
    return addY(rotate(dropY(vec), rotation), vec.y)


def flipRotation(rotation: int, flip: bvec2):
    """Returns rotation such that applying rotation after <flip> is equivalent to applying <flip>
    after <rotation>."""
    scale = flipToScale2D(flip)
    return (rotation * scale.x * scale.y + 4) % 4

def flipRotationXZ(rotation: int, flip: bvec3):
    """Returns rotation such that applying rotation after <flip> is equivalent to applying <flip>
    after <rotation>"""
    return flipRotation(rotation, dropY(flip))


def rotateSize(size: ivec2, rotation: int):
    """Returns the effective size of a rect of size [size] that has been rotated by [rotation]."""
    return ivec2(size.y, size.x) if rotation in [1, 3] else size


def rotateSizeXZ(size: ivec3, rotation: int):
    """Returns the effective size of a box of size [size] that has been rotated by [rotation]."""
    return addY(rotateSize(dropY(size), rotation), size.y)


def flipToScale2D(flip: bvec2):
    """Returns a vector with a 1 where <flip> is false, and -1 where <flip> is true"""
    return 1 - 2*ivec2(flip)

def flipToScale3D(flip: bvec3):
    """Returns a vector with a 1 where <flip> is false, and -1 where <flip> is true"""
    return 1 - 2*ivec3(flip)


def scaleToFlip2D(scale: ivec2):
    """Returns whether [scale] flips space in each axis"""
    return bvec2(scale.x < 0, scale.y < 0)

def scaleToFlip3D(scale: ivec3):
    """Returns whether [scale] flips space in each axis"""
    return bvec3(scale.x < 0, scale.y < 0, scale.z < 0)


def toAxisVector(vec: ivec2):
    """Returns the axis-aligned unit vector closest to [vec]"""
    if abs(vec.x) > abs(vec.y): # pylint: disable=no-else-return
        return ivec2(non_zero_sign(vec.x), 0)
    else:
        return ivec2(0, non_zero_sign(vec.y))


def directionToRotation(direction: ivec2):
    """Returns the rotation that rotates (0,-1) closest to [direction]"""
    vec = toAxisVector(direction)
    if vec.y < 0: return 0
    if vec.x > 0: return 1
    if vec.y > 0: return 2
    if vec.x < 0: return 3
    raise ValueError()


# For some reason, glm's length, length2, distance, distance2 and l1Norm refuse to work with integer
# vectors. We provide some wrappers.

def length(vec: Union[ivec2, ivec3]):
    """Returns the length of [vec]"""
    if isinstance(vec, ivec2): return glm.length(vec2(vec))
    if isinstance(vec, ivec3): return glm.length(vec3(vec))
    raise ValueError()

def length2(vec: Union[ivec2, ivec3]):
    """Returns the squared length of [vec]"""
    if isinstance(vec, ivec2): return int(glm.length2(vec2(vec)))
    if isinstance(vec, ivec3): return int(glm.length2(vec3(vec)))
    raise ValueError()

def distance(vecA: Union[ivec2, ivec3], vecB: Union[ivec2, ivec3]) -> float:
    """Returns the distance between [vecA] and [vecB]"""
    if isinstance(vecA, ivec2) and isinstance(vecB, ivec2): return glm.distance(vec2(vecA), vec2(vecB))
    if isinstance(vecA, ivec3) and isinstance(vecB, ivec2): return glm.distance(vec3(vecA), vec3(vecB))
    raise ValueError()

def distance2(vecA: Union[ivec2, ivec3], vecB: Union[ivec2, ivec3]):
    """Returns the squared distance between [vecA] and [vecB]"""
    if isinstance(vecA, ivec2) and isinstance(vecB, ivec2): return int(glm.distance2(vec2(vecA), vec2(vecB)))
    if isinstance(vecA, ivec3) and isinstance(vecB, ivec2): return int(glm.distance2(vec3(vecA), vec3(vecB)))
    raise ValueError()

def l1Norm(vec: Union[ivec2, ivec3]):
    """Returns the L1 norm of [vec]"""
    if isinstance(vec, ivec2): return abs(vec.x) + abs(vec.y)
    if isinstance(vec, ivec3): return abs(vec.x) + abs(vec.y) + abs(vec.z)
    raise ValueError()

def l1Distance(vecA: Union[ivec2, ivec3], vecB: Union[ivec2, ivec3]):
    """Returns the L1 norm distance between [vecA] and [vecB]"""
    return l1Norm(vecA - vecB)


def orderedCorners2D(corner1: ivec2, corner2: ivec2):
    """Returns two corners of the rectangle defined by <corner1> and <corner2>, such that the first
    corner is smaller than the second corner in each axis"""
    return (
        ivec2(
            corner1.x if corner1.x <= corner2.x else corner2.x,
            corner1.y if corner1.y <= corner2.y else corner2.y,
        ),
        ivec2(
            corner1.x if corner1.x > corner2.x else corner2.x,
            corner1.y if corner1.y > corner2.y else corner2.y,
        )
    )


def orderedCorners3D(corner1: ivec3, corner2: ivec3):
    """Returns two corners of the box defined by <corner1> and <corner2>, such that the first
    corner is smaller than the second corner in each axis"""
    return (
        ivec3(
            corner1.x if corner1.x <= corner2.x else corner2.x,
            corner1.y if corner1.y <= corner2.y else corner2.y,
            corner1.z if corner1.z <= corner2.z else corner2.z,
        ),
        ivec3(
            corner1.x if corner1.x > corner2.x else corner2.x,
            corner1.y if corner1.y > corner2.y else corner2.y,
            corner1.z if corner1.z > corner2.z else corner2.z,
        )
    )


def getDimensionality(corner1: Union[ivec2, ivec3], corner2: Union[ivec2, ivec3]) -> Tuple[int, List[str]]:
    """Determines the number of dimensions for which <corner1> and <corner2> are in general
    position, i.e. the number of dimensions for which the volume they define is not flat.\n
    Returns (dimensionality, list of indices of dimensions for which the volume is flat).
    For example: (2, [0,2]) means that the volume is flat in the x and z axes."""
    difference = np.array(corner1) - np.array(corner2)
    flatSides = np.argwhere(difference == 0).flatten()
    return len(corner1) - np.sum(flatSides), list(flatSides)


# ==================================================================================================
# Rect and Box
# ==================================================================================================


# TODO: If someone knows how to fix the duplication in Rect and Box, please do tell.


@dataclass
class Rect:
    """A rectangle, defined by an offset and a size"""

    offset: ivec2 = field(default_factory=ivec2)
    size:   ivec2 = field(default_factory=ivec2)

    @property
    def begin(self):
        """Equivalent to self.offset. Setting will modify self.offset."""
        return self.offset

    @begin.setter
    def begin(self, value: ivec2):
        self.offset = value

    @property
    def end(self):
        """Equivalent to self.offset + self.size. Setting will modify self.size."""
        return self.begin + self.size

    @end.setter
    def end(self, value: ivec2):
        self.size = value - self.begin

    @property
    def middle(self):
        """This Rect's middle point, rounded down"""
        return (self.begin + self.size) // 2

    @property
    def inner(self):
        """Yields all points contained in this Rect"""
        return (
            ivec2(x, y)
            for x in range(self.begin.x, self.end.x)
            for y in range(self.begin.y, self.end.y)
        )

    @property
    def area(self):
        """This Rect's surface area"""
        return self.size.x*self.size.y

    @property
    def corners(self):
        """Yields this Rect's corner points"""
        return (
            self.offset + sum(subset)
            for subset in powerset([ivec2(self.size.x, 0), ivec2(0, self.size.y)])
        )

    def contains(self, vec: ivec2):
        """Returns whether this Rect contains [vec]"""
        return (
            self.begin.x <= vec.x < self.end.x and
            self.begin.y <= vec.y < self.end.y
        )

    def collides(self, other: 'Rect'):
        """Returns whether this Rect and [other] have any overlap"""
        return (
            self.begin.x <= other.end  .x and
            self.end  .x >= other.begin.x and
            self.begin.y <= other.end  .y and
            self.end  .y >= other.begin.y
        )

    def squaredDistanceToVec(self, vec: ivec2):
        """Returns the squared distance between this Rect and [vec]"""
        dx = max(self.begin.x - vec.x, 0, vec.x - (self.end.x - 1))
        dy = max(self.begin.y - vec.y, 0, vec.y - (self.end.y - 1))
        return dx*dx + dy*dy

    def distanceToVec(self, vec: ivec2):
        """Returns the distance between this Rect and [vec]"""
        return math.sqrt(self.squaredDistanceToVec(vec))

    def translated(self, translation: Union[ivec2, int]):
        """Returns a copy of this Rect, translated by [translation]"""
        return Rect(self.offset + translation, self.size)

    def dilate(self, dilation: int = 1):
        """Morphologically dilates this rect by [dilation]"""
        self.offset -= dilation
        self.size   += dilation*2

    def dilated(self, dilation: int = 1):
        """Returns a copy of this Rect, morphologically dilated by [dilation]"""
        return Rect(self.offset - dilation, self.size + dilation*2)

    def erode(self, erosion: int = 1):
        """Morphologically erodes this rect by [erosion]"""
        self.dilate(-erosion)

    def eroded(self, erosion: int = 1):
        """Returns a copy of this Rect, morphologically eroded by [erosion]"""
        return self.dilated(-erosion)

    def centeredSubRectOffset(self, size: ivec2):
        """Returns an offset such that Rect(offset, [size]).middle == self.middle"""
        difference = self.size - size
        return self.offset + difference/2

    def centeredSubRect(self, size: ivec2):
        """Returns a rect of size [size] with the same middle as this rect"""
        return Rect(self.centeredSubRectOffset(size), size)

    @staticmethod
    def between(cornerA: ivec2, cornerB: ivec2):
        """Returns the Rect between [cornerA] and [cornerB] (inclusive),
        which may be any opposing corners."""
        first, last = orderedCorners2D(cornerA, cornerB)
        return Rect(first, (last - first) + 1)

    @staticmethod
    def bounding(points: Iterable[ivec2]):
        """Returns the smallest Rect containing all [points]"""
        pointArray = np.array(points)
        minPoint = np.min(pointArray, axis=0)
        maxPoint = np.max(pointArray, axis=0)
        return Rect(minPoint, maxPoint - minPoint + 1)

    def toBox(self, offsetY = 0, sizeY = 0):
        """Returns a corresponding Box"""
        return Box(addY(self.offset, offsetY), addY(self.size, sizeY))

    @property
    def outline(self):
        """Yields this Rect's outline points"""
        # It's surprisingly difficult to get this right without duplicates. (Think of the corners!)
        first = self.begin
        last  = self.end - 1
        yield from loop2D(ivec2(first.x, first.y), ivec2(last.x  -1, first.y   ) + 1)
        yield from loop2D(ivec2(last.x,  first.y), ivec2(last.x,     last.y  -1) + 1)
        yield from loop2D(ivec2(last.x,  last.y),  ivec2(first.x +1, last.y    ) - 1)
        yield from loop2D(ivec2(first.x, last.y),  ivec2(first.x,    first.y +1) - 1)


@dataclass()
class Box:
    """A box, defined by an offset and a size"""

    offset: ivec3 = field(default_factory=ivec3)
    size:   ivec3 = field(default_factory=ivec3)

    @property
    def begin(self):
        """Equivalent to self.offset. Setting will modify self.offset."""
        return self.offset

    @begin.setter
    def begin(self, value: ivec2):
        self.offset = value

    @property
    def end(self):
        """Equivalent to self.offset + self.size. Setting will modify self.size."""
        return self.begin + self.size

    @end.setter
    def end(self, value: ivec2):
        self.size = value - self.begin

    @property
    def middle(self):
        """This Box's middle point, rounded down"""
        return (self.begin + self.size) // 2

    @property
    def inner(self):
        """Yields all points contained in this Box"""
        return (
            ivec3(x, y, z)
            for x in range(self.begin.x, self.end.x)
            for y in range(self.begin.y, self.end.y)
            for z in range(self.begin.z, self.end.z)
        )

    @property
    def volume(self):
        """This Box's volume"""
        return self.size.x*self.size.y*self.size.z

    @property
    def corners(self):
        """Yields this Box's corner points"""
        return [
            self.offset + sum(subset)
            for subset in powerset([ivec3(self.size.x, 0, 0), ivec3(0, self.size.y, 0), ivec3(0, 0, self.size.z)])
        ]

    def contains(self, vec: ivec3):
        """Returns whether this Box contains [vec]"""
        return (
            self.begin.x <= vec.x < self.end.x and
            self.begin.y <= vec.y < self.end.y and
            self.begin.z <= vec.z < self.end.z
        )

    def collides(self, other: 'Box'):
        """Returns whether this Box and [other] have any overlap"""
        return (
            self.begin.x <= other.end  .x and
            self.end  .x >= other.begin.x and
            self.begin.y <= other.end  .y and
            self.end  .y >= other.begin.y and
            self.begin.z <= other.end  .z and
            self.end  .z >= other.begin.z
        )

    def squaredDistanceToVec(self, vec: ivec3):
        """Returns the squared distance between this Box and [vec]"""
        dx = max(self.begin.x - vec.x, 0, vec.x - (self.end.x - 1))
        dy = max(self.begin.y - vec.y, 0, vec.y - (self.end.y - 1))
        dz = max(self.begin.z - vec.z, 0, vec.z - (self.end.z - 1))
        return dx*dx + dy*dy + dz*dz

    def distanceToVec(self, vec: ivec3):
        """Returns the distance between this Box and [vec]"""
        return math.sqrt(self.squaredDistanceToVec(vec))

    def translated(self, translation: Union[ivec3, int]):
        """Returns a copy of this Box, translated by [translation]"""
        return Box(self.offset + translation, self.size)

    def dilate(self, dilation: int = 1):
        """Morphologically dilates this box by [dilation]"""
        self.offset -= dilation
        self.size   += dilation*2

    def dilated(self, dilation: int = 1):
        """Returns a copy of this Box, morphologically dilated by [dilation]"""
        return Rect(self.offset - dilation, self.size + dilation*2)

    def erode(self, erosion: int = 1):
        """Morphologically erodes this box by [erosion]"""
        self.dilate(-erosion)

    def eroded(self, erosion: int = 1):
        """Returns a copy of this Box, morphologically eroded by [erosion]"""
        return self.dilated(-erosion)

    def centeredSubBoxOffset(self, size: ivec2):
        """Returns an offset such that Box(offset, [size]).middle == self.middle"""
        difference = self.size - size
        return self.offset + difference/2

    def centeredSubBox(self, size: ivec2):
        """Returns an box of size [size] with the same middle as this box"""
        return Box(self.centeredSubBoxOffset(size), size)

    @staticmethod
    def between(cornerA: ivec3, cornerB: ivec3):
        """Returns the Box between [cornerA] and [cornerB] (both inclusive),
        which may be any opposing corners"""
        first, last = orderedCorners3D(cornerA, cornerB)
        return Box(first, last - first + 1)

    @staticmethod
    def bounding(points: Iterable[ivec3]):
        """Returns the smallest Box containing all [points]"""
        pointArray = np.array(points)
        minPoint = np.min(pointArray, axis=0)
        maxPoint = np.max(pointArray, axis=0)
        return Rect(minPoint, maxPoint - minPoint + 1)

    def toRect(self):
        """Returns this Box's XZ-plane as a Rect"""
        return Rect(dropY(self.offset), dropY(self.size))

    @property
    def shell(self):
        """Yields all points on this Box's surface"""
        # It's surprisingly difficult to get this right without duplicates. (Think of the corners!)
        first = self.begin
        last  = self.end - 1
        # Bottom face
        yield from loop3D(ivec3(first.x, first.y, first.z), ivec3(last.x, first.y, last.z) + 1)
        # Top face
        yield from loop3D(ivec3(first.x, last.y, first.z), ivec3(last.x, last.y, last.z) + 1)
        # Sides
        yield from loop3D(ivec3(first.x, first.y+1, first.z), ivec3(last.x -1,  last.y-1, first.z   ) + 1)
        yield from loop3D(ivec3(last.x,  first.y+1, first.z), ivec3(last.x,     last.y-1, last.z  -1) + 1)
        yield from loop3D(ivec3(last.x,  first.y+1, last.z ), ivec3(first.x +1, last.y+1, last.z    ) - 1)
        yield from loop3D(ivec3(first.x, first.y+1, last.z ), ivec3(first.x,    last.y+1, first.z +1) - 1)

    @property
    def wireframe(self):
        """Yields all points on this Box's edges"""
        # It's surprisingly difficult to get this right without duplicates. (Think of the corners!)
        first = self.begin
        last  = self.end - 1
        # Bottom face
        yield from loop3D(ivec3(first.x, first.y, first.z), ivec3(last.x -1,  first.y, first.z   ) + 1)
        yield from loop3D(ivec3(last.x,  first.y, first.z), ivec3(last.x,     first.y, last.z  -1) + 1)
        yield from loop3D(ivec3(last.x,  first.y, last.z ), ivec3(first.x +1, first.y, last.z    ) - 1)
        yield from loop3D(ivec3(first.x, first.y, last.z ), ivec3(first.x,    first.y, first.z +1) - 1)
        # top face
        yield from loop3D(ivec3(first.x, last.y,  first.z), ivec3(last.x -1,  last.y,  first.z   ) + 1)
        yield from loop3D(ivec3(last.x,  last.y,  first.z), ivec3(last.x,     last.y,  last.z  -1) + 1)
        yield from loop3D(ivec3(last.x,  last.y,  last.z ), ivec3(first.x +1, last.y,  last.z    ) - 1)
        yield from loop3D(ivec3(first.x, last.y,  last.z ), ivec3(first.x,    last.y,  first.z +1) - 1)
        # sides
        yield from loop3D(ivec3(first.x, first.y+1, first.z), ivec3(first.x, last.y-1, first.z) + 1)
        yield from loop3D(ivec3(last.x,  first.y+1, first.z), ivec3(last.x,  last.y-1, first.z) + 1)
        yield from loop3D(ivec3(last.x,  first.y+1, last.z ), ivec3(last.x,  last.y-1, last.z ) + 1)
        yield from loop3D(ivec3(first.x, first.y+1, last.z ), ivec3(first.x, last.y-1, last.z ) + 1)


def rectSlice(array: np.ndarray, rect: Rect):
    """Returns the slice from [array] defined by [rect]"""
    return array[rect.begin.x:rect.end.x, rect.begin.y:rect.end.y]


def setRectSlice(array: np.ndarray, rect: Rect, value: Any):
    """Sets the slice from [array] defined by [rect] to [value]"""
    array[rect.begin.x:rect.end.x, rect.begin.y:rect.end.y] = value


def boxSlice(array: np.ndarray, box: Box):
    """Returns the slice from [array] defined by [box]"""
    return array[box.begin.x:box.end.x, box.begin.y:box.end.y, box.begin.z:box.end.z]


def setBoxSlice(array: np.ndarray, box: Box, value: Any):
    """Sets the slice from [array] defined by [box] to [value]"""
    array[box.begin.x:box.end.x, box.begin.y:box.end.y, box.begin.z:box.end.z] = value


# ==================================================================================================
# Point generation
# ==================================================================================================


def loop2D(begin: ivec2, end: Optional[ivec2] = None):
    """Yields all points between <begin> and <end> (end-exclusive).\n
    If <end> is not given, yields all points between (0,0) and <begin>."""
    if end is None:
        begin, end = ivec2(0, 0), begin

    for x in range(begin.x, end.x, non_zero_sign(end.x - begin.x)):
        for y in range(begin.y, end.y, non_zero_sign(end.y - begin.y)):
            yield ivec2(x, y)


def loop3D(begin: ivec3, end: Optional[ivec3] = None):
    """Yields all points between <begin> and <end> (end-exclusive).\n
    If <end> is not given, yields all points between (0,0,0) and <begin>."""
    if end is None:
        begin, end = ivec3(0, 0, 0), begin

    for x in range(begin.x, end.x, non_zero_sign(end.x - begin.x)):
        for y in range(begin.y, end.y, non_zero_sign(end.y - begin.y)):
            for z in range(begin.z, end.z, non_zero_sign(end.z - begin.z)):
                yield ivec3(x, y, z)


def cuboid2D(corner1: ivec2, corner2: ivec2):
    """Yields all points in the rectangle between <corner1> and <corner2> (inclusive)."""
    return Rect.between(corner1, corner2).inner


def cuboid3D(corner1: ivec3, corner2: ivec3):
    """Yields all points in the box between <corner1> and <corner2> (inclusive)."""
    return Box.between(corner1, corner2).inner


def filled2DArray(points: Iterable[ivec2], seedPoint: ivec2, boundingRect: Optional[Rect] = None, includeInputPoints=True) -> np.ndarray:
    """Fills the shape defined by <points>, starting at <seedPoint> and returns a (n,2) numpy array
    containing the resulting points.\n
    <boundingRect> should contain all <points>. If not provided, it is calculated."""
    if boundingRect is None:
        boundingRect = Rect.bounding(points)

    pointMap = np.zeros(boundingRect.size, dtype=int)
    pointMap[tuple(np.transpose(np.array(points) - np.array(boundingRect.offset)))] = 1
    filled = skimage.segmentation.flood_fill(pointMap, tuple(seedPoint - boundingRect.offset), 1, footprint=np.array([[0,1,0],[1,1,1],[0,1,0]]))
    if not includeInputPoints:
        filled -= pointMap
    return np.argwhere(filled) + np.array(boundingRect.offset)


def filled2D(points: Iterable[ivec2], seedPoint: ivec2, boundingRect: Optional[Rect] = None, includeInputPoints=True):
    """Fills the shape defined by <points>, starting at <seedPoint> and yields the resulting points.\n
    <boundingRect> should contain all <points>. If not provided, it is calculated."""
    return (ivec2(*point) for point in filled2DArray(points, seedPoint, boundingRect, includeInputPoints))


def filled3DArray(points: Iterable[ivec3], seedPoint: ivec3, boundingBox: Optional[Box] = None, includeInputPoints=True) -> np.ndarray:
    """Fills the shape defined by <points>, starting at <seedPoint> and returns a (n,3) numpy array
    containing the resulting points.\n
    <boundingBox> should contain all <points>. If not provided, it is calculated."""
    if boundingBox is None:
        boundingBox = Rect.bounding(points)

    pointMap = np.zeros(boundingBox.size, dtype=int)
    pointMap[tuple(np.transpose(np.array(points) - np.array(boundingBox.offset)))] = 1
    filled = skimage.segmentation.flood_fill(pointMap, tuple(seedPoint - boundingBox.offset), 1, connectivity=1)
    if not includeInputPoints:
        filled -= pointMap
    return np.argwhere(filled) + np.array(boundingBox.offset)


def filled3D(points: Iterable[ivec3], seedPoint: ivec3, boundingBox: Optional[Box] = None, includeInputPoints=True):
    """Fills the shape defined by <points>, starting at <seedPoint> and yields the resulting points.\n
    <boundingBox> should contain all <points>. If not provided, it is calculated."""
    return (ivec3(*point) for point in filled3DArray(points, seedPoint, boundingBox, includeInputPoints))


# TODO: separate out thickening code?
def _lineArray(begin: Union[ivec2, ivec3], end: Union[ivec2, ivec3], width: int = 1) -> np.ndarray:
    delta = np.array(end - begin)
    maxDelta = int(max(abs(delta)))
    if maxDelta == 0:
        return np.array([])
    points = delta[np.newaxis,:] * np.arange(maxDelta + 1)[:,np.newaxis] / maxDelta + np.array(begin)
    points = np.rint(points).astype(np.signedinteger)

    if width > 1:
        minPoint = np.array(glm.min(begin, end))

        # convert point array to a map
        array_width = maxDelta + width*2
        array = np.zeros([array_width]*len(begin), dtype=int)
        array[tuple(np.transpose(points - minPoint + width))] = 1

        # dilate map (make it thick)
        if width > 1:
            array = ndimage.binary_dilation(array, iterations = width - 1)

        # rebuild point array from map
        points = np.argwhere(array) + minPoint - width

    return points


def line2DArray(begin: ivec2, end: ivec2, width: int = 1):
    """Returns (n,2) numpy array of points on the line between [begin] and [end] (inclusive)"""
    return _lineArray(begin, end, width)


def line2D(begin: ivec2, end: ivec2, width: int = 1):
    """Yields the points on the line between [begin] and [end] (inclusive)"""
    return (ivec2(*point) for point in _lineArray(begin, end, width))


def line3Darray(begin: ivec3, end: ivec3, width: int = 1):
    """Returns (n,3) numpy array of points on the line between [begin] and [end] (inclusive)"""
    return _lineArray(begin, end, width)


def line3D(begin: ivec3, end: ivec3, width: int = 1):
    """Yields the points on the line between [begin] and [end] (inclusive)"""
    return (ivec3(*point) for point in _lineArray(begin, end, width))


def lineSequence2D(points: Iterable[ivec2], closed=False):
    """Yields all points on the lines that connect <points>"""
    for i in range((-1 if closed else 0), len(points)-1):
        yield from line2D(points[i], points[i+1])


def lineSequence3D(points: Iterable[ivec3], closed=False):
    """Yields all points on the lines that connect <points>"""
    for i in range((-1 if closed else 0), len(points)-1):
        yield from line3D(points[i], points[i+1])


def circle(center: ivec2, diameter: int, filled=False):
    """Yields the points of the specified circle.\n
    If <diameter> is even, <center> will be the bottom left center point."""

    # With 'inspiration' from:
    # https://www.geeksforgeeks.org/bresenhams-circle-drawing-algorithm/

    if diameter == 0:
        empty: List[ivec2] = []
        return (point for point in empty)

    e = 1 - (diameter % 2) # for even centers
    points: Set[ivec2] = set()

    def eightPoints(x: int, y: int):
        points.add(center + ivec2(e + x, e + y))
        points.add(center + ivec2(0 - x, e + y))
        points.add(center + ivec2(e + x, 0 - y))
        points.add(center + ivec2(0 - x, 0 - y))
        points.add(center + ivec2(e + y, e + x))
        points.add(center + ivec2(0 - y, e + x))
        points.add(center + ivec2(e + y, 0 - x))
        points.add(center + ivec2(0 - y, 0 - x))

    radius = (diameter-1) // 2
    x, y = 0, radius
    d = 3 - 2 * radius
    eightPoints(x, y)
    while y >= x:
        # for each pixel we will
        # draw all eight pixels

        x += 1

        # check for decision parameter
        # and correspondingly
        # update d, x, y
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6
        eightPoints(x, y)

    if filled:
        return filled2D(points, center, Rect(center - radius, ivec2(diameter, diameter)))
    return (point for point in points)


def fittingCircle(corner1: ivec2, corner2: ivec2, filled=False):
    """Yields the points of the largest circle that fits between <corner1> and <corner2>.\n
    The circle is centered in the larger axis."""
    corner1, corner2 = orderedCorners2D(corner1, corner2)
    diameter = min(corner2.x - corner1.x, corner2.y - corner1.y) + 1
    return circle((corner1 + corner2) // 2, diameter, filled)


def ellipse(center: ivec2, diameters: ivec2, filled=False):
    """Yields the points of the specified ellipse.\n
    If <diameter>[axis] is even, <center>[axis] will be the lower center point in that axis."""

    # Modified version 'inspired' by chandan_jnu from
    # https://www.geeksforgeeks.org/midpoint-ellipse-drawing-algorithm/

    if diameters.x == 0 or diameters.y == 0:
        empty: List[ivec2] = []
        return (point for point in empty)

    if diameters.x == diameters.y:
        return circle(center, diameters.x, filled)

    e = 1 - (diameters % 2)

    points: Set[ivec2] = set()

    def fourpoints(x, y):
        points.add(center + ivec2(e.x + x, e.y + y))
        points.add(center + ivec2(0   - x, e.y + y))
        points.add(center + ivec2(e.x + x, 0   - y))
        points.add(center + ivec2(0   - x, 0   - y))

        if filled:
            points.update(line2D(center + ivec2(0 - x, e.y + y), center + ivec2(e.x + x, e.y + y)))
            points.update(line2D(center + ivec2(0 - x, 0   - y), center + ivec2(e.x + x, 0   - y)))

    rx, ry = (diameters-1) // 2

    x, y = 0, ry

    # Initial decision parameter of region 1
    d1 = ((ry * ry) - (rx * rx * ry) + (0.25 * rx * rx))
    dx = 2 * ry * ry * x
    dy = 2 * rx * rx * y

    # For region 1
    while dx < dy:
        fourpoints(x, y)

        # Checking and updating value of
        # decision parameter based on algorithm
        if d1 < 0:
            x += 1
            dx = dx + (2 * ry * ry)
            d1 = d1 + dx + (ry * ry)
        else:
            x += 1
            y -= 1
            dx = dx + (2 * ry * ry)
            dy = dy - (2 * rx * rx)
            d1 = d1 + dx - dy + (ry * ry)

    # Decision parameter of region 2
    d2 = (((ry * ry) * ((x + 0.5) * (x + 0.5)))
          + ((rx * rx) * ((y - 1) * (y - 1))) - (rx * rx * ry * ry))

    # Plotting points of region 2
    while y >= 0:
        fourpoints(x, y)

        # Checking and updating parameter
        # value based on algorithm
        if d2 > 0:
            y -= 1
            dy = dy - (2 * rx * rx)
            d2 = d2 + (rx * rx) - dy
        else:
            y -= 1
            x += 1
            dx = dx + (2 * ry * ry)
            dy = dy - (2 * rx * rx)
            d2 = d2 + dx - dy + (rx * rx)

    return (point for point in points)


def fittingEllipse(corner1: ivec2, corner2: ivec2, filled=False):
    """Yields the points of the largest ellipse that fits between <corner1> and <corner2>."""
    corner1, corner2 = orderedCorners2D(corner1, corner2)
    diameters = (corner2 - corner1) + 1
    return ellipse((corner1 + corner2) // 2, diameters, filled)


def cylinder(baseCenter: ivec3, diameters: Union[ivec2, int], length: int, axis=1, tube=False, hollow=False):
    """Yields the points from the specified cylinder.\n
    If <diameter> is even, <center> will be the bottom left center point.\n
    <tube> has precedence over <hollow>."""

    if isinstance(diameters, int):
        diameters = ivec2(diameters, diameters)

    if diameters.x == 0 or diameters.y == 0 or length == 0:
        empty: List[ivec3] = []
        return (point for point in empty)

    corner1 = baseCenter - addDimension((diameters-1)/2, axis, 0)
    corner2 = corner1 + addDimension(diameters-1, axis, length-1)
    return fittingCylinder(corner1, corner2, axis, tube, hollow)


def fittingCylinder(corner1: ivec3, corner2: ivec3, axis=1, tube=False, hollow=False):
    """Yields the points of the largest cylinder that fits between <corner1> and <corner2>.\n
    <tube> has precedence over <hollow>."""

    corner1, corner2 = orderedCorners3D(corner1, corner2)
    dimensionality, flatSides = getDimensionality(corner1, corner2)

    if dimensionality == 0:
        yield corner1
        return

    if (dimensionality == 1 or (dimensionality == 2 and flatSides[0] != axis)):
        yield from cuboid3D(corner1, corner2)
        return

    baseCorner1 = dropDimension(corner1, axis)
    baseCorner2 = dropDimension(corner2, axis)
    h0 = corner1[axis]
    hn = corner2[axis]

    ellipsePoints2D = list(fittingEllipse(baseCorner1, baseCorner2, filled=False))
    ellipsePoints3D = [addDimension(point, axis, h0) for point in ellipsePoints2D]

    if tube:
        basePoints = ellipsePoints3D
        bodyPoints = ellipsePoints3D
    else:
        basePoints = [addDimension(point, axis, h0) for point in filled2D(ellipsePoints2D, (baseCorner1 + baseCorner2) // 2, Rect.between(baseCorner1, baseCorner2))]
        bodyPoints = ellipsePoints3D if hollow else basePoints

    yield from basePoints
    if hn != h0:
        direction = ivec3(0,0,0)
        direction[axis] = 1
        yield from (point + (hn - h0)*direction for point in basePoints)
        yield from (point + i*direction for i in range(1, hn-h0) for point in bodyPoints)


def neighbors2D(point: ivec2, boundingRect: Rect, diagonal: bool = False, stride: int = 1):
    """Yields the neighbors of [point] within [bounding_rect].\n
    Useful for pathfinding."""

    end = boundingRect.end

    left  = point.x - stride >= boundingRect.offset.x
    down  = point.y - stride >= boundingRect.offset.y
    right = point.x + stride <  end.x
    up    = point.y + stride <  end.y

    if left:   yield ivec2(point.x - stride, point.y         )
    if down:   yield ivec2(point.x         , point.y - stride)
    if right:  yield ivec2(point.x + stride, point.y         )
    if up:     yield ivec2(point.x         , point.y + stride)

    if not diagonal:
        return

    if left  and down: yield ivec2(point.x - stride, point.y - stride)
    if left  and up:   yield ivec2(point.x - stride, point.y + stride)
    if right and down: yield ivec2(point.x + stride, point.y - stride)
    if right and up:   yield ivec2(point.x + stride, point.y + stride)


def neighbors3D(point: ivec3, boundingBox: Box, diagonal: bool = False, stride: int = 1):
    """Yields the neighbors of [point] within [bounding_box].\n
    Useful for pathfinding."""

    end = boundingBox.end

    left  = point.x - stride >= boundingBox.offset.x
    down  = point.y - stride >= boundingBox.offset.y
    back  = point.z - stride >= boundingBox.offset.z
    right = point.x + stride <  end.x
    up    = point.y + stride <  end.y
    front = point.z + stride <  end.z

    if left:  yield ivec3(point.x - stride, point.y         , point.z         )
    if down:  yield ivec3(point.x         , point.y - stride, point.z         )
    if back:  yield ivec3(point.x         , point.y         , point.z - stride)
    if right: yield ivec3(point.x + stride, point.y         , point.z         )
    if up:    yield ivec3(point.x         , point.y + stride, point.z         )
    if front: yield ivec3(point.x         , point.y         , point.z + stride)

    if not diagonal:
        return

    if left  and down:           yield ivec3(point.x - stride, point.y - stride, point.z         )
    if left  and back:           yield ivec3(point.x - stride, point.y         , point.z - stride)
    if left  and up:             yield ivec3(point.x - stride, point.y + stride, point.z         )
    if left  and front:          yield ivec3(point.x - stride, point.y         , point.z + stride)
    if right and down:           yield ivec3(point.x + stride, point.y - stride, point.z         )
    if right and back:           yield ivec3(point.x + stride, point.y         , point.z - stride)
    if right and up:             yield ivec3(point.x + stride, point.y + stride, point.z         )
    if right and front:          yield ivec3(point.x + stride, point.y         , point.z + stride)
    if down  and back:           yield ivec3(point.x         , point.y - stride, point.z - stride)
    if down  and front:          yield ivec3(point.x         , point.y - stride, point.z + stride)
    if up    and back:           yield ivec3(point.x         , point.y + stride, point.z - stride)
    if up    and front:          yield ivec3(point.x         , point.y + stride, point.z + stride)
    if left  and down and back:  yield ivec3(point.x - stride, point.y - stride, point.z - stride)
    if left  and down and front: yield ivec3(point.x - stride, point.y - stride, point.z + stride)
    if left  and up   and back:  yield ivec3(point.x - stride, point.y + stride, point.z - stride)
    if left  and up   and front: yield ivec3(point.x - stride, point.y + stride, point.z + stride)
    if right and down and back:  yield ivec3(point.x + stride, point.y - stride, point.z - stride)
    if right and down and front: yield ivec3(point.x + stride, point.y - stride, point.z + stride)
    if right and up   and back:  yield ivec3(point.x + stride, point.y + stride, point.z - stride)
    if right and up   and front: yield ivec3(point.x + stride, point.y + stride, point.z + stride)

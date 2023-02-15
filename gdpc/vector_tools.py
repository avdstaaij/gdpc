"""Various vector utilities"""


from typing import Sequence, Any, Iterable, List, Optional, Set, Tuple, Union
from abc import ABC
from numbers import Integral
from dataclasses import dataclass
import math

from more_itertools import powerset
import numpy as np
from scipy import ndimage
import skimage.segmentation
import glm
from glm import ivec2, ivec3, vec2, vec3, bvec2, bvec3

from .utils import nonZeroSign


# ==================================================================================================
# VecLike ABCs
# ==================================================================================================


class Vec2iLike(ABC, Sequence[int]):
    """An abstract base class. A class is a Vec2iLike if it acts like a sequence of two Integrals."""
    @classmethod
    def __subclasshook__(cls, C):
        try:
            return len(C) == 2 and all(isinstance(C[i], Integral) for i in range(2))
        except TypeError:
            return False

class Vec3iLike(ABC, Sequence[int]):
    """An abstract base class. A class is a Vec3iLike if it acts like a sequence of three Integrals."""
    @classmethod
    def __subclasshook__(cls, C):
        try:
            return len(C) == 3 and all(isinstance(C[i], Integral) for i in range(3))
        except TypeError:
            return False

class Vec2bLike(ABC, Sequence[bool]):
    """An abstract base class. A class is a Vec2bLike if it acts like a sequence of two bools."""
    @classmethod
    def __subclasshook__(cls, C):
        try:
            return len(C) == 2 and all(isinstance(C[i], bool) for i in range(2))
        except TypeError:
            return False

class Vec3bLike(ABC, Sequence[bool]):
    """An abstract base class. A class is a Vec3bLike if it acts like a sequence of three bools."""
    @classmethod
    def __subclasshook__(cls, C):
        try:
            return len(C) == 3 and all(isinstance(C[i], bool) for i in range(3))
        except TypeError:
            return False


# ==================================================================================================
# Constants
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


# ==================================================================================================
# General
# ==================================================================================================


def dropDimension(vec: Vec3iLike, dimension: int):
    """Returns <vec> without its <dimension>-th component"""
    if dimension == 0: return ivec2(vec[1], vec[2])
    if dimension == 1: return ivec2(vec[0], vec[2])
    if dimension == 2: return ivec2(vec[0], vec[1])
    raise ValueError(f'Invalid dimension "{dimension}"')


def addDimension(vec: Vec2iLike, dimension: int, value=0):
    """Inserts <value> into <vec> at <dimension> and returns the resulting 3D vector"""
    l = list(vec)
    return ivec3(*l[:dimension], value, *l[dimension:])


def dropY(vec: Vec3iLike):
    """Returns [vec] without its y-component (i.e., projected on the XZ-plane)"""
    return ivec2(vec[0], vec[2])


def addY(vec: Vec2iLike, y=0):
    """Returns a 3D vector (vec[0], y, vec[1])"""
    return ivec3(vec[0], y, vec[1])


def setY(vec: Vec3iLike, y=0):
    """Returns [vec] with its y-component set to [y]"""
    return ivec3(vec[0], y, vec[2])


def trueMod2D(vec: Vec2iLike, modulus: int):
    """Returns <v> modulo <modulus>.\n
    Negative numbers are handled just like Python's built-in integer modulo."""
    return ivec2(vec[0] % modulus, vec[1] % modulus)

def trueMod3D(vec: Vec3iLike, modulus: int):
    """Returns <v> modulo <modulus>.\n
    Negative numbers are handled just like Python's built-in integer modulo."""
    return ivec3(vec[0] % modulus, vec[1] % modulus, vec[2] % modulus)


def perpendicular(vec: Vec2iLike):
    """Returns the vector perpendicular to [vec] that points to the right of [vec] and has the same
    length as [vec]."""
    return ivec2(vec[1], -vec[0])


def rotate2D(vec: Vec2iLike, rotation: int):
    """Returns [vec], rotated by [rotation]"""
    if rotation == 0: return ivec2(*vec)
    if rotation == 1: return ivec2(-vec[1],  vec[0])
    if rotation == 2: return ivec2(-vec[0], -vec[1])
    if rotation == 3: return ivec2( vec[1], -vec[0])
    raise ValueError("Rotation must be in {0,1,2,3}")


def rotate3D(vec: Vec3iLike, rotation: int):
    """Returns [vec], rotated in the XZ-plane by [rotation]"""
    return addY(rotate2D(dropY(vec), rotation), vec[1])


def flipRotation2D(rotation: int, flip: Vec2bLike):
    """Returns rotation such that applying rotation after <flip> is equivalent to applying <flip>
    after <rotation>."""
    scale = flipToScale2D(flip)
    return (rotation * scale.x * scale.y + 4) % 4

def flipRotation3D(rotation: int, flip: Vec3bLike):
    """Returns rotation such that applying rotation after <flip> is equivalent to applying <flip>
    after <rotation>"""
    return flipRotation2D(rotation, dropY(flip))


def rotateSize2D(size: Vec2iLike, rotation: int):
    """Returns the effective size of a rect of size [size] that has been rotated in the XZ-plane by
    [rotation]."""
    return ivec2(size[1], size[0]) if rotation in [1, 3] else size


def rotateSize3D(size: Vec3iLike, rotation: int):
    """Returns the effective size of a box of size [size] that has been rotated in the XZ-plane by
    [rotation]."""
    return addY(rotateSize2D(dropY(size), rotation), size[1])


def flipToScale2D(flip: Vec2bLike):
    """Returns a vector with a 1 where <flip> is false, and -1 where <flip> is true"""
    return 1 - 2*ivec2(*flip)

def flipToScale3D(flip: Vec3bLike):
    """Returns a vector with a 1 where <flip> is false, and -1 where <flip> is true"""
    return 1 - 2*ivec3(*flip)


def scaleToFlip2D(scale: Vec2iLike):
    """Returns whether [scale] flips space in each axis"""
    return bvec2(scale[0] < 0, scale[1] < 0)

def scaleToFlip3D(scale: Vec3iLike):
    """Returns whether [scale] flips space in each axis"""
    return bvec3(scale[0] < 0, scale[1] < 0, scale[2] < 0)


def toAxisVector2D(vec: Vec2iLike):
    """Returns the axis-aligned unit vector closest to [vec]"""
    if abs(vec[0]) > abs(vec[1]): # pylint: disable=no-else-return
        return ivec2(nonZeroSign(vec[0]), 0)
    else:
        return ivec2(0, nonZeroSign(vec[1]))


def directionToRotation(direction: Vec2iLike):
    """Returns the rotation that rotates (0,-1) closest to [direction]"""
    vec = toAxisVector2D(direction)
    if vec[1] < 0: return 0
    if vec[0] > 0: return 1
    if vec[1] > 0: return 2
    if vec[0] < 0: return 3
    raise ValueError()


# For some reason, glm's length, length2, distance, distance2 and l1Norm refuse to work with integer
# vectors. We provide some wrappers.

def length(vec: Union[Vec2iLike, Vec3iLike]):
    """Returns the length of [vec]"""
    if len(vec) == 2: return glm.length(vec2(*vec))
    if len(vec) == 3: return glm.length(vec3(*vec))
    raise ValueError()

def length2(vec: Union[Vec2iLike, Vec3iLike]):
    """Returns the squared length of [vec]"""
    if len(vec) == 2: return int(glm.length2(vec2(*vec)))
    if len(vec) == 3: return int(glm.length2(vec3(*vec)))
    raise ValueError()

def distance(vecA: Union[Vec2iLike, Vec3iLike], vecB: Union[Vec2iLike, Vec3iLike]) -> float:
    """Returns the distance between [vecA] and [vecB]"""
    if len(vecA) == 2 and len(vecB) == 2: return glm.distance(vec2(*vecA), vec2(*vecB))
    if len(vecA) == 3 and len(vecB) == 3: return glm.distance(vec3(*vecA), vec3(*vecB))
    raise ValueError()

def distance2(vecA: Union[Vec2iLike, Vec3iLike], vecB: Union[Vec2iLike, Vec3iLike]):
    """Returns the squared distance between [vecA] and [vecB]"""
    if len(vecA) == 2 and len(vecB) == 2: return int(glm.distance2(vec2(*vecA), vec2(*vecB)))
    if len(vecA) == 3 and len(vecB) == 3: return int(glm.distance2(vec3(*vecA), vec3(*vecB)))
    raise ValueError()

def l1Norm(vec: Union[Vec2iLike, Vec3iLike]):
    """Returns the L1 norm of [vec]"""
    return sum(abs(n) for n in vec)

def l1Distance(vecA: Union[Vec2iLike, Vec3iLike], vecB: Union[Vec2iLike, Vec3iLike]):
    """Returns the L1 norm distance between [vecA] and [vecB]"""
    return l1Norm(vecA - vecB)


def orderedCorners2D(corner1: Vec2iLike, corner2: Vec2iLike):
    """Returns two corners of the rectangle defined by <corner1> and <corner2>, such that the first
    corner is smaller than the second corner in each axis"""
    return (
        ivec2(
            corner1[0] if corner1[0] <= corner2[0] else corner2[0],
            corner1[1] if corner1[1] <= corner2[1] else corner2[1],
        ),
        ivec2(
            corner1[0] if corner1[0] > corner2[0] else corner2[0],
            corner1[1] if corner1[1] > corner2[1] else corner2[1],
        )
    )


def orderedCorners3D(corner1: Vec3iLike, corner2: Vec3iLike):
    """Returns two corners of the box defined by <corner1> and <corner2>, such that the first
    corner is smaller than the second corner in each axis"""
    return (
        ivec3(
            corner1[0] if corner1[0] <= corner2[0] else corner2[0],
            corner1[1] if corner1[1] <= corner2[1] else corner2[1],
            corner1[2] if corner1[2] <= corner2[2] else corner2[2],
        ),
        ivec3(
            corner1[0] if corner1[0] > corner2[0] else corner2[0],
            corner1[1] if corner1[1] > corner2[1] else corner2[1],
            corner1[2] if corner1[2] > corner2[2] else corner2[2],
        )
    )


def getDimensionality(corner1: Union[Vec2iLike, Vec3iLike], corner2: Union[Vec2iLike, Vec3iLike]) -> Tuple[int, List[str]]:
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

    _offset: ivec2
    _size:   ivec2

    def __init__(self, offset: Vec2iLike = (0,0), size: Vec2iLike = (0,0)):
        self._offset = ivec2(*offset)
        self._size   = ivec2(*size)

    def __repr__(self):
        return f"Rect({tuple(self._offset)}, {tuple(self._size)})"

    @property
    def offset(self):
        """This Rect's offset"""
        return self._offset

    @offset.setter
    def offset(self, value: Vec2iLike):
        self._offset = ivec2(*value)

    @property
    def size(self):
        """This Rect's size"""
        return self._size

    @size.setter
    def size(self, value: Vec2iLike):
        self._size = ivec2(*value)

    @property
    def begin(self):
        """Equivalent to self.offset. Setting will modify self.offset."""
        return self._offset

    @begin.setter
    def begin(self, value: Vec2iLike):
        self._offset = ivec2(*value)

    @property
    def end(self):
        """Equivalent to self.offset + self.size. Setting will modify self.size."""
        return self.begin + self._size

    @end.setter
    def end(self, value: Vec2iLike):
        self._size = ivec2(*value) - self.begin

    @property
    def last(self):
        """Equivalent to self.offset + self.size - 1. Setting will modify self.size."""
        return self._offset + self._size - 1

    @last.setter
    def last(self, value: Vec2iLike):
        self._size = ivec2(*value) - self._offset + 1

    @property
    def middle(self):
        """This Rect's middle point, rounded down"""
        return self._offset + self._size // 2

    @property
    def center(self):
        """Equivalent to .middle"""
        return self.middle

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
        return self._size.x*self._size.y

    @property
    def corners(self):
        """Yields this Rect's corner points"""
        return (
            self._offset + sum(subset)
            for subset in powerset([ivec2(self._size.x, 0), ivec2(0, self._size.y)])
        )

    def contains(self, vec: Vec2iLike):
        """Returns whether this Rect contains [vec]"""
        return (
            self.begin.x <= vec[0] < self.end.x and
            self.begin.y <= vec[1] < self.end.y
        )

    def collides(self, other: 'Rect'):
        """Returns whether this Rect and [other] have any overlap"""
        return (
            self.begin.x <= other.end  .x and
            self.end  .x >= other.begin.x and
            self.begin.y <= other.end  .y and
            self.end  .y >= other.begin.y
        )

    def squaredDistanceToVec(self, vec: Vec2iLike):
        """Returns the squared distance between this Rect and [vec]"""
        dx = max(self.begin.x - vec[0], 0, vec[0] - (self.end[0] - 1))
        dy = max(self.begin.y - vec[1], 0, vec[1] - (self.end[1] - 1))
        return dx*dx + dy*dy

    def distanceToVec(self, vec: Vec2iLike):
        """Returns the distance between this Rect and [vec]"""
        return math.sqrt(self.squaredDistanceToVec(vec))

    def translated(self, translation: Union[Vec2iLike, int]):
        """Returns a copy of this Rect, translated by [translation]"""
        return Rect(self._offset + ivec2(*translation), self._size)

    def dilate(self, dilation: int = 1):
        """Morphologically dilates this rect by [dilation]"""
        self._offset  -= dilation
        self._size    += dilation*2

    def dilated(self, dilation: int = 1):
        """Returns a copy of this Rect, morphologically dilated by [dilation]"""
        return Rect(self._offset - dilation, self._size + dilation*2)

    def erode(self, erosion: int = 1):
        """Morphologically erodes this rect by [erosion]"""
        self.dilate(-erosion)

    def eroded(self, erosion: int = 1):
        """Returns a copy of this Rect, morphologically eroded by [erosion]"""
        return self.dilated(-erosion)

    def centeredSubRectOffset(self, size: Vec2iLike):
        """Returns an offset such that Rect(offset, [size]).middle == self.middle"""
        difference = self._size - ivec2(*size)
        return self._offset + difference/2

    def centeredSubRect(self, size: Vec2iLike):
        """Returns a rect of size [size] with the same middle as this rect"""
        return Rect(self.centeredSubRectOffset(size), size)

    @staticmethod
    def between(cornerA: Vec2iLike, cornerB: Vec2iLike):
        """Returns the Rect between [cornerA] and [cornerB] (inclusive),
        which may be any opposing corners."""
        first, last = orderedCorners2D(cornerA, cornerB)
        return Rect(first, (last - first) + 1)

    @staticmethod
    def bounding(points: Iterable[Vec2iLike]):
        """Returns the smallest Rect containing all [points]"""
        pointArray = np.array(points)
        minPoint = np.min(pointArray, axis=0)
        maxPoint = np.max(pointArray, axis=0)
        return Rect(minPoint, maxPoint - minPoint + 1)

    def toBox(self, offsetY = 0, sizeY = 0):
        """Returns a corresponding Box"""
        return Box(addY(self.offset, offsetY), addY(self._size, sizeY))

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

    _offset: ivec3
    _size:   ivec3

    def __init__(self, offset: Vec3iLike = (0,0,0), size: Vec3iLike = (0,0,0)):
        self._offset = ivec3(*offset)
        self._size   = ivec3(*size)

    def __repr__(self):
        return f"Box({tuple(self._offset)}, {tuple(self._size)})"

    @property
    def offset(self):
        """This Box's offset"""
        return self._offset

    @offset.setter
    def offset(self, value: Vec3iLike):
        self._offset = ivec3(*value)

    @property
    def size(self):
        """This Box's size"""
        return self._size

    @size.setter
    def size(self, value: Vec3iLike):
        self._size = ivec3(*value)

    @property
    def begin(self):
        """Equivalent to self.offset. Setting will modify self.offset."""
        return self._offset

    @begin.setter
    def begin(self, value: Vec3iLike):
        self._offset = ivec3(*value)

    @property
    def end(self):
        """Equivalent to self.offset + self.size. Setting will modify self.size."""
        return self.begin + self._size

    @end.setter
    def end(self, value: Vec3iLike):
        self._size = ivec3(*value) - self.begin

    @property
    def last(self):
        """Equivalent to self.offset + self.size - 1. Setting will modify self.size."""
        return self._offset + self._size - 1

    @last.setter
    def last(self, value: Vec3iLike):
        self._size = ivec3(*value) - self._offset + 1

    @property
    def middle(self):
        """This Box's middle point, rounded down"""
        return self.begin + self._size // 2

    @property
    def center(self):
        """Equivalent to .middle"""
        return self.middle

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
        return self._size.x*self._size.y*self._size.z

    @property
    def corners(self):
        """Yields this Box's corner points"""
        return [
            self._offset + sum(subset)
            for subset in powerset([ivec3(self._size.x, 0, 0), ivec3(0, self._size.y, 0), ivec3(0, 0, self._size.z)])
        ]

    def contains(self, vec: Vec3iLike):
        """Returns whether this Box contains [vec]"""
        return (
            self.begin.x <= vec[0] < self.end.x and
            self.begin.y <= vec[1] < self.end.y and
            self.begin.z <= vec[2] < self.end.z
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

    def squaredDistanceToVec(self, vec: Vec3iLike):
        """Returns the squared distance between this Box and [vec]"""
        dx = max(self.begin.x - vec[0], 0, vec[0] - (self.end.x - 1))
        dy = max(self.begin.y - vec[1], 0, vec[1] - (self.end.y - 1))
        dz = max(self.begin.z - vec[2], 0, vec[2] - (self.end.z - 1))
        return dx*dx + dy*dy + dz*dz

    def distanceToVec(self, vec: Vec3iLike):
        """Returns the distance between this Box and [vec]"""
        return math.sqrt(self.squaredDistanceToVec(vec))

    def translated(self, translation: Union[Vec3iLike, int]):
        """Returns a copy of this Box, translated by [translation]"""
        return Box(self._offset + ivec3(*translation), self._size)

    def dilate(self, dilation: int = 1):
        """Morphologically dilates this box by [dilation]"""
        self._offset -= dilation
        self._size   += dilation*2

    def dilated(self, dilation: int = 1):
        """Returns a copy of this Box, morphologically dilated by [dilation]"""
        return Rect(self._offset - dilation, self._size + dilation*2)

    def erode(self, erosion: int = 1):
        """Morphologically erodes this box by [erosion]"""
        self.dilate(-erosion)

    def eroded(self, erosion: int = 1):
        """Returns a copy of this Box, morphologically eroded by [erosion]"""
        return self.dilated(-erosion)

    def centeredSubBoxOffset(self, size: Vec3iLike):
        """Returns an offset such that Box(offset, [size]).middle == self.middle"""
        difference = self._size - ivec3(*size)
        return self._offset + difference/2

    def centeredSubBox(self, size: Vec3iLike):
        """Returns an box of size [size] with the same middle as this box"""
        return Box(self.centeredSubBoxOffset(size), size)

    @staticmethod
    def between(cornerA: Vec3iLike, cornerB: Vec3iLike):
        """Returns the Box between [cornerA] and [cornerB] (both inclusive),
        which may be any opposing corners"""
        first, last = orderedCorners3D(cornerA, cornerB)
        return Box(first, last - first + 1)

    @staticmethod
    def bounding(points: Iterable[Vec3iLike]):
        """Returns the smallest Box containing all [points]"""
        pointArray = np.array(points)
        minPoint = np.min(pointArray, axis=0)
        maxPoint = np.max(pointArray, axis=0)
        return Rect(minPoint, maxPoint - minPoint + 1)

    def toRect(self):
        """Returns this Box's XZ-plane as a Rect"""
        return Rect(dropY(self._offset), dropY(self._size))

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
        if self._size.y < 3:
            return
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
        if self._size.y < 3:
            return
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


def loop2D(begin: Vec2iLike, end: Optional[Vec2iLike] = None):
    """Yields all points between <begin> and <end> (end-exclusive).\n
    If <end> is not given, yields all points between (0,0) and <begin>."""
    if end is None:
        begin, end = (0, 0), begin

    for x in range(begin[0], end[0], nonZeroSign(end[0] - begin[0])):
        for y in range(begin[1], end[1], nonZeroSign(end[1] - begin[1])):
            yield ivec2(x, y)


def loop3D(begin: Vec3iLike, end: Optional[Vec3iLike] = None):
    """Yields all points between <begin> and <end> (end-exclusive).\n
    If <end> is not given, yields all points between (0,0,0) and <begin>."""
    if end is None:
        begin, end = (0, 0, 0), begin

    for x in range(begin[0], end[0], nonZeroSign(end[0] - begin[0])):
        for y in range(begin[1], end[1], nonZeroSign(end[1] - begin[1])):
            for z in range(begin[2], end[2], nonZeroSign(end[2] - begin[2])):
                yield ivec3(x, y, z)


def cuboid2D(corner1: Vec2iLike, corner2: Vec2iLike):
    """Yields all points in the rectangle between <corner1> and <corner2> (inclusive)."""
    return Rect.between(corner1, corner2).inner


def cuboid3D(corner1: Vec3iLike, corner2: Vec3iLike):
    """Yields all points in the box between <corner1> and <corner2> (inclusive)."""
    return Box.between(corner1, corner2).inner


def filled2DArray(points: Iterable[Vec2iLike], seedPoint: Vec2iLike, boundingRect: Optional[Rect] = None, includeInputPoints=True) -> np.ndarray:
    """Fills the shape defined by <points>, starting at <seedPoint> and returns a (n,2) numpy array
    containing the resulting points.\n
    <boundingRect> should contain all <points>. If not provided, it is calculated."""
    if boundingRect is None:
        boundingRect = Rect.bounding(points)

    pointMap = np.zeros(boundingRect.size, dtype=int)
    pointMap[tuple(np.transpose(np.array(points) - np.array(boundingRect.offset)))] = 1
    filled = skimage.segmentation.flood_fill(pointMap, tuple(ivec2(*seedPoint) - boundingRect.offset), 1, footprint=np.array([[0,1,0],[1,1,1],[0,1,0]]))
    if not includeInputPoints:
        filled -= pointMap
    return np.argwhere(filled) + np.array(boundingRect.offset)


def filled2D(points: Iterable[Vec2iLike], seedPoint: Vec2iLike, boundingRect: Optional[Rect] = None, includeInputPoints=True):
    """Fills the shape defined by <points>, starting at <seedPoint> and yields the resulting points.\n
    <boundingRect> should contain all <points>. If not provided, it is calculated."""
    return (ivec2(*point) for point in filled2DArray(points, seedPoint, boundingRect, includeInputPoints))


def filled3DArray(points: Iterable[Vec3iLike], seedPoint: Vec3iLike, boundingBox: Optional[Box] = None, includeInputPoints=True) -> np.ndarray:
    """Fills the shape defined by <points>, starting at <seedPoint> and returns a (n,3) numpy array
    containing the resulting points.\n
    <boundingBox> should contain all <points>. If not provided, it is calculated."""
    if boundingBox is None:
        boundingBox = Rect.bounding(points)

    pointMap = np.zeros(boundingBox.size, dtype=int)
    pointMap[tuple(np.transpose(np.array(points) - np.array(boundingBox.offset)))] = 1
    filled = skimage.segmentation.flood_fill(pointMap, tuple(ivec3(*seedPoint) - boundingBox.offset), 1, connectivity=1)
    if not includeInputPoints:
        filled -= pointMap
    return np.argwhere(filled) + np.array(boundingBox.offset)


def filled3D(points: Iterable[Vec3iLike], seedPoint: Vec3iLike, boundingBox: Optional[Box] = None, includeInputPoints=True):
    """Fills the shape defined by <points>, starting at <seedPoint> and yields the resulting points.\n
    <boundingBox> should contain all <points>. If not provided, it is calculated."""
    return (ivec3(*point) for point in filled3DArray(points, seedPoint, boundingBox, includeInputPoints))


# TODO: separate out thickening code?
def _lineArray(begin: Union[Vec2iLike, Vec3iLike], end: Union[Vec2iLike, Vec3iLike], width: int = 1) -> np.ndarray:
    begin: np.ndarray = np.array(begin)
    end:   np.ndarray = np.array(end)
    delta = end - begin
    maxDelta = int(max(abs(delta)))
    if maxDelta == 0:
        return np.array([])
    points = delta[np.newaxis,:] * np.arange(maxDelta + 1)[:,np.newaxis] / maxDelta + np.array(begin)
    points = np.rint(points).astype(np.signedinteger)

    if width > 1:
        minPoint = np.minimum(begin, end)

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


def line2DArray(begin: Vec2iLike, end: Vec2iLike, width: int = 1):
    """Returns (n,2) numpy array of points on the line between [begin] and [end] (inclusive)"""
    return _lineArray(begin, end, width)


def line2D(begin: Vec2iLike, end: Vec2iLike, width: int = 1):
    """Yields the points on the line between [begin] and [end] (inclusive)"""
    return (ivec2(*point) for point in _lineArray(begin, end, width))


def line3Darray(begin: Vec3iLike, end: Vec3iLike, width: int = 1):
    """Returns (n,3) numpy array of points on the line between [begin] and [end] (inclusive)"""
    return _lineArray(begin, end, width)


def line3D(begin: Vec3iLike, end: Vec3iLike, width: int = 1):
    """Yields the points on the line between [begin] and [end] (inclusive)"""
    return (ivec3(*point) for point in _lineArray(begin, end, width))


def lineSequence2D(points: Iterable[Vec2iLike], closed=False):
    """Yields all points on the lines that connect <points>"""
    for i in range((-1 if closed else 0), len(points)-1):
        yield from line2D(points[i], points[i+1])


def lineSequence3D(points: Iterable[Vec3iLike], closed=False):
    """Yields all points on the lines that connect <points>"""
    for i in range((-1 if closed else 0), len(points)-1):
        yield from line3D(points[i], points[i+1])


def circle(center: Vec2iLike, diameter: int, filled=False):
    """Yields the points of the specified circle.\n
    If <diameter> is even, <center> will be the bottom left center point."""

    # With 'inspiration' from:
    # https://www.geeksforgeeks.org/bresenhams-circle-drawing-algorithm/

    center: ivec2 = ivec2(*center)

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


def fittingCircle(corner1: Vec2iLike, corner2: Vec2iLike, filled=False):
    """Yields the points of the largest circle that fits between <corner1> and <corner2>.\n
    The circle is centered in the larger axis."""
    _corner1, _corner2 = orderedCorners2D(corner1, corner2)
    diameter = min(_corner2.x - _corner1.x, _corner2.y - _corner1.y) + 1
    return circle((_corner1 + _corner2) // 2, diameter, filled)


def ellipse(center: Vec2iLike, diameters: Vec2iLike, filled=False):
    """Yields the points of the specified ellipse.\n
    If <diameter>[axis] is even, <center>[axis] will be the lower center point in that axis."""

    # Modified version 'inspired' by chandan_jnu from
    # https://www.geeksforgeeks.org/midpoint-ellipse-drawing-algorithm/

    center:    ivec2 = ivec2(*center)
    diameters: ivec2 = ivec2(*diameters)

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


def fittingEllipse(corner1: Vec2iLike, corner2: Vec2iLike, filled=False):
    """Yields the points of the largest ellipse that fits between <corner1> and <corner2>."""
    _corner1, _corner2 = orderedCorners2D(corner1, corner2)
    diameters = (_corner2 - _corner1) + 1
    return ellipse((_corner1 + _corner2) // 2, diameters, filled)


def cylinder(baseCenter: Vec3iLike, diameters: Union[Vec2iLike, int], length: int, axis=1, tube=False, hollow=False):
    """Yields the points from the specified cylinder.\n
    If <diameter> is even, <center> will be the bottom left center point.\n
    <tube> has precedence over <hollow>."""

    diameters:  ivec2 = ivec2(diameters) if isinstance(diameters, int) else ivec2(*diameters)
    baseCenter: ivec3 = ivec3(*baseCenter)

    if diameters.x == 0 or diameters.y == 0 or length == 0:
        empty: List[ivec3] = []
        return (point for point in empty)

    corner1 = baseCenter - addDimension((diameters-1)/2, axis, 0)
    corner2 = corner1 + addDimension(diameters-1, axis, length-1)
    return fittingCylinder(corner1, corner2, axis, tube, hollow)


def fittingCylinder(corner1: Vec3iLike, corner2: Vec3iLike, axis=1, tube=False, hollow=False):
    """Yields the points of the largest cylinder that fits between <corner1> and <corner2>.\n
    <tube> has precedence over <hollow>."""

    _corner1, _corner2 = orderedCorners3D(corner1, corner2)
    dimensionality, flatSides = getDimensionality(_corner1, _corner2)

    if dimensionality == 0:
        yield _corner1
        return

    if (dimensionality == 1 or (dimensionality == 2 and flatSides[0] != axis)):
        yield from cuboid3D(_corner1, _corner2)
        return

    baseCorner1 = dropDimension(_corner1, axis)
    baseCorner2 = dropDimension(_corner2, axis)
    h0 = _corner1[axis]
    hn = _corner2[axis]

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


def neighbors2D(point: Vec2iLike, boundingRect: Rect, diagonal: bool = False, stride: int = 1):
    """Yields the neighbors of [point] within [bounding_rect].\n
    Useful for pathfinding."""

    end = boundingRect.end

    left  = point[0] - stride >= boundingRect.offset.x
    down  = point[1] - stride >= boundingRect.offset.y
    right = point[0] + stride <  end.x
    up    = point[1] + stride <  end.y

    if left:   yield ivec2(point[0] - stride, point[1]         )
    if down:   yield ivec2(point[0]         , point[1] - stride)
    if right:  yield ivec2(point[0] + stride, point[1]         )
    if up:     yield ivec2(point[0]         , point[1] + stride)

    if not diagonal:
        return

    if left  and down: yield ivec2(point[0] - stride, point[1] - stride)
    if left  and up:   yield ivec2(point[0] - stride, point[1] + stride)
    if right and down: yield ivec2(point[0] + stride, point[1] - stride)
    if right and up:   yield ivec2(point[0] + stride, point[1] + stride)


def neighbors3D(point: Vec3iLike, boundingBox: Box, diagonal: bool = False, stride: int = 1):
    """Yields the neighbors of [point] within [bounding_box].\n
    Useful for pathfinding."""

    end = boundingBox.end

    left  = point[0] - stride >= boundingBox.offset.x
    down  = point[1] - stride >= boundingBox.offset.y
    back  = point[2] - stride >= boundingBox.offset.z
    right = point[0] + stride <  end.x
    up    = point[1] + stride <  end.y
    front = point[2] + stride <  end.z

    if left:  yield ivec3(point[0] - stride, point[1]         , point[2]         )
    if down:  yield ivec3(point[0]         , point[1] - stride, point[2]         )
    if back:  yield ivec3(point[0]         , point[1]         , point[2] - stride)
    if right: yield ivec3(point[0] + stride, point[1]         , point[2]         )
    if up:    yield ivec3(point[0]         , point[1] + stride, point[2]         )
    if front: yield ivec3(point[0]         , point[1]         , point[2] + stride)

    if not diagonal:
        return

    if left  and down:           yield ivec3(point[0] - stride, point[1] - stride, point[2]         )
    if left  and back:           yield ivec3(point[0] - stride, point[1]         , point[2] - stride)
    if left  and up:             yield ivec3(point[0] - stride, point[1] + stride, point[2]         )
    if left  and front:          yield ivec3(point[0] - stride, point[1]         , point[2] + stride)
    if right and down:           yield ivec3(point[0] + stride, point[1] - stride, point[2]         )
    if right and back:           yield ivec3(point[0] + stride, point[1]         , point[2] - stride)
    if right and up:             yield ivec3(point[0] + stride, point[1] + stride, point[2]         )
    if right and front:          yield ivec3(point[0] + stride, point[1]         , point[2] + stride)
    if down  and back:           yield ivec3(point[0]         , point[1] - stride, point[2] - stride)
    if down  and front:          yield ivec3(point[0]         , point[1] - stride, point[2] + stride)
    if up    and back:           yield ivec3(point[0]         , point[1] + stride, point[2] - stride)
    if up    and front:          yield ivec3(point[0]         , point[1] + stride, point[2] + stride)
    if left  and down and back:  yield ivec3(point[0] - stride, point[1] - stride, point[2] - stride)
    if left  and down and front: yield ivec3(point[0] - stride, point[1] - stride, point[2] + stride)
    if left  and up   and back:  yield ivec3(point[0] - stride, point[1] + stride, point[2] - stride)
    if left  and up   and front: yield ivec3(point[0] - stride, point[1] + stride, point[2] + stride)
    if right and down and back:  yield ivec3(point[0] + stride, point[1] - stride, point[2] - stride)
    if right and down and front: yield ivec3(point[0] + stride, point[1] - stride, point[2] + stride)
    if right and up   and back:  yield ivec3(point[0] + stride, point[1] + stride, point[2] - stride)
    if right and up   and front: yield ivec3(point[0] + stride, point[1] + stride, point[2] + stride)

"""Various vector utilities"""


from typing import Any, List, Optional, Tuple, Union, overload
from dataclasses import dataclass, field
import math

from more_itertools import powerset
import numpy as np
from scipy import ndimage
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
def dropY(vec: vec3) -> vec2: ...
@overload
def dropY(vec: ivec3) -> ivec2: ...
@overload
def dropY(vec: bvec3) -> bvec2: ...

def dropY(vec):
    """Returns [vec] without its y-component"""
    return vec.xz


@overload
def addY(vec: vec2, y: float) -> vec3: ...
@overload
def addY(vec: ivec2, y: int) -> ivec3: ...
@overload
def addY(vec: bvec2, y: bool) -> bvec3: ...

def addY(vec, y=0):
    """Returns [vec] with an added y-component of [y]"""
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
    for i in range(len(result)):
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

def distance(vecA: Union[ivec2, ivec3], vecB: Union[ivec2, ivec3]):
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


def vecString(vec: Union[ivec2, ivec3]):
    """Alternative to [vec].__str__ that is nicer to read"""
    if isinstance(vec, ivec2): return f"({vec.x}, {vec.y})"
    if isinstance(vec, ivec3): return f"({vec.x}, {vec.y}, {vec.z})"
    return ""


@overload
def orderedCorners(corner1: ivec2, corner2: ivec2) -> Tuple[ivec2, ivec2]: ...
@overload
def orderedCorners(corner1: ivec3, corner2: ivec3) -> Tuple[ivec3, ivec3]: ...

def orderedCorners(corner1, corner2):
    """Returns two corners of the rectangle defined by <corner1> and <corner2>, such that the first
    corner is smaller than the second corner in each axis"""
    for axis in range(len(corner1)):
        if corner1[axis] > corner2[axis]:
            corner1[axis], corner2[axis] = corner2[axis], corner1[axis]
    return corner1, corner2


def loop2D(begin: ivec2, end: Optional[ivec2] = None):
    """Yields all points between <begin> and <end> (end-exclusive).\n
    If <end> is not given, yields all points between (0,0) and <begin>."""
    if end is None:
        begin, end = ivec2(0,0), begin

    for x in range(begin.x, end.x, non_zero_sign(end.x - begin.x)):
        for y in range(begin.y, end.y, non_zero_sign(end.y - begin.y)):
            yield ivec2(x, y)


def loop3D(begin: ivec3, end: Optional[ivec3] = None):
    """Yields all points between <begin> and <end> (end-exclusive).\n
    If <end> is not given, yields all points between (0,0,0) and <begin>."""
    if end is None:
        begin, end = ivec3(0,0,0), begin

    for x in range(begin.x, end.x, non_zero_sign(end.x - begin.x)):
        for y in range(begin.y, end.y, non_zero_sign(end.y - begin.y)):
            for z in range(begin.z, end.z, non_zero_sign(end.z - begin.z)):
                yield ivec3(x, y, z)


def lineToPixelArray(begin: ivec2, end: ivec2, width: int = 1):
    delta = np.array(end - begin)
    maxDelta = int(max(abs(delta)))
    if maxDelta == 0:
        return np.array([])
    pixels = delta[np.newaxis,:] * np.arange(maxDelta + 1)[:,np.newaxis] / maxDelta + np.array(begin)
    pixels = np.rint(pixels).astype(np.signedinteger)

    if width > 1:
        minPixel = np.array([min(end.x, begin.x), min(end.y, begin.y)])

        # convert pixel list to np array
        array = np.zeros((maxDelta + width*2, maxDelta + width*2), dtype=int)
        array[tuple(np.transpose(pixels - minPixel + width))] = 1

        # dilate pixel array (make it THICC)
        if width > 1:
            array = ndimage.binary_dilation(array, iterations = width - 1)

        # rebuild pixel list from array
        pixels = np.argwhere(array) + minPixel - width

    return pixels

def lineToVoxelArray(begin: ivec3, end: ivec3, width: int = 1):
    delta = np.array(end - begin)
    maxDelta = int(max(abs(delta)))
    if maxDelta == 0:
        return np.array([])
    voxels = delta[np.newaxis,:] * np.arange(maxDelta + 1)[:,np.newaxis] / maxDelta + np.array(begin)
    voxels = np.rint(voxels).astype(np.signedinteger)

    if width > 1:
        min_voxel = np.array([min(end.x, begin.x), min(end.y, begin.y), min(end.z, begin.z)])

        # convert pixel list to np array
        array_width = maxDelta + width*2
        array = np.zeros((array_width, array_width, array_width), dtype=int)
        array[tuple(np.transpose(voxels - min_voxel + width))] = 1

        # dilate pixel array (make it THICC)
        if width > 1:
            array = ndimage.binary_dilation(array, iterations = width - 1)

        # rebuild pixel list from array
        voxels = np.argwhere(array) + min_voxel - width

    return voxels


def lineToPixelList(begin: ivec2, end: ivec2, width: int = 1):
    pixelArray = lineToPixelArray(begin, end, width)
    return [ivec2(pixel[0], pixel[1]) for pixel in pixelArray]


def lineToVoxelList(begin: ivec2, end: ivec2, width: int = 1) -> List[ivec3]:
    voxelArray = lineToVoxelArray(begin, end, width)
    return [ivec3(pixel[0], pixel[1], pixel[2]) for pixel in voxelArray]


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
        return self.begin + self.size / 2

    @property
    def inner(self):
        """Generator that yields all points contained in this Rect"""
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
        """Generator that yields this Rect's corner points"""
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

    def toBox(self, offsetY = 0, sizeY = 0):
        """Returns a corresponding Box"""
        return Box(addY(self.offset, offsetY), addY(self.size, sizeY))

    @staticmethod
    def between(cornerA: ivec2, cornerB: ivec2):
        """Returns the Rect between [cornerA] and [cornerB] (both inclusive),
        which may be any opposing corners"""
        first = ivec2(
            cornerA.x if cornerA.x <= cornerB.x else cornerB.x,
            cornerA.y if cornerA.y <= cornerB.y else cornerB.y,
        )
        last = ivec2(
            cornerA.x if cornerA.x > cornerB.x else cornerB.x,
            cornerA.y if cornerA.y > cornerB.y else cornerB.y,
        )
        return Rect(first, last - first + 1)


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
        return self.begin + self.size / 2

    @property
    def inner(self):
        """Generator that yields all points contained in this Box"""
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
        """Generator that yields this Box's corner points"""
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

    def toRect(self):
        """Returns this Box's XZ-plane as a Rect"""
        return Rect(dropY(self.offset), dropY(self.size))

    @staticmethod
    def between(cornerA: ivec3, cornerB: ivec3):
        """Returns the Box between [cornerA] and [cornerB] (both inclusive),
        which may be any opposing corners"""
        first = ivec3(
            cornerA.x if cornerA.x <= cornerB.x else cornerB.x,
            cornerA.y if cornerA.y <= cornerB.y else cornerB.y,
            cornerA.z if cornerA.z <= cornerB.z else cornerB.z,
        )
        last = ivec3(
            cornerA.x if cornerA.x > cornerB.x else cornerB.x,
            cornerA.y if cornerA.y > cornerB.y else cornerB.y,
            cornerA.z if cornerA.z > cornerB.z else cornerB.z,
        )
        return Box(first, last - first + 1)


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
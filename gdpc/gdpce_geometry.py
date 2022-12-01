"""Functions that place blocks in geometrical patterns.

Wraps gdpc v5.0's geometry module to work with vectors, and extends it.
"""


from typing import Optional, Union, List
from dataclasses import dataclass
from glm import ivec3
from gdpc import geometry

from .vector_util import addY, scaleToFlip3D, Rect, Box, boxBetween
from .block import Block
from .gdpce_interface import Interface


# An explanation of why this class is here:
#
# We wrap gdpc.interface with our own Interface class. We have several reasons for doing so, most
# importantly to work with vectors and transforms. However, we also want to use some of
# gdpc.geometry's functions to implement the vector-based geometry functions in this file, rather
# than re-inventing the wheel. The functions from gdpc.geometry use gdpc.interface directly, so they
# do not go through our wrapping Interface class.
#
# Initially, this was not a problem: we would just apply the transform of the passed Interface
# manually and then call the functions from gdpc.geometry using the pre-transformed coordinates,
# pre-stringified block and the Interface's underlying gdpc.interface.
#
# However, to implement some advanced features, we need to have a single point - under our control -
# where all block placements pass through. That is, we want all block placements to go through
# Interface. To achieve this without having to re-implement the functions from gdpc.geometry that we
# use, we use this class. What this class does, is act as if it is a gdpc.interface class for all
# purposes needed by the gdpc.geometry functions (duck typing), while it actually redirects all
# placeBlock calls to Interface.
#
# For this to work, we rely on internal implementation details of gdpc. Therefore, it is essential
# that a specific version of gdpc is used (the one in requirements.txt).
#
# For performance reasons, we still manually apply the transform of the passed Interface and
# manually stringify blocks in the wrapping geometry functions. This way, we only have to do so for
# the corner blocks of the geometrical areas, rather than all of them.
@dataclass
class _HackedGDPCInterface():
    interface: Interface

    # We call the gdpc geometry functions with "block" set to the tuple of values we need here.
    def placeBlock(self, x, y, z, block, replace=None, doBlockUpdates=-1, customFlags=-1):
        self.interface.placeStringGlobal(ivec3(x, y, z), block[0], block[1], block[2], block[3], replace)
        return "0" # Indicates "no error" to gdpc.

    def setBuffering(self, value, notify):
        pass

    def isBuffering(self):
        return True # No need to speak the truth here.


def placeList(itf: Interface, position_list: List[ivec3], block: Block, replace: Optional[Union[str, List[str]]] = None):
    """Places a [block] at each position in [position_list].\n
    Slightly more efficient than calling Interface.placeBlock() in a loop."""
    blockState = block.blockStateString(itf.transform.rotation, scaleToFlip3D(itf.transform.rotation))
    for position in position_list:
        itf.placeStringGlobal(position, itf.transform.scale, block.name, blockState, block.nbt, replace)


def placeLine(itf: Interface, first: ivec3, last: ivec3, block: Block, replace: Optional[Union[str, List[str]]] = None):
    """Places a line of [block] blocks from [first] to [last] (inclusive).\n
    When placing axis-aligned lines, placeCuboid and placeBox are more efficient."""
    globalFirst = itf.transform * first
    globalLast  = itf.transform * last
    geometry.placeLine(
        globalFirst.x, globalFirst.y, globalFirst.z,
        globalLast .x, globalLast .y, globalLast .z,
        (itf.transform.scale, block.name, block.blockStateString(itf.transform.rotation, scaleToFlip3D(itf.transform.scale)), block.nbt),
        replace,
        interface = _HackedGDPCInterface(itf)
    )


# TODO: Add a "wireframe" option, perhaps with another boolean next to [hollow].
def placeCuboid(itf: Interface, first: ivec3, last: ivec3, block: Block, replace: Optional[Union[str, List[str]]] = None, hollow: bool = False):
    """Places a box of [block] blocks from [first] to [last] (inclusive).\n
    If [hollow]=True, the box is hollow, but sides are always filled."""
    globalFirst = itf.transform * first
    globalLast  = itf.transform * last
    geometry.placeCuboid(
        globalFirst.x, globalFirst.y, globalFirst.z,
        globalLast .x, globalLast .y, globalLast .z,
        (itf.transform.scale, block.name, block.blockStateString(itf.transform.rotation, scaleToFlip3D(itf.transform.scale)), block.nbt),
        replace, hollow,
        interface = _HackedGDPCInterface(itf)
    )


def placeBox(itf: Interface, box: Box, block: Block, replace: Optional[Union[str, List[str]]] = None, hollow: bool = False):
    """Places a box of [block] blocks.\n
    If [hollow]=True, the box is hollow, but sides are always filled."""
    if (box.size.x == 0 or box.size.y == 0 or box.size.z == 0): return
    placeCuboid(itf, box.begin, box.end - 1, block, replace, hollow)


def placeRect(itf: Interface, rect: Rect, y: int, block: Block, replace: Optional[Union[str, List[str]]] = None):
    """Places a rectangle of blocks in the XY-plane, at height [y]"""
    if (rect.size.x == 0 or rect.size.y == 0): return
    placeBox(itf, rect.toBox(y, 1), block, replace)


# TODO: Wrap other GDPC geometry functions, just like placeLine and placeCuboid.


def placeRectOutline(itf: Interface, rect: Rect, y: int, block: Block, replace: Optional[Union[str, List[str]]] = None):
    """Places the outline of a rectangle of blocks in the XY-plane, at height [y]"""
    if (rect.size.x == 0 or rect.size.y == 0): return
    with itf.pushTransform(addY(rect.offset, y)):
        placeCuboid(itf, ivec3(            0, 0,             0), ivec3(rect.size.x-1, 0,             0), block, replace)
        placeCuboid(itf, ivec3(rect.size.x-1, 0,             0), ivec3(rect.size.x-1, 0, rect.size.y-1), block, replace)
        placeCuboid(itf, ivec3(rect.size.x-1, 0, rect.size.y-1), ivec3(            0, 0, rect.size.y-1), block, replace)
        placeCuboid(itf, ivec3(            0, 0, rect.size.y-1), ivec3(            0, 0,             0), block, replace)


def placeCornerPillars(itf: Interface, box: Box, block: Block, replace: Optional[Union[str, List[str]]] = None):
    """Places pillars of [block] blocks at the corners of [box]"""
    for corner in box.toRect().corners:
        placeBox(itf, Box(addY(corner, box.offset.y), ivec3(1, box.size.y, 1)), block, replace)


def placeCheckeredCuboid(itf: Interface, first: ivec3, last: ivec3, block1: Block, block2: Block = Block("minecraft:air"), replace: Optional[Union[str, List[str]]] = None):
    """Places a checker pattern of [block1] and [block2] in the box between [first] and [last]
    (inclusive)"""
    placeCheckeredBox(itf, boxBetween(first, last), block1, block2, replace)


def placeCheckeredBox(itf: Interface, box: Box, block1: Block, block2: Block = Block("minecraft:air"), replace: Optional[Union[str, List[str]]] = None):
    """Places a checker pattern of [block1] and [block2] in [box]"""
    # We loop through [box]-local positions so that the pattern start is independent of [box].offset
    for pos in Box(size=box.size).inner:
        itf.placeBlock(box.offset + pos, block1 if sum(pos) % 2 == 0 else block2, replace)


def placeStripedCuboid(itf: Interface, first: ivec3, last: ivec3, stripeAxis: int, block1: Block, block2: Block = Block("minecraft:air"), replace: Optional[Union[str, List[str]]] = None):
    """Places a stripe pattern of [block1] and [block2] along [stripeAxis] (0, 1 or 2) in the box
    between [first] and [last] (inclusive)"""
    placeStripedBox(itf, boxBetween(first, last), stripeAxis, block1, block2, replace)


def placeStripedBox(itf: Interface, box: Box, stripeAxis: int, block1: Block, block2: Block = Block("minecraft:air"), replace: Optional[Union[str, List[str]]] = None):
    """Places a stripe pattern of [block1] and [block2] along [stripeAxis] (0, 1 or 2) in [box]"""
    # We loop through [box]-local positions so that the pattern start is independent of [box].offset
    for pos in Box(size=box.size).inner:
        itf.placeBlock(box.offset + pos, block1 if pos[stripeAxis] % 2 == 0 else block2, replace)

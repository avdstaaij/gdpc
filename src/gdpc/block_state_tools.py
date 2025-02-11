"""Utilities for working with orientation-related block states.

You most likely don't need to use this module directly: block transformations are already handled
by the :class:`.Block` class.
"""


from glm import ivec3, bvec3

from .vector_tools import Vec3iLike, Vec3bLike


# ==================================================================================================
# Listings
# ==================================================================================================


AXIS_VALUES     = ("x", "y", "z")
"""The possible values for the "axis" block state."""

FACING_VALUES   = ("up", "down", "north", "east", "south", "west")
"""The possible values for the "facing" block state."""

ROTATION_VALUES = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15")
"""The possible values for the "rotation" block state."""


# ==================================================================================================
# Conversions between different block states
# ==================================================================================================


__FACING_TO_ROTATION = {
    "south": "0",
    "west":  "4",
    "north": "8",
    "east":  "12",
}
def facingToRotation(facing: str) -> str:
    """Converts ``facing`` to the corresponding "rotation" block state string."""
    return __FACING_TO_ROTATION[facing]


__ROTATION_TO_FACING = {
    "0":  "south",
    "1":  "south",
    "2":  "south",
    "3":  "west",
    "4":  "west",
    "5":  "west",
    "6":  "west",
    "7":  "north",
    "8":  "north",
    "9":  "north",
    "10": "north",
    "11": "east",
    "12": "east",
    "13": "east",
    "14": "east",
    "15": "south",
}
def rotationToFacing(rotation: str) -> str:
    """Converts ``rotation`` to the nearest corresponding "facing" block state string."""
    return __ROTATION_TO_FACING[rotation]


# ==================================================================================================
# String <-> vector conversion functions
# ==================================================================================================


# --------------------------------------------------------------------------------------------------
# Axis


__VECTOR_TO_AXIS = {
    (1,0,0): "x",
    (0,1,0): "y",
    (0,0,1): "z",
}
def vectorToAxis(vec: Vec3iLike) -> str:
    """Returns the "axis" block state string corresponding to the direction vector ``vec``."""
    v = (
        vec[0] != 0,
        vec[1] != 0,
        vec[2] != 0,
    )
    try:
        return __VECTOR_TO_AXIS[v]
    except KeyError as e:
        raise ValueError("Exactly one vector component must be non-zero") from e


__AXIS_TO_VECTOR = {
    "x": ivec3(1,0,0),
    "y": ivec3(0,1,0),
    "z": ivec3(0,0,1),
}
def axisToVector(axis: str) -> ivec3:
    """Returns the direction vector corresponding to the "axis" block state string ``axis``."""
    return __AXIS_TO_VECTOR[axis]


# --------------------------------------------------------------------------------------------------
# Facing


__VECTOR_TO_FACING = {
    ( 0, 0,-1): "north",
    ( 0, 0, 1): "south",
    ( 0,-1, 0): "down",
    ( 0, 1, 0): "up",
    (-1, 0, 0): "west",
    ( 1, 0, 0): "east",
}
def vectorToFacing(vec: Vec3iLike) -> str:
    """Returns the "facing" block state string corresponding to the direction vector ``vec``."""
    v = (
        -1 if vec[0] < 0 else 1 if vec[0] > 0 else 0,
        -1 if vec[1] < 0 else 1 if vec[1] > 0 else 0,
        -1 if vec[2] < 0 else 1 if vec[2] > 0 else 0,
    )
    try:
        return __VECTOR_TO_FACING[v]
    except KeyError as e:
        raise ValueError("Exactly one vector component must be non-zero") from e


__FACING_TO_VECTOR = {
    "north": ivec3( 0, 0,-1),
    "south": ivec3( 0, 0, 1),
    "down":  ivec3( 0,-1, 0),
    "up":    ivec3( 0, 1, 0),
    "west":  ivec3(-1, 0, 0),
    "east":  ivec3( 1, 0, 0),
}
def facingToVector(facing: str) -> ivec3:
    """Returns the direction vector corresponding to the "facing" block state string ``facing``."""
    return __FACING_TO_VECTOR[facing]


# --------------------------------------------------------------------------------------------------
# Rotation


# TODO: vectorToRotation


def rotationToVector(rotation: str) -> ivec3:
    """Returns the axis-aligned direction vector corresponding to ``rotation``."""
    return facingToVector(rotationToFacing(rotation))


# ==================================================================================================
# String transformation functions
# ==================================================================================================


# --------------------------------------------------------------------------------------------------
# Axis


def rotateAxis(axis: str, rotation: int) -> str:
    """Returns the rotated "axis" block state string."""
    strings = ["x", "z"]
    try:
        return strings[(strings.index(axis) + rotation) % 2]
    except ValueError: # if axis == "y"
        return axis


def transformAxis(axis: str, rotation: int = 0) -> str:
    """Returns the transformed "axis" block state string."""
    # Flipping is a no-op for axis strings
    return rotateAxis(axis, rotation)


# --------------------------------------------------------------------------------------------------
# Facing


def rotateFacing(facing: str, rotation: int) -> str:
    """Returns the rotated "facing" block state string."""
    strings = ["north", "east", "south", "west"]
    try:
        return strings[(strings.index(facing) + rotation) % 4]
    except ValueError:
        return facing # up, down


def flipFacing(facing: str, flip: Vec3bLike) -> str:
    """Returns the flipped "facing" block state string."""
    if flip[0]:
        if facing == "east":  return "west"
        if facing == "west":  return "east"
    if flip[1]:
        if facing == "down":  return "up"
        if facing == "up":    return "down"
    if flip[2]:
        if facing == "north": return "south"
        if facing == "south": return "north"
    return facing


def transformFacing(facing: str, rotation: int = 0, flip: Vec3bLike = bvec3()) -> str:
    """Returns the transformed "facing" block state string.\n
    Flips first, rotates second."""
    return rotateFacing(flipFacing(facing, flip), rotation)


__INVERT_FACING = {
    "north": "south",
    "south": "north",
    "down":  "up",
    "up":    "down",
    "west":  "east",
    "east":  "west",
}
def invertFacing(facing: str) -> str:
    """Returns the inverted "facing" block state string."""
    return __INVERT_FACING[facing]


# --------------------------------------------------------------------------------------------------
# Rotation


def rotateRotation(blockStateRotation: str, rotation: int) -> str:
    """Returns the rotated "rotation" block state string.\n
    Yes, this name is confusing. ``blockStateRotation`` denotes a value of the "rotation" block
    state, as used by e.g. signs. ``rotation`` denotes a rotation as used by GDPC's transformation
    system, so one of {0,1,2,3}. This function name is consistent with the other block state
    rotation functions."""
    return str((int(blockStateRotation) + 4*rotation) % 16)


def flipRotation(rotation: str, flip: Vec3bLike) -> str:
    """Returns the flipped "rotation" block state string."""
    rotationInt = int(rotation)
    if flip[0]:
        rotationInt = (16 - rotationInt) % 16
    if flip[2]:
        rotationInt = (8 - rotationInt) % 16
    return str(rotationInt)


def transformRotation(blockStateRotation: str, rotation: int = 0, flip: Vec3bLike = bvec3()) -> str:
    """Returns the transformed "rotation" block state string.\n
    Flips first, rotates second."""
    return rotateRotation(flipRotation(blockStateRotation, flip), rotation)


# --------------------------------------------------------------------------------------------------
# Half


# Note: We transform half="bottom"/"top" (Used by e.g. stairs), but "half" is also used for other
# purposes, (e.g. doors can have half="lower"/"upper"). We make sure to keep those other possible
# values unchanged.


__INVERT_FACING = {
    "bottom": "top",
    "top":    "bottom",
}
def invertHalf(half: str) -> str:
    """Returns the inverted "half" block state string."""
    result = __INVERT_FACING.get(half)
    return result if result is not None else half


def flipHalf(half: str, flip: Vec3bLike) -> str:
    """Returns the flipped "half" block state string."""
    return invertHalf(half) if flip[1] else half


def transformHalf(half: str, flip: Vec3bLike = bvec3()) -> str:
    """Returns the transformed "half" block state string."""
    return flipHalf(half, flip)

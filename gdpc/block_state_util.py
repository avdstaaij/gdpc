"""Utilities for working with orientation-related block state properties"""


from glm import ivec3, bvec3


# ==================================================================================================
# String <-> vector conversion functions
# ==================================================================================================


### Axis


__AXIS_VECTOR_TO_STRING = {
    (1,0,0): "x",
    (0,1,0): "y",
    (0,0,1): "z",
}
def axisVectorToString(vec: ivec3):
    """Returns the "axis" block state string corresponding to the direction vector [vec]"""
    v = (
        vec.x != 0,
        vec.y != 0,
        vec.z != 0,
    )
    try:
        return __AXIS_VECTOR_TO_STRING[v]
    except KeyError as e:
        raise ValueError("axisVectorToString: exactly one vector component must be non-zero") from e


__AXIS_STRING_TO_VECTOR = {
    "x": ivec3(1,0,0),
    "y": ivec3(0,1,0),
    "z": ivec3(0,0,1),
}
def axisStringToVector(axis: str):
    """Returns the direction vector corresponding to the "axis" block state string [axis]"""
    return __AXIS_STRING_TO_VECTOR[axis]


### Facing


__FACING_VECTOR_TO_STRING = {
    ( 0, 0,-1): "north",
    ( 0, 0, 1): "south",
    ( 0,-1, 0): "down",
    ( 0, 1, 0): "up",
    (-1, 0, 0): "west",
    ( 1, 0, 0): "east",
}
def facingVectorToString(vec: ivec3):
    """Returns the "facing" block state string corresponding to the direction vector [vec]"""
    v = (
        -1 if vec[0] < 0 else 1 if vec[0] > 0 else 0,
        -1 if vec[1] < 0 else 1 if vec[1] > 0 else 0,
        -1 if vec[2] < 0 else 1 if vec[2] > 0 else 0,
    )
    try:
        return __FACING_VECTOR_TO_STRING[v]
    except KeyError as e:
        raise ValueError("facingVectorToString: exactly one vector component must be non-zero") from e


__FACING_STRING_TO_VECTOR = {
    "north": ivec3( 0, 0,-1),
    "south": ivec3( 0, 0, 1),
    "down":  ivec3( 0,-1, 0),
    "up":    ivec3( 0, 1, 0),
    "west":  ivec3(-1, 0, 0),
    "east":  ivec3( 1, 0, 0),
}
def facingStringToVector(facing: str):
    """Returns the direction vector corresponding to the "facing" block state string [facing]"""
    return __FACING_STRING_TO_VECTOR[facing]


# ==================================================================================================
# String transformation functions
# ==================================================================================================


### Axis


def rotateXZaxisString(axis: str, rotation: int):
    """Returns the rotated "axis" block state string"""
    strings = ["x", "z"]
    try:
        return strings[(strings.index(axis) + rotation) % 2]
    except ValueError: # if axis == "y"
        return axis


def transformAxisString(axis: str, rotation: int = 0):
    """Returns the transformed "axis" block state string"""
    # Flipping is a no-op for axis strings
    return rotateXZaxisString(axis, rotation)


### Facing


def rotateXZfacingString(facing: str, rotation: int):
    """Returns the rotated "facing" block state string"""
    strings = ["north", "east", "south", "west"]
    try:
        return strings[(strings.index(facing) + rotation) % 4]
    except ValueError:
        return facing # up, down


def flipFacingString(facing: str, flip: bvec3):
    """Returns the flipped "facing" block state string"""
    if flip.x:
        if facing == "east":  return "west"
        if facing == "west":  return "east"
    if flip.y:
        if facing == "down":  return "up"
        if facing == "up":    return "down"
    if flip.z:
        if facing == "north": return "south"
        if facing == "south": return "north"
    return facing


def transformFacingString(facing: str, rotation: int = 0, flip: bvec3 = bvec3()):
    """Returns the transformed "facing" block state string.\n
    Flips first, rotates second."""
    return rotateXZfacingString(flipFacingString(facing, flip), rotation)

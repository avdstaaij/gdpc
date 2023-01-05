"""Provides the Transform class and related functions"""


from abc import ABC
from dataclasses import dataclass, field

from glm import ivec3, bvec3

from .vector_tools import rotateXZ, flipRotationXZ, flipToScale3D, rotateSizeXZ, Box


# ==================================================================================================
# Transform class
# ==================================================================================================


@dataclass
class Transform:
    """Represents a transformation of space.

    When applied to a vector, [flip] is applied first, [rotation] second, and [translation] third.

    Note that only 90-degree rotations in the XZ-plane are supported. Hence, [rotation] should
    be 0, 1, 2 or 3.
    """

    translation: ivec3 = field(default_factory=ivec3)
    rotation:    int   = 0
    flip:        bvec3 = field(default_factory=bvec3)

    def apply(self, vec: ivec3):
        """Applies this transform to [vec].\n
        Equivalent to [self] * [vec]. """
        return rotateXZ(vec * flipToScale3D(self.flip), self.rotation) + self.translation

    def invApply(self, vec: ivec3):
        """Applies the inverse of this transform to [vec].\n
        Faster version of ~[self] * [vec]."""
        return rotateXZ(vec - self.translation, (-self.rotation + 4) % 4) * flipToScale3D(self.flip)

    def compose(self, other: 'Transform'):
        """Returns a transform that applies [self] after [other].\n
        Equivalent to [self] @ [other]. """
        return Transform(
            translation = self.apply(other.translation),
            rotation    = (self.rotation + flipRotationXZ(other.rotation, self.flip)) % 4,
            flip        = bvec3(ivec3(self.flip) ^ ivec3(other.flip))
        )

    def invCompose(self, other: 'Transform'):
        """Returns a transform that applies [self]^-1 after [other].\n
        Faster version of ~[self] @ [other]."""
        return Transform(
            translation = self.invApply(other.translation),
            rotation    = flipRotationXZ((other.rotation - self.rotation + 4) % 4, self.flip),
            flip        = bvec3(ivec3(self.flip) ^ ivec3(other.flip))
        )

    def composeInv(self, other: 'Transform'):
        """Returns a transform that applies [self] after [other]^-1.\n
        Faster version of [self] @ ~[other]."""
        flip = bvec3(ivec3(self.flip) ^ ivec3(other.flip))
        rotation = (self.rotation - flipRotationXZ(other.rotation, flip) + 4) % 4
        return Transform(
            translation = self.translation - rotateXZ(other.translation * flipToScale3D(flip), rotation),
            rotation    = rotation,
            flip        = flip
        )

    def push(self, other: 'Transform'):
        """Adds the effect of [other] to this transform.\n
        Equivalent to [self] @= [other]."""
        self.translation += rotateXZ(other.translation * flipToScale3D(self.flip), self.rotation)
        self.rotation     = (self.rotation + flipRotationXZ(other.rotation, self.flip)) % 4
        self.flip         = bvec3(ivec3(self.flip) ^ ivec3(other.flip))

    def pop(self, other: 'Transform'):
        """The inverse of push. Removes the effect of [other] from this transform.\n
        Faster version of [self] @= ~[other]."""
        self.flip         = bvec3(ivec3(self.flip) ^ ivec3(other.flip))
        self.rotation     = (self.rotation - flipRotationXZ(other.rotation, self.flip) + 4) % 4
        self.translation -= rotateXZ(other.translation * flipToScale3D(self.flip), self.rotation)

    def inverted(self):
        """Equivalent to ~[self]."""
        flip = self.flip # Flip stays unchanged
        rotation = flipRotationXZ((-self.rotation + 4) % 4, flip)
        return Transform(
            translation = - rotateXZ(self.translation * flipToScale3D(self.flip), self.rotation),
            rotation    = rotation,
            flip        = flip
        )

    def invert(self):
        """Faster version of [self] = ~[self]."""
        # Flip stays unchanged
        self.rotation    = flipRotationXZ((-self.rotation + 4) % 4, self.flip)
        self.translation = - rotateXZ(self.translation * flipToScale3D(self.flip), self.rotation)

    def __matmul__(self, other: 'Transform') -> 'Transform':
        return self.compose(other)

    def __mul__(self, vec: ivec3) -> ivec3:
        return self.apply(vec)

    def __imatmul__(self, other: 'Transform'):
        self.push(other)
        return self

    def __invert__(self):
        return self.inverted()


# ==================================================================================================
# TransformLike ABC
# ==================================================================================================


class TransformLike(ABC):
    """An abstract base class. A class is a TransformLike if it is a Transform or if a Transform can
    be constructed with it."""
    @classmethod
    def __subclasshook__(cls, c):
        if isinstance(c, Transform):
            return True
        try:
            _ = Transform(c)
        except Exception: # pylint: disable=broad-except
            return False
        return True


def toTransform(transformLike: TransformLike) -> Transform:
    """Converts <transformLike> to a Transform, interpreting a vector as a translation.

    Functions that take a Transform parameter are very often called with just a translation.
    By taking a transformLike pararameter instead and using this converter, calling such a
    function with just a translation becomes slightly easier. This does however cost a bit
    of performance (for an isinstance call).
    """
    return transformLike if isinstance(transformLike, Transform) else Transform(transformLike)


# ==================================================================================================
# Transform utilities
# ==================================================================================================


def rotatedBoxTransform(box: Box, rotation: int):
    """Returns a transform that maps the box ((0,0,0), size) to [box] under [rotation], where
    size == vector_util.rotateXZScale([box].size, [rotation])."""
    return Transform(
        translation = box.offset + ivec3(
            box.size.x - 1 if rotation in [1, 2] else 0,
            0,
            box.size.z - 1 if rotation in [2, 3] else 0,
        ),
        rotation = rotation
    )


def rotatedBoxTransformAndSize(box: Box, rotation: int):
    """Returns (transform, size) such that [transform] maps the box ((0,0,0), [size]) to [box],
    under [rotation]."""
    return rotatedBoxTransform(box, rotation), rotateSizeXZ(box.size, rotation)


def flippedBoxTransform(box: Box, flip: bvec3):
    """Returns a transform that maps the box ((0,0,0), [box].size) to [box] under [flip]."""
    return Transform(
        translation = box.offset + (box.size - 1) * ivec3(flip),
        flip = flip
    )

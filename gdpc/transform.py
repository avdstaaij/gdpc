"""Provides the Transform class and related functions"""


from typing import Union
from abc import ABC
from dataclasses import dataclass, field

from glm import ivec3, bvec3
import glm

from .vector_util import rotateXZ, rotateXZScale, scaleToFlip3D, Box


# ==================================================================================================
# Transform class
# ==================================================================================================


@dataclass
class Transform:
    """Represents a transformation of space.

    When applied to a vector, [scaling] is applied first, [rotation] second, and [translation]
    third. Negative scales can be used to flip.

    Note that only 90-degree rotations in the XZ-plane are supported. Hence, [rotation] should
    be 0, 1, 2 or 3.

    Also note that only integer scaling is supported. This may cause some unexpected effects,
    such as t1.compose(t2.inverted()) not always being equivalent to t1.composeInv(t2)."""

    translation: ivec3 = field(default_factory=ivec3)
    rotation:    int   = 0
    scale:       ivec3 = field(default_factory=lambda: ivec3(1,1,1))

    @property
    def flip(self):
        """Get or set the flip property (derived from self.scale).\n
        Note that setting actually *sets* the flip property: it does not toggle."""
        return scaleToFlip3D(self.scale)

    @flip.setter
    def flip(self, value: bvec3):
        self.scale = glm.abs(self.scale) * (1 - 2 * ivec3(value))

    def apply(self, vec: ivec3):
        """Applies this transform to [vec].\n
        Equivalent to [self] * [vec]. """
        return rotateXZ(vec * self.scale, self.rotation) + self.translation

    def invApply(self, vec: ivec3):
        """Applies the inverse of this transform to [vec].\n
        Faster version of ~[self] * [vec] that is safer when using non-unit scalings."""
        return rotateXZ(vec - self.translation, (-self.rotation + 4) % 4) / self.scale

    def compose(self, other: 'Transform'):
        """Returns a transform that applies [self] after [other].\n
        Equivalent to [self] @ [other]. """
        return Transform(
            translation = self.apply(other.translation),
            rotation    = (self.rotation + other.rotation) % 4,
            scale       = rotateXZScale(self.scale * other.scale, other.rotation)
        )

    def invCompose(self, other: 'Transform'):
        """Returns a transform that applies [self]^-1 after [other].\n
        Faster version of ~[self] @ [other] that is safer when using non-unit scalings."""
        return Transform(
            translation = self.invApply(other.translation),
            rotation    = (other.rotation - self.rotation + 4) % 4,
            scale       = rotateXZScale(other.scale / self.scale, other.rotation)
        )

    def composeInv(self, other: 'Transform'):
        """Returns a transform that applies [self] after [other]^-1.\n
        Faster version of [self] @ ~[other] that is safer when using non-unit scalings."""
        scale    = rotateXZScale(self.scale / other.scale, other.rotation)
        rotation = (self.rotation - other.rotation + 4) % 4
        return Transform(
            translation = self.translation - rotateXZ(other.translation * scale, rotation),
            rotation    = rotation,
            scale       = scale
        )

    def push(self, other: 'Transform'):
        """Adds the effect of [other] to this transform.\n
        Equivalent to [self] @= [other]."""
        self.translation += rotateXZ(other.translation * self.scale, self.rotation)
        self.rotation     = (self.rotation + other.rotation) % 4
        self.scale        = rotateXZScale(self.scale * other.scale, other.rotation)

    def pop(self, other: 'Transform'):
        """The inverse of push. Removes the effect of [other] from this transform.\n
        Faster version of [self] @= ~[other] that is safer when using non-unit scalings."""
        self.scale        = rotateXZScale(self.scale, other.rotation) / other.scale
        self.rotation     = (self.rotation - other.rotation + 4) % 4
        self.translation -= rotateXZ(other.translation * self.scale, self.rotation)

    def inverted(self):
        """Equivalent to ~[self].\n
        Note that non-unit scalings cannot be inverted: any fractional part is dropped."""
        scale    = rotateXZScale(1 / self.scale, self.rotation)
        rotation = (-self.rotation + 4) % 4
        return Transform(
            translation = rotateXZ(self.translation, rotation) * scale,
            rotation    = rotation,
            scale       = scale
        )

    def invert(self):
        """Faster equivalent of [self] = ~[self].\n
        Note that non-unit scalings cannot be inverted: any fractional part is dropped."""
        self.scale       = rotateXZScale(1 / self.scale, self.rotation)
        self.rotation    = (-self.rotation + 4) % 4
        self.translation = rotateXZ(self.translation, self.rotation) * self.scale

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
    return rotatedBoxTransform(box, rotation), rotateXZScale(box.size, rotation)


def scaledBoxTransform(box: Box, scale: ivec3):
    """Returns a transform that maps the box ((0,0,0), [box].size) to [box] under [scale]."""
    return Transform(
        translation = box.offset + (box.size - 1) * ivec3(scaleToFlip3D(scale)),
        scale = scale
    )


def flippedBoxTransform(box: Box, flip: bvec3):
    """Returns a transform that maps the box ((0,0,0), [box].size) to [box] under [flip]."""
    iflip = ivec3(flip)
    return Transform(
        translation = box.offset + (box.size - 1) * iflip,
        scale = 1 - iflip * 2
    )

"""Provides the :class:`.Transform` class and related functions"""


from __future__ import annotations

from typing import Union
from dataclasses import dataclass

from glm import ivec3, bvec3

from .vector_tools import Vec3iLike, Vec3bLike, rotate3D, flipRotation3D, flipToScale3D, rotateSize3D, Box, Tuple


# ==================================================================================================
# Transform class
# ==================================================================================================


# pylint: disable=protected-access
@dataclass
class Transform:
    """Represents a transformation of space.

    When applied to a vector, ``flip`` is applied first, ``rotation`` second, and ``translation``
    third.

    Note that only the four 90-degree rotations in the XZ-plane are supported. Hence, ``rotation``
    should be 0, 1, 2 or 3. A rotation of 1 rotates (1,0,0) to (0,0,1). In
    :ref:`Minecraft's coordinate system<minecrafts-coordinate-system>`, this is clockwise.
    """

    _translation: ivec3
    _rotation:    int
    _flip:        bvec3

    def __init__(self, translation: Vec3iLike = ivec3(), rotation: int = 0, flip: Vec3bLike = bvec3()) -> None:
        """Constructs a Transform with the given properties."""
        self._translation = ivec3(*translation)
        self._rotation    = rotation
        self._flip        = bvec3(*flip)


    def __repr__(self) -> str:
        return f"Transform(translation={tuple(self._translation)}, rotation={self._rotation}, flip={tuple(self._flip)})"


    @property
    def translation(self) -> ivec3:
        """The translation component of this transform"""
        return self._translation

    @translation.setter
    def translation(self, value: Vec3iLike) -> None:
        self._translation = ivec3(*value)

    @property
    def rotation(self) -> int:
        """The rotation component of this transform"""
        return self._rotation

    @rotation.setter
    def rotation(self, value: int) -> None:
        self._rotation = value % 4

    @property
    def flip(self) -> bvec3:
        """The flip component of this transform"""
        return self._flip

    @flip.setter
    def flip(self, value: Vec3bLike) -> None:
        self._flip = bvec3(*value)


    def apply(self, vec: Vec3iLike) -> ivec3:
        """Applies this transform to ``vec``.\n
        Equivalent to ``self * vec``. """
        return rotate3D(ivec3(*vec) * flipToScale3D(self._flip), self._rotation) + self._translation

    def invApply(self, vec: Vec3iLike) -> ivec3:
        """Applies the inverse of this transform to ``vec``.\n
        Faster version of ``~self * vec``."""
        return rotate3D(ivec3(*vec) - self._translation, (-self._rotation + 4) % 4) * flipToScale3D(self._flip)

    def compose(self, other: 'Transform') -> 'Transform':
        """Returns a transform that applies ``self`` after ``other``.\n
        Equivalent to ``self @ other``. """
        return Transform(
            translation = self.apply(other._translation),
            rotation    = (self._rotation + flipRotation3D(other._rotation, self._flip)) % 4,
            flip        = self._flip ^ other._flip
        )

    def invCompose(self, other: 'Transform') -> 'Transform':
        """Returns a transform that applies ``~self`` after ``other``.\n
        Faster version of ``~self @ other``."""
        return Transform(
            translation = self.invApply(other._translation),
            rotation    = flipRotation3D((other._rotation - self._rotation + 4) % 4, self._flip),
            flip        = self._flip ^ other._flip
        )

    def composeInv(self, other: 'Transform') -> 'Transform':
        """Returns a transform that applies ``self`` after ``~other``.\n
        Faster version of ``self @ ~other``."""
        flip = self._flip ^ other._flip
        rotation = (self._rotation - flipRotation3D(other._rotation, flip) + 4) % 4
        return Transform(
            translation = self._translation - rotate3D(other._translation * flipToScale3D(flip), rotation),
            rotation    = rotation,
            flip        = flip
        )

    def push(self, other: 'Transform') -> None:
        """Adds the effect of ``other`` to this transform.\n
        Equivalent to ``self @= other``."""
        self._translation += rotate3D(other._translation * flipToScale3D(self._flip), self._rotation)
        self._rotation     = (self._rotation + flipRotation3D(other._rotation, self._flip)) % 4
        self._flip         = self._flip ^ other._flip

    def pop(self, other: 'Transform') -> None:
        """The inverse of push. Removes the effect of ``other`` from this transform.\n
        Faster version of ``self @= ~other``."""
        self._flip         = self._flip ^ other._flip
        self._rotation     = (self._rotation - flipRotation3D(other._rotation, self._flip) + 4) % 4
        self._translation -= rotate3D(other._translation * flipToScale3D(self._flip), self._rotation)

    def inverted(self) -> 'Transform':
        """Returns the inversion of this transform.\n
        Equivalent to ``~self``."""
        flip = self._flip # Flip stays unchanged
        rotation = flipRotation3D((-self._rotation + 4) % 4, flip)
        return Transform(
            translation = - rotate3D(self._translation * flipToScale3D(flip), rotation),
            rotation    = rotation,
            flip        = flip
        )

    def invert(self) -> None:
        """Inverts this transform.\n
        Faster version of ``self = ~self``."""
        # Flip stays unchanged
        self._rotation    = flipRotation3D((-self._rotation + 4) % 4, self._flip)
        self._translation = - rotate3D(self._translation * flipToScale3D(self._flip), self._rotation)

    def __matmul__(self, other: 'Transform') -> 'Transform':
        """``@`` operator. Returns a transform that applies ``self`` after ``other``\n
        Equivalent to ``self.compose(other)``"""
        return self.compose(other)

    def __mul__(self, vec: Vec3iLike) -> ivec3:
        """``*`` operator. Applies this transform to ``vec``\n
        Equivalent to ``self.apply(vec)``"""
        return self.apply(vec)

    def __imatmul__(self, other: 'Transform') -> 'Transform':
        """``@=`` operator. Adds the effect of ``other`` to this transform.\n
        Equivalent to ``self.push(other)``"""
        self.push(other)
        return self

    def __invert__(self) -> 'Transform':
        """``~`` operator. Returns the inversion of this transform.\n
        Equivalent to ``self.inverted()``."""
        return self.inverted()


# ==================================================================================================
# TransformLike
# ==================================================================================================


TransformLike = Union[Transform, Vec3iLike]
"""A class is a TransformLike if it is a :class:`.Transform` or a :class:`.Vec3iLike`, the latter
being interpreted as a translation."""


def toTransform(transformLike: TransformLike) -> Transform:
    """Converts ``transformLike`` to a :class:`.Transform`, interpreting a vector as a translation.

    This function is mainly for internal use in GDPC, but may also be useful in user programs.

    Functions that take a Transform parameter are very often called with just a translation.
    By taking a TransformLike pararameter instead and using this converter, calling such a
    function with just a translation becomes slightly easier. This does however cost a bit
    of performance (for an ``isinstance`` call).
    """
    return transformLike if isinstance(transformLike, Transform) else Transform(transformLike)


# ==================================================================================================
# Transform utilities
# ==================================================================================================


def rotatedBoxTransform(box: Box, rotation: int) -> Transform:
    """Returns a transform that maps the box ``((0,0,0), size)`` to ``box`` under ``rotation``,
    where :python:`size == vector_tools.rotateSize3D(box.size, rotation)`."""
    return Transform(
        translation = box.offset + ivec3(
            box.size.x - 1 if rotation in [1, 2] else 0,
            0,
            box.size.z - 1 if rotation in [2, 3] else 0,
        ),
        rotation = rotation
    )


def rotatedBoxTransformAndSize(box: Box, rotation: int) -> Tuple[Transform, ivec3]:
    """Returns ``(transform, size)`` such that ``transform`` maps the box ``((0,0,0), size)`` to
    ``box``, under ``rotation``."""
    return rotatedBoxTransform(box, rotation), rotateSize3D(box.size, rotation)


def flippedBoxTransform(box: Box, flip: Vec3bLike) -> Transform:
    """Returns a transform that maps the box ``((0,0,0), box.size)`` to ``box`` under ``flip``."""
    return Transform(
        translation = box.offset + (box.size - 1) * ivec3(*flip),
        flip = flip
    )

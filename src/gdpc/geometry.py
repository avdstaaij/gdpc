"""Tools for placing geometrical shapes of blocks.

For nearly every function defined in this module, there is also an equivalent function
in :mod:`.vector_tools` that generates the points of the shape without placing any blocks.
"""


from typing import Optional, Sequence, Union, List, Iterable

from .vector_tools import Vec2iLike, Vec3iLike, Rect, Box, cylinder, fittingCylinder, fittingEllipsoid, fittingSphere, line3D, lineSequence3D, ellipsoid
from .block import Block, transformedBlockOrPalette
from .editor import Editor


def placeCuboid(editor: Editor, first: Vec3iLike, last: Vec3iLike, block: Union[Block, Sequence[Block]], replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a box of ``block`` blocks from ``first`` to ``last`` (inclusive).\n
    To get only the points of this shape, see :func:`.loop3D`, :func:`.cuboid3D` or :attr:`.Box.inner`."""
    # Transform only the key points instead of all points
    first = editor.transform * first
    last = editor.transform * last
    block = transformedBlockOrPalette(block, editor.transform.rotation, editor.transform.flip)
    editor.placeBlockGlobal(Box.between(first, last).inner, block, replace)


def placeCuboidHollow(editor: Editor, first: Vec3iLike, last: Vec3iLike, block: Union[Block, Sequence[Block]], replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a hollow box of ``block`` blocks from ``first`` to ``last`` (inclusive).\n
    To get only the points of this shape, see :attr:`.Box.shell`."""
    # Transform only the key points instead of all points
    first = editor.transform * first
    last = editor.transform * last
    block = transformedBlockOrPalette(block, editor.transform.rotation, editor.transform.flip)
    editor.placeBlockGlobal(Box.between(first, last).shell, block, replace)


def placeCuboidWireframe(editor: Editor, first: Vec3iLike, last: Vec3iLike, block: Union[Block, Sequence[Block]], replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a wireframe of ``block`` blocks from ``first`` to ``last`` (inclusive).\n
    To get only the points of this shape, see :attr:`.Box.wireframe`."""
    # Transform only the key points instead of all points
    first = editor.transform * first
    last = editor.transform * last
    block = transformedBlockOrPalette(block, editor.transform.rotation, editor.transform.flip)
    editor.placeBlockGlobal(Box.between(first, last).wireframe, block, replace)


def placeBox(editor: Editor, box: Box, block: Union[Block, Sequence[Block]], replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a box of ``block`` blocks.\n
    To get only the points of this shape, see :func:`.loop3D`, :func:`.cuboid3D` or :attr:`.Box.inner`."""
    if (box.size.x == 0 or box.size.y == 0 or box.size.z == 0): return
    placeCuboid(editor, box.begin, box.end - 1, block, replace)


def placeBoxHollow(editor: Editor, box: Box, block: Union[Block, Sequence[Block]], replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a hollow box of ``block`` blocks.\n
    To get only the points of this shape, see :attr:`.Box.shell`."""
    if (box.size.x == 0 or box.size.y == 0 or box.size.z == 0): return
    placeCuboidHollow(editor, box.begin, box.end - 1, block, replace)


def placeBoxWireframe(editor: Editor, box: Box, block: Union[Block, Sequence[Block]], replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a wireframe of ``block`` blocks.\n
    To get only the points of this shape, see :attr:`.Box.wireframe`."""
    if (box.size.x == 0 or box.size.y == 0 or box.size.z == 0): return
    placeCuboidWireframe(editor, box.begin, box.end - 1, block, replace)


def placeRect(editor: Editor, rect: Rect, y: int, block: Union[Block, Sequence[Block]], replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a rectangle of blocks in the XY-plane, at height ``y``.\n
    To get only the points of this shape, see :func:`.loop2D`, :func:`.cuboid2D` or :attr:`.Rect.inner` (each with :func:`.addY`)."""
    placeBox(editor, rect.toBox(y, 1), block, replace)


def placeRectOutline(editor: Editor, rect: Rect, y: int, block: Union[Block, Sequence[Block]], replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places the outline of a rectangle of blocks in the XZ-plane, at height ``y``\n
    To get only the points of this shape, see :attr:`.Rect.outline` (with :func:`.addY`) or :meth:`.Rect.toBox` with :attr:`.Box.wireframe`."""
    placeBoxWireframe(editor, rect.toBox(y, 1), block, replace)


def placeCheckeredCuboid(editor: Editor, first: Vec3iLike, last: Vec3iLike, block1: Block, block2: Block = Block(None), replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a checker pattern of ``block1`` and ``block2`` in the box between ``first`` and ``last`` (inclusive)."""
    placeCheckeredBox(editor, Box.between(first, last), block1, block2, replace)


def placeCheckeredBox(editor: Editor, box: Box, block1: Block, block2: Block = Block(None), replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a checker pattern of ``block1`` and ``block2`` in ``box``."""
    # We loop through [box]-local positions so that the pattern start is independent of [box].offset
    for pos in Box(size=box.size).inner:
        editor.placeBlock(box.offset + pos, block1 if sum(pos) % 2 == 0 else block2, replace)


def placeStripedCuboid(editor: Editor, first: Vec3iLike, last: Vec3iLike, block1: Block, block2: Block = Block(None), axis: int = 0, replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a stripe pattern of ``block1`` and ``block2`` along ``axis`` (0, 1 or 2) in the box
    between ``first`` and ``last`` (inclusive)."""
    placeStripedBox(editor, Box.between(first, last), block1, block2, axis, replace)


def placeStripedBox(editor: Editor, box: Box, block1: Union[Block, Sequence[Block]], block2: Union[Block, Sequence[Block]] = Block(None), axis: int = 0, replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a stripe pattern of ``block1`` and ``block2`` along ``axis`` (0, 1 or 2) in ``box``."""
    # We loop through [box]-local positions so that the pattern start is independent of [box].offset
    for pos in Box(size=box.size).inner:
        editor.placeBlock(box.offset + pos, block1 if pos[axis] % 2 == 0 else block2, replace)


def placeLine(editor: Editor, first: Vec3iLike, last: Vec3iLike, block: Union[Block, Sequence[Block]], width=1, replace: Optional[Union[str, List[str]]] = None) -> None:
    """Places a line of ``block`` blocks from ``first`` to ``last`` (inclusive).\n
    To get only the points of this shape, see :func:`.line3D`.\n
    When placing axis-aligned lines, placeCuboid and placeBox are more efficient."""
    # Transform only the key points instead of all points
    first = editor.transform * first
    last = editor.transform * last
    block = transformedBlockOrPalette(block, editor.transform.rotation, editor.transform.flip)
    editor.placeBlockGlobal(line3D(first, last, width), block, replace)


def placeLineSequence(editor: Editor, points: Iterable[Vec3iLike], block: Union[Block, Sequence[Block]], closed=False, replace: Optional[Union[str, List[str]]] = None) -> None:
    """Place lines that run from point to point.\n
    To get only the points of this shape, see :func:`.lineSequence3D`."""
    editor.placeBlock(lineSequence3D(points, closed=closed), block, replace)


def placeCylinder(
    editor: Editor,
    baseCenter: Vec3iLike, diameters: Union[Vec2iLike, int], length: int,
    block: Union[Block, Sequence[Block]],
    axis=1, tube=False, hollow=False,
    replace: Optional[Union[str, List[str]]] = None
) -> None:
    """Place blocks in the shape of a cylinder with the specified properties.\n
    To get only the points of this shape, see :func:`.cylinder`."""
    editor.placeBlock(cylinder(baseCenter, diameters, length, axis, tube, hollow), block, replace)


def placeFittingCylinder(
    editor: Editor,
    corner1: Vec3iLike, corner2: Vec3iLike,
    block: Union[Block, Sequence[Block]],
    axis=1, tube=False, hollow=False,
    replace: Optional[Union[str, List[str]]] = None
) -> None:
    """Place blocks in the shape of the largest cylinder that fits between ``corner1`` and ``corner2``.\n
    To get only the points of this shape, see :func:`.fittingCylinder`."""
    # Transform only the key points instead of all points
    corner1 = editor.transform * corner1
    corner2 = editor.transform * corner2
    block = transformedBlockOrPalette(block, editor.transform.rotation, editor.transform.flip)
    editor.placeBlockGlobal(fittingCylinder(corner1, corner2, axis, tube, hollow), block, replace)


def placeSphere(
    editor: Editor,
    center: Vec3iLike,
    diameter: int,
    block: Union[Block, Sequence[Block]],
    hollow: bool = False,
    replace: Optional[Union[str, List[str]]] = None
) -> None:
    """Places blocks in the shape of a sphere with the specified properties.\n
    To get only the points of this shape, see :func:`.sphere`."""
    editor.placeBlock(ellipsoid(center, (diameter, diameter, diameter), hollow), block, replace)


def placeFittingSphere(
    editor: Editor,
    corner1: Vec3iLike, corner2: Vec3iLike,
    block: Union[Block, Sequence[Block]],
    hollow: bool = False,
    replace: Optional[Union[str, List[str]]] = None
) -> None:
    """Place blocks in the shape of the largest sphere that fits between ``corner1`` and ``corner2``.\n
    To get only the points of this shape, see :func:`.fittingSphere`."""
    # Transform only the key points instead of all points
    corner1 = editor.transform * corner1
    corner2 = editor.transform * corner2
    block = transformedBlockOrPalette(block, editor.transform.rotation, editor.transform.flip)
    editor.placeBlockGlobal(fittingSphere(corner1, corner2, hollow), block, replace)


def placeEllipsoid(
    editor: Editor,
    center: Vec3iLike,
    diameters: Vec3iLike,
    block: Union[Block, Sequence[Block]],
    hollow: bool = False,
    replace: Optional[Union[str, List[str]]] = None
) -> None:
    """Place blocks in the shape of an ellipsoid with the specified properties.\n
    To get only the points of this shape, see :func:`.ellipsoid`."""
    editor.placeBlock(ellipsoid(center, diameters, hollow), block, replace)


def placeFittingEllipsoid(
    editor: Editor,
    corner1: Vec3iLike, corner2: Vec3iLike,
    block: Union[Block, Sequence[Block]],
    hollow: bool = False,
    replace: Optional[Union[str, List[str]]] = None
) -> None:
    """Place blocks in the shape of the largest ellipsoid that fits between ``corner1`` and ``corner2``.\n
    To get only the points of this shape, see :func:`.fittingEllipsoid`."""
    # Transform only the key points instead of all points
    corner1 = editor.transform * corner1
    corner2 = editor.transform * corner2
    block = transformedBlockOrPalette(block, editor.transform.rotation, editor.transform.flip)
    editor.placeBlockGlobal(fittingEllipsoid(corner1, corner2, hollow), block, replace)

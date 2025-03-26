"""Provides the :class:`.Editor` class, which provides high-level functions to interact with the
Minecraft world through the GDMC HTTP interface."""


from __future__ import annotations

from typing import Dict, Sequence, Union, Optional, List, Iterable, Generator, Sized, Any, cast
from numbers import Integral
from contextlib import contextmanager
from copy import copy, deepcopy
import random
from concurrent import futures
import logging
import atexit
import weakref

import numpy as np
import numpy.typing as npt
from pyglm.glm import ivec3

from .utils import eagerAll, OrderedByLookupDict
from .vector_tools import Vec3iLike, Rect, Box, dropY
from .transform import Transform, TransformLike, toTransform
from .block import Block, transformedBlockOrPalette
from . import interface
from .world_slice import WorldSlice


logger = logging.getLogger(__name__)


class Editor:
    """Provides high-level functions to interact with the Minecraft world through the GDMC HTTP
    interface.

    Stores various settings, resources, buffers and caches related to world interaction, and a
    transform that defines a local coordinate system.
    """

    def __init__(
        self,
        transformLike         : Optional[TransformLike] = None,
        dimension             : Optional[str]           = None,
        buffering             : bool                    = False,
        bufferLimit           : int                     = 1024,
        caching               : bool                    = False,
        cacheLimit            : int                     = 8192,
        multithreading        : bool                    = False,
        multithreadingWorkers : int                     = 1,
        retries               : int                     = 4,
        timeout               : Optional[float]         = None,
        host                  : str                     = interface.DEFAULT_HOST,
    ) -> None:
        """Constructs an Editor instance with the specified transform and settings.

        All settings specified here can be accessed and modified through properties with the same
        name. For more information on each setting, see the documentation for the corresponding
        property."""
        self._retries = retries
        self._timeout = timeout
        self._host    = host

        self._transform = Transform() if transformLike is None else toTransform(transformLike)

        self._dimension = dimension

        self._buffering = buffering
        self._bufferLimit = bufferLimit
        self._buffer: Dict[ivec3,Block] = {}
        self._commandBuffer: List[str] = []

        self._caching = caching
        self._cache = OrderedByLookupDict[ivec3,Block](cacheLimit)

        self._multithreading = False
        self._multithreadingWorkers = multithreadingWorkers
        self.multithreading = multithreading # The property setter initializes the multithreading system.
        self._bufferFlushFutures: List[futures.Future[None]] = []

        self._doBlockUpdates = True
        self._spawnDrops     = False
        self._bufferDoBlockUpdates = self._doBlockUpdates
        self._bufferSpawnDrops     = self._spawnDrops

        self._worldSlice: Optional[WorldSlice] = None
        self._worldSliceDecay: Optional[npt.NDArray[np.bool_]] = None

        # We need to do some cleanup when the Editor gets deleted or when the program ends. In
        # particular, we need to flush the block buffer and await any remaining buffer flush
        # futures.
        #
        # The standard way to do this would be to put the cleanup code in __del__. But while this
        # works for the editor-gets-deleted case, it does not work reliably for the program-ends
        # case. __del__ does get called at program exit, but only when the interpreter is already
        # half-shut-down. At that point, we can no longer send HTTP requests or schedule additional
        # futures, so buffer flushing doesn't work anymore.
        #
        # One way to solve this would be to make Editor a context manager, but that would make it
        # slightly harder to use (and it would be a breaking change). Instead, we solve it using an
        # atexit handler. These get called early enough for buffer flushing to still work.
        #
        # We have to be careful about a few things:
        # - We must use a weak reference to refer to the Editor. A normal reference would keep the
        #   Editor alive and prevent the atexit handler from ever getting called.
        # - We must create a new callable object for each Editor, so that when we unregister the
        #   atexit handler, we only unregister the handler for the Editor that registered it. We
        #   accomplish this using a lambda.
        # - We need to store the lambda so that we can unregister it in __del__ and avoid a double
        #   cleanup.

        ref = weakref.ref(cast(Editor, self))
        self._clean_up_handler = lambda: Editor._clean_up_at_exit(ref)
        atexit.register(self._clean_up_handler)


    @staticmethod
    def _clean_up(editor: Editor) -> None:
        """The real Editor destructor, called from both __del__ and the atexit handler."""
        editor.flushBuffer()
        editor.awaitBufferFlushes()


    @staticmethod
    def _clean_up_at_exit(editor_weakref: weakref.ref[Editor]) -> None:
        editor = editor_weakref()
        if editor is not None:
            Editor._clean_up(editor)


    def __del__(self) -> None:
        """Cleans up this Editor instance.\n
        Flushes the block buffer and waits for any remaining buffer flush futures.
        """
        atexit.unregister(self._clean_up_handler)
        Editor._clean_up(self)


    @property
    def transform(self) -> Transform:
        """This editor's local coordinate transform.

        Many of ``Editor``'s methods have a ``position`` parameter. In most cases, the passed
        position vector is interpreted as relative to the coordinate system defined by this
        property.
        For example, :python:`editor.placeBlock(pos, block)` would place ``block`` at
        :python:`editor.transform * pos`.
        Changing this property allows you to change the "point of view" of the editor.

        For a more comprehensive overview of GDPC's transformation system, see
        :ref:`here<the-transformation-system>`."""
        return self._transform

    @transform.setter
    def transform(self, value: TransformLike) -> None:
        self._transform = toTransform(value)

    @property
    def dimension(self) -> Optional[str]:
        """The Minecraft dimension this editor interacts with.

        Can be set to any string, though specifying an invalid dimension may cause other ``Editor``
        methods to raise exceptions. See the documentation of the GDMC HTTP interface mod for the
        full list of options. The following options are certainly supported:

        * ``"overworld"``
        * ``"the_nether"``
        * ``"the_end"``
        * ``"nether"``
        * ``"end"``

        Changing the dimension will flush the block buffer and invalidate all caches.\n
        Note that :attr:`.transform` is NOT reset or modified when the dimension is changed! In
        particular, the transform's translation (if any) is NOT adjusted for the nether's 8x smaller
        scale."""
        return self._dimension

    @dimension.setter
    def dimension(self, value: Optional[str]) -> None:
        if value != self._dimension:
            self.flushBuffer()
            self._cache.clear()
            self._worldSlice      = None
            self._worldSliceDecay = None
        self._dimension = value

    @property
    def buffering(self) -> bool:
        """Whether block placement buffering is enabled.

        When buffering is enabled, blocks passed to :meth:`.placeBlock`/:meth:`.placeBlockGlobal`
        are not placed immediately, but are instead added to a buffer. When the buffer is full
        (:attr:`bufferLimit`), all blocks are then placed at once, using a single HTTP request.

        The block retrieval functions (such as :meth:`.getBlock`) take the buffer into account:
        if the buffer contains a block at the specified position, that block is returned.
        If both buffering and caching (see :attr:`caching`) are enabled, the buffer supersedes the
        cache for block retrieval.

        Note that, if the Minecraft world is changed by something other than the buffering
        ``Editor`` (for example, by a player on the server) after blocks have been buffered but
        before they have been placed, then the buffered blocks may overwrite those changes.

        To manually flush the buffer, call :meth:`.flushBuffer`.
        """
        # TODO: document that the buffer gets flushed in __del__? That method is unreliable though
        # (#68), so we should probably fix it first rather than explain the unreliability.
        return self._buffering

    @buffering.setter
    def buffering(self, value: bool) -> None:
        if self.buffering and not value:
            self.flushBuffer()
        self._buffering = value

    @property
    def bufferLimit(self) -> int:
        """Size of the block buffer (see :attr:`.buffering`)."""
        return self._bufferLimit

    @bufferLimit.setter
    def bufferLimit(self, value: int) -> None:
        self._bufferLimit = value
        if len(self._buffer) >= self.bufferLimit:
            self.flushBuffer()

    @property
    def caching(self) -> bool:
        """Whether caching placed and retrieved blocks is enabled.

        When caching is enabled, the last :attr:`cacheLimit` placed and retrieved blocks and their
        positions are cached in this ``Editor`` object. If a block at a cached position is accessed
        (such as with :meth:`.getBlock`), the block is retrieved from the cache, and no HTTP request
        is sent.

        If both buffering (see :attr:`buffering`) and caching are enabled, the buffer supersedes the
        cache for block retrieval.

        Note that, if the Minecraft world is modified by something other than the caching
        ``Editor`` (for example, by a player on the server), the cache will not reflect those
        changes, and retrieved blocks may be incorrect.
        """
        return self._caching

    @caching.setter
    def caching(self, value: bool) -> None:
        self._caching = value

    @property
    def cacheLimit(self) -> int:
        """Size of the block cache (see :attr:`.caching`)."""
        return self._cache.maxSize

    @cacheLimit.setter
    def cacheLimit(self, value: int) -> None:
        self._cache.maxSize = value

    @property
    def multithreading(self) -> bool:
        """Whether multithreaded buffer flushing is enabled."""
        return self._multithreading

    @multithreading.setter
    def multithreading(self, value: bool) -> None:
        if not self._multithreading and value:
            self._bufferFlushExecutor = futures.ThreadPoolExecutor(self._multithreadingWorkers)
            if self._multithreadingWorkers > 1:
                logger.warning(
                    "Multithreading with more than one worker thread.\n"
                    "An editor has been set to use multithreaded buffer flushing with more than one\n"
                    "worker thread.\n"
                    "The editor can no longer guarantee that blocks will be placed in the same order\n"
                    "as they were sent. If buffering or caching is used, this can also cause the\n"
                    "caches to become inconsistent with the actual world.\n"
                    "Multithreading with more than one worker thread can speed up block placement on\n"
                    "some machines, which can be nice during development, but it is NOT RECOMMENDED\n"
                    "for production code."
                )
        elif self._multithreading and not value:
            self._bufferFlushExecutor.shutdown(wait=True)
            del self._bufferFlushExecutor
        self._multithreading = value

    @property
    def multithreadingWorkers(self) -> int:
        """The amount of buffer flush worker threads."""
        return self._multithreadingWorkers

    @multithreadingWorkers.setter
    def multithreadingWorkers(self, value: int) -> None:
        restartExecutor = self.multithreading and self._multithreadingWorkers != value
        self._multithreadingWorkers = value
        if restartExecutor:
            self.multithreading = False
            self.multithreading = True

    @property
    def doBlockUpdates(self) -> bool:
        """Whether placed blocks receive a block update.

        When a player places a block in Minecraft, that block and its surrounding blocks receive a
        block update.* This triggers effects such as sand blocks falling and fences adjusting their
        shape.

        If this setting is ``True``, blocks placed with
        :meth:`.placeBlock`/:meth:`.placeBlockGlobal` will be given a block update, just like if
        they were placed by a player. We recommend leaving this on in most cases.

        \\*: The system is actually a bit more complex than this.
        See https://minecraft.wiki/w/Block_update for the full details.
        """
        return self._doBlockUpdates

    @doBlockUpdates.setter
    def doBlockUpdates(self, value: bool) -> None:
        if self.buffering and value != self._doBlockUpdates:
            self.flushBuffer()
        self._doBlockUpdates = value

    @property
    def spawnDrops(self) -> bool:
        """Whether overwritten blocks drop items.

        If ``True``, overwritten blocks drop as items (as if they were destroyed with a
        Silk Touch* tool).
        Blocks with an inventory (e.g. chests) will drop their inventory as well.

        Note that if this is ``False`` but `:attr:`.doBlockUpdates` is ``True``, overwriting a block
        may still cause a different block to break and drop as an item. For example, if a block with
        a torch on its side is removed, the torch will drop.
        """
        return self._spawnDrops

    @spawnDrops.setter
    def spawnDrops(self, value: bool) -> None:
        if self.buffering and value != self._spawnDrops:
            self.flushBuffer()
        self._spawnDrops = value

    @property
    def retries(self) -> int:
        """The amount of retries for requests to the GDMC HTTP interface.

        If a request to the interface fails, it will be retried this many times
        (1 + this value in total) before an exception is thrown.
        """
        return self._retries

    @retries.setter
    def retries(self, value: int) -> None:
        self._retries = value

    @property
    def timeout(self) -> Optional[float]:
        """The timeout for requests to the GDMC HTTP interface

        Behaves as described by the
        `requests package <https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts>`_).
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: Optional[float]) -> None:
        self._timeout = value

    @property
    def host(self) -> str:
        """The address (hostname+port) of the GDMC HTTP interface to use.\n
        Changing the host will flush the buffer and invalidate all caches.\n
        Note that the :attr:`.transform` is NOT reset or modified when the host is changed!"""
        return self._host

    @host.setter
    def host(self, value: str) -> None:
        if value != self._host:
            self.flushBuffer()
            self.awaitBufferFlushes()
            self._cache.clear()
            self._worldSlice      = None
            self._worldSliceDecay = None
        self._host = value

    @property
    def worldSlice(self) -> Optional[WorldSlice]:
        """The cached WorldSlice (see :meth:`.loadWorldSlice`)."""
        return self._worldSlice

    @property
    def worldSliceDecay(self) -> Optional[npt.NDArray[np.bool_]]:
        """3D boolean array indicating whether the block at the specified position in the cached
        worldSlice is still valid.\n
        Note that the lowest Y-layer is at ``[:,0,:]``, despite Minecraft's negative Y coordinates.
        If :attr:`.worldSlice` is ``None``, this property will also be ``None``."""
        if self._worldSliceDecay is None:
            return None
        view = self._worldSliceDecay.view()
        view.flags.writeable = False
        return view


    def runCommand(self, command: str, position: Optional[Vec3iLike] = None, syncWithBuffer: bool = False) -> None:
        """Executes one or multiple Minecraft commands (separated by newlines).\n
        The leading "/" must be omitted.\n
        If buffering is enabled and ``syncWithBuffer`` is ``True``, the command is deferred until
        after the next buffer flush. This can be useful if the command depends on possibly buffered
        block changes.\n
        If ``position`` is provided, the command's execution position is set to ``position``, where
        ``position`` is interpreted as local to :attr:`.transform`.
        This means that, for example, the position "~ ~ ~" in the command will correspond to
        ``position``. Note however that any rotation or flip performed by :attr:`.transform` is NOT
        reflected in the command's execution context! This means that the use of local coordinate
        offsets (e.g. "^1 ^2 ^3") is in general not safe.
        For more details about relative and local command coordinates, see
        https://minecraft.wiki/Coordinates#Commands"""
        if position is not None:
            position = self.transform * position
        self.runCommandGlobal(command, position, syncWithBuffer)


    def runCommandGlobal(self, command: str, position: Optional[Vec3iLike] = None, syncWithBuffer: bool = False) -> None:
        """Executes one or multiple Minecraft commands (separated by newlines), ignoring :attr:`.transform`.\n
        The leading "/" must be omitted.\n
        If buffering is enabled and ``syncWithBuffer`` is ``True``, the command is deferred until
        after the next buffer flush. This can be useful if the command depends on possibly buffered
        block changes.\n
        If ``position`` is provided, the command's execution position is set to ``position``,
        ignoring :attr:`.transform`.
        This means that, for example, the position "~ ~ ~" in the command will correspond to
        ``position``.
        For more details about relative and local command coordinates, see
        https://minecraft.wiki/Coordinates#Commands"""
        if position is not None:
            command = f"execute positioned {' '.join(str(c) for c in position)} run {command}"

        if self.buffering and syncWithBuffer:
            self._commandBuffer.append(command)
            return
        result = interface.runCommand(command, dimension=self.dimension, retries=self.retries, timeout=self.timeout, host=self.host)
        if not result[0][0]:
            logger.error("Server returned error upon running command:\n  %s", result[0][1])


    def getBuildArea(self) -> Box:
        """Returns the build area that was specified by ``/setbuildarea`` in-game.\n
        The build area is always in **global coordinates**; :attr:`.transform` is ignored."""
        return interface.getBuildArea(retries=self.retries, timeout=self.timeout, host=self.host)


    def setBuildArea(self, buildArea: Box) -> Box:
        """Sets the build area to ``buildArea``, and returns it.\n
        The build area must be given in **global coordinates**; :attr:`.transform` is ignored."""
        self.runCommandGlobal(f"setbuildarea {buildArea.begin.x} {buildArea.begin.y} {buildArea.begin.z} {buildArea.end.x} {buildArea.end.y} {buildArea.end.z}")
        return self.getBuildArea()


    def getBlock(self, position: Vec3iLike) -> Block:
        """Returns the block at ``position``.\n
        ``position`` is interpreted as local to the coordinate system defined by :attr:`.transform`.
        The returned block's orientation is also from the perspective of :attr:`.transform`.\n
        If the given coordinates are invalid, returns ``Block("minecraft:void_air")``."""
        block = self.getBlockGlobal(self.transform * position)
        invTransform = ~self.transform
        block.transform(invTransform.rotation, invTransform.flip)
        return block


    def getBlockGlobal(self, position: Vec3iLike) -> Block:
        """Returns the block at ``position``, ignoring :attr:`.transform`.\n
        If the given coordinates are invalid, returns ``Block("minecraft:void_air")``."""
        _position = ivec3(*position)

        if self.caching:
            block = self._cache.get(_position)
            if block is not None:
                return copy(block)

        if self.buffering:
            block = self._buffer.get(_position)
            if block is not None:
                return copy(block)

        if (
            self._worldSlice is not None and
            self._worldSlice.box.contains(_position) and
            not cast(npt.NDArray[np.bool_], self._worldSliceDecay)[tuple(_position - self._worldSlice.box.offset)]
        ):
            block = self._worldSlice.getBlockGlobal(_position)
        else:
            block = interface.getBlocks(_position, dimension=self.dimension, includeState=True, includeData=True, retries=self.retries, timeout=self.timeout, host=self.host)[0][1]

        if self.caching:
            self._cache[_position] = copy(block)

        return block


    def getBiome(self, position: Vec3iLike) -> str:
        """Returns the biome at ``position``.\n
        ``position`` is interpreted as local to the coordinate system defined by :attr:`.transform`.\n
        If the given coordinates are invalid, returns an empty string."""
        return self.getBiomeGlobal(self.transform * position)


    def getBiomeGlobal(self, position: Vec3iLike) -> str:
        """Returns the biome at ``position``, ignoring :attr:`.transform`.\n
        If the given coordinates are invalid, returns an empty string."""
        if (
            self._worldSlice is not None and
            self._worldSlice.box.contains(position) and
            not cast(npt.NDArray[np.bool_], self._worldSliceDecay)[tuple(ivec3(*position) - self._worldSlice.box.offset)]
        ):
            return self._worldSlice.getBiomeGlobal(position)

        return interface.getBiomes(position, dimension=self.dimension, retries=self.retries, timeout=self.timeout, host=self.host)[0][1]


    def placeBlock(
        self,
        position: Union[Vec3iLike, Iterable[Vec3iLike]],
        block:    Union[Block, Sequence[Block]],
        replace:  Optional[Union[str, List[str]]] = None
    ) -> bool:
        """Places ``block`` at ``position``.\n
        ``position`` is interpreted as local to the coordinate system defined by :attr:`.transform`.\n
        If ``position`` is iterable (e.g. a list), ``block`` is placed at all positions.
        This is more efficient than calling this method in a loop.\n
        If ``block`` is a sequence (e.g. a list), blocks are sampled randomly.\n
        Returns whether the placement succeeded fully."""
        # Distinguishing between Vec3iLike and Iterable[Vec3iLike] is... not easy.
        # Perhaps we should add a differently-named function for placing multiple blocks instead.
        # (This would be a breaking change.)
        globalPosition = (
            self.transform * cast(Vec3iLike, position)
            if (
                hasattr(position, "__len__")
                and len(cast(Sized, position)) == 3
                and hasattr(position, "__getitem__")
                and isinstance(cast(Sequence[Any], position)[0], Integral)
            )
            else (self.transform * pos for pos in cast(Iterable[Vec3iLike], position))
        )
        globalBlock = transformedBlockOrPalette(block, self.transform.rotation, self.transform.flip)
        return self.placeBlockGlobal(globalPosition, globalBlock, replace)


    def placeBlockGlobal(
        self,
        position: Union[Vec3iLike, Iterable[Vec3iLike]],
        block:    Union[Block, Sequence[Block]],
        replace:  Optional[Union[str, Iterable[str]]] = None
    ) -> bool:
        """Places ``block`` at ``position``, ignoring :attr:`.transform`.\n
        If ``position`` is iterable (e.g. a list), ``block`` is placed at all positions.
        In this case, buffering is temporarily enabled for better performance.\n
        If ``block`` is a sequence (e.g. a list), blocks are sampled randomly.\n
        Returns whether the placement succeeded fully."""

        if (
            hasattr(position, "__len__")
            and len(cast(Sized, position)) == 3
            and hasattr(position, "__getitem__")
            and isinstance(cast(Sequence[Any], position)[0], Integral)
        ):
            return self._placeSingleBlockGlobal(ivec3(*cast(Vec3iLike, position)), block, replace)

        oldBuffering = self.buffering
        self.buffering = True
        success = eagerAll(self._placeSingleBlockGlobal(ivec3(*pos), block, replace) for pos in cast(Iterable[Vec3iLike], position))
        self.buffering = oldBuffering
        return success


    def _placeSingleBlockGlobal(
        self,
        position: ivec3,
        block:    Union[Block, Sequence[Block]],
        replace:  Optional[Union[str, Iterable[str]]] = None
    ) -> bool:
        """Places ``block`` at ``position``, ignoring :attr:`.transform`.\n
        If ``block`` is a sequence (e.g. a list), blocks are sampled randomly.\n
        Returns whether the placement succeeded fully."""

        # Check replace condition
        if replace is not None:
            if isinstance(replace, str):
                replace = [replace]
            if cast(str, self.getBlockGlobal(position).id) not in replace:
                return True

        # Select block from palette
        if not isinstance(block, Block):
            block = random.choice(block)
        if not block.id:
            return True

        if self._buffering:
            success = self._placeSingleBlockGlobalBuffered(position, block)
        else:
            success = self._placeSingleBlockGlobalDirect(position, block)

        if not success:
            return False

        if self.caching:
            self._cache[position] = block

        if self._worldSlice is not None and self._worldSlice.rect.contains(dropY(position)):
            cast(npt.NDArray[np.bool_], self._worldSliceDecay)[tuple(position - self._worldSlice.box.offset)] = True

        return True


    def _placeSingleBlockGlobalDirect(self, position: ivec3, block: Block) -> bool:
        """Place a single block in the world directly.\n
        Returns whether the placement succeeded."""
        result = interface.placeBlocks([(position, block)], dimension=self.dimension, doBlockUpdates=self.doBlockUpdates, spawnDrops=self.spawnDrops, retries=self.retries, timeout=self.timeout, host=self.host)
        if not result[0][0]:
            logger.error("Server returned error upon placing block:\n  %s", result[0][1])
            return False
        return True


    def _placeSingleBlockGlobalBuffered(self, position: ivec3, block: Block) -> bool:
        """Place a block in the buffer and send once limit is exceeded.\n
        Returns whether placement succeeded."""
        if len(self._buffer) >= self.bufferLimit:
            self.flushBuffer()
        self._buffer.pop(position, None) # Ensure the new block is added at the *end* of the buffer.
        self._buffer[position] = block
        return True


    def flushBuffer(self) -> None:
        """Flushes the block placement buffer.\n
        If multithreaded buffer flushing is enabled, the worker threads can be awaited with
        :meth:`.awaitBufferFlushes`."""

        def flush(blockBuffer: Dict[ivec3, Block], commandBuffer: List[str]):
            # Flush block buffer
            if blockBuffer:
                response = interface.placeBlocks(blockBuffer.items(), dimension=self.dimension, doBlockUpdates=self._bufferDoBlockUpdates, spawnDrops=self.spawnDrops, retries=self.retries, timeout=self.timeout, host=self.host)
                blockBuffer.clear()

                for entry in response:
                    if not entry[0]:
                        logger.error("Server returned error upon placing buffered block:\n  %s", entry[1])

            # Flush command buffer
            if commandBuffer:
                response = interface.runCommand("\n".join(commandBuffer), dimension=self.dimension, retries=self.retries, timeout=self.timeout, host=self.host)
                commandBuffer.clear()

                for entry in response:
                    if not entry[0]:
                        logger.error("Server returned error upon running buffered command:\n  %s", entry[1])

        if self._multithreading:
            # Clean up finished buffer flush futures
            self._bufferFlushFutures = [
                future for future in self._bufferFlushFutures if not future.done()
            ]

            # Shallow copies are good enough here
            blockBufferCopy   = self._buffer
            commandBufferCopy = self._commandBuffer
            def task():
                flush(blockBufferCopy, commandBufferCopy)

            # Submit the task
            future = self._bufferFlushExecutor.submit(task)
            self._bufferFlushFutures.append(future)

            # Empty the buffers (the thread has copies of the references)
            self._buffer = {}
            self._commandBuffer = []

        else: # No multithreading
            flush(self._buffer, self._commandBuffer)


    def awaitBufferFlushes(self, timeout: Optional[float] = None) -> None:
        """Awaits all pending buffer flushes.\n
        If ``timeout`` is not ``None``, waits for at most ``timeout`` seconds.\n
        Does nothing if no buffer flushes have occured while multithreaded buffer flushing was
        enabled."""
        self._bufferFlushFutures = list(futures.wait(self._bufferFlushFutures, timeout).not_done)


    def loadWorldSlice(self, rect: Optional[Rect]=None, heightmapTypes: Optional[Iterable[str]] = None, cache: bool = False) -> WorldSlice:
        """Loads the world slice for the given XZ-rectangle.\n
        The rectangle must be given in **global coordinates**; :attr:`.transform` is ignored.\n
        If ``rect`` is None, the world slice of the current build area is loaded.\n
        If ``heightmapTypes`` is None, all heightmaps are loaded.\n
        If ``cache`` is ``True``, the loaded worldSlice is cached in this editor. It can then be
        accessed through :attr:`.worldSlice`.
        If a world slice was already cached, it is replaced.
        The cached world slice is used for faster block and biome retrieval. Note that the editor
        assumes that nothing besides itself changes the given area of the world. If the given world
        area is changed other than through this editor, call :meth:`.updateWorldSlice` to update the
        cached world slice."""
        if rect is None:
            rect = self.getBuildArea().toRect()
        worldSlice = WorldSlice(rect, dimension=self.dimension, heightmapTypes=heightmapTypes, retries=self.retries, timeout=self.timeout, host=self.host)
        if cache:
            self._worldSlice      = worldSlice
            self._worldSliceDecay = np.zeros(tuple(self._worldSlice.box.size), dtype=np.bool_)
        return worldSlice


    def updateWorldSlice(self) -> WorldSlice:
        """Updates the cached world slice.\n
        Loads and caches new world slice for the same area and with the same heightmaps as the
        currently cached one.
        Raises a :exc:`RuntimeError` if no world slice is cached.
        """
        if self._worldSlice is None:
            raise RuntimeError("No world slice is cached. Call .loadWorldSlice() with cache=True first.")
        return self.loadWorldSlice(self._worldSlice.rect, self._worldSlice.heightmaps.keys(), cache=True)


    def getMinecraftVersion(self) -> str:
        """Returns the Minecraft version as a string."""
        return interface.getVersion(retries=self.retries, timeout=self.timeout, host=self.host)


    def checkConnection(self) -> None:
        """Raises an :exc:`InterfaceConnectionError` if the GDMC HTTP interface cannot be reached.\n
        Does not perform any retries."""
        interface.getVersion(retries=0, timeout=self.timeout, host=self.host)


    @contextmanager
    def pushTransform(self, transformLike: Optional[TransformLike] = None) -> Generator[None, None, None]:
        """Creates a context that reverts all changes to :attr:`.transform` on exit.
        If ``transformLike`` is not ``None``, it is pushed to :attr:`.transform` on enter.

        Can be used to create a local coordinate system on top of the current local coordinate
        system.

        Not to be confused with :meth:`.Transform.push`!"""

        originalTransform = deepcopy(self.transform)
        if transformLike is not None:
            self.transform @= toTransform(transformLike)
        try:
            yield
        finally:
            self.transform = originalTransform

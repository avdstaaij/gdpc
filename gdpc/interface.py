"""Provide tools for placing and getting blocks and more.

This module contains functions to:
- Request the build area as defined in-world
- Run Minecraft commands
- Get the block ID at a particular coordinate
- Place blocks in the world
"""


from typing import Any, Union, Optional, List, Tuple
from contextlib import contextmanager
from copy import copy, deepcopy
from collections import OrderedDict
import random
import time
from concurrent import futures

from glm import ivec3

from .util import non_zero_sign, eprint
from .lookup import TCOLORS
from .toolbox import is_sequence
from .vector_util import scaleToFlip3D, Rect, Box, boxBetween
from .transform import Transform, TransformLike, toTransform
from .block import Block
from . import direct_interface as di
from . import worldLoader


def getBuildArea(default = Box(ivec3(0,0,0), ivec3(128,256,128))):
    """Returns the build area that was specified by /setbuildarea in-game.\n
    If no build area was specified, returns <default>."""
    success, result = di.getBuildArea()
    if not success:
        return default
    beginX, beginY, beginZ, endX, endY, endZ = result
    return boxBetween(ivec3(beginX, beginY, beginZ), ivec3(endX, endY, endZ))


def setBuildArea(buildArea: Box):
    """Sets the build area to [box], and returns it."""
    runCommand(f"setbuildarea {buildArea.begin.x} {buildArea.begin.y} {buildArea.begin.z} {buildArea.end.x} {buildArea.end.y} {buildArea.end.z}")
    return getBuildArea()


def centerBuildAreaOnPlayer(size: ivec3):
    """Sets the build area to a box of [size] centered on the player, and returns it."""
    # -1 to correcting for offset from player position
    radius = (size - 1) // 2
    runCommand("execute at @p run setbuildarea "
               f"~{-radius.x} ~{-radius.y} ~{-radius.z} ~{radius.x} ~{radius.y} ~{radius.z}")
    return getBuildArea()


# TODO: move retrying to worldSlice constructor, or to general retrying function
def getWorldSlice(rect: Rect):
    """Returns a WorldSlice of the region specified by [rect]."""
    assert isinstance(rect, Rect) # To protect from calling this with a Box
    attempts = 0
    while True:
        try:
            attempts += 1
            return worldLoader.WorldSlice(rect.begin[0], rect.begin[1], rect.end[0], rect.end[1])
        except Exception as e: # pylint: disable=broad-except
            if attempts < 10:
                eprint("Could not get the world slice. Try reducing your render distance. I'll retry in a bit.")
                time.sleep(2)
            else:
                eprint("OK, that's enough retries. You deal with the exception.")
                raise


def runCommand(command: str):
    """Executes one or multiple Minecraft commands (separated by newlines).\n
    The leading "/" can be omitted.\n
    Returns a list with one string for each command. If the command was successful, the string
    is its return value. Otherwise, it is the error message."""
    if command[0] == '/':
        command = command[1:]
    return di.runCommand(command)


def blockNBTCommand(position: ivec3, nbt: str):
    """Returns the command required to merge the nbt data of the block at the global position
    [position] with [nbt]."""
    return f"data merge block {position.x} {position.y} {position.z} {{{nbt}}}"


class OrderedByLookupDict(OrderedDict):
    """Limit size, evicting the least recently looked-up key when full.

    Taken from
    https://docs.python.org/3/library/collections.html?highlight=ordereddict#collections.OrderedDict
    """

    def __init__(self, maxsize, *args, **kwds):
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    # inherited __repr__ from OrderedDict is sufficient

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if self.maxsize > 0 and len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]


class Editor:
    """Provides functions to place blocks in the world by interacting with the GDMC mod's HTTP
    interface.

    Stores various settings, resources, buffers and caches related to block placement, and a
    transform that defines a local coordinate system.

    Wraps gdpc v5.0's Interface class to work with vectors and transforms, and extends it, but
    also removes some features. The wrapped gdpc Interface is available as .gdpcInterface."""

    def __init__(
        self,
        transformLike: Optional[TransformLike] = None,
        buffering             = True,
        bufferLimit           = 1024,
        caching               = False,
        cacheLimit            = 8192,
        multithreading        = False,
        multithreadingWorkers = 8,
    ):
        """Constructs an Interface instance with the specified transform and settings"""
        self._transform = Transform() if transformLike is None else toTransform(transformLike)

        self._buffering = buffering
        self._bufferLimit = bufferLimit
        self._buffer: List[Tuple[ivec3, str]] = []

        self._caching = caching
        self._cache = OrderedByLookupDict(cacheLimit)

        self._multithreadingWorkers = multithreadingWorkers
        self._bufferFlushExecutor   = None
        self.multithreading = multithreading # Creates the buffer flush executor if True
        self._bufferFlushFutures: List[futures.Future] = []
        self._commandBuffer:      List[str]            = []

        self._doBlockUpdates = True
        self._bufferDoBlockUpdates = True


    def __del__(self):
        """Cleans up this Interface instance"""
        self.sendBufferedBlocks()
        self.awaitBufferFlushes()


    @property
    def transform(self):
        """This interface's local coordinate transform"""
        return self._transform

    @transform.setter
    def transform(self, value: Union[Transform, ivec3]):
        self._transform = toTransform(value)

    @property
    def buffering(self) -> bool:
        """Whether block placement buffering is enabled"""
        return self._buffering

    @buffering.setter
    def buffering(self, value: bool):
        if self.buffering and not value:
            self.sendBufferedBlocks()
        self._buffering = value

    @property
    def bufferLimit(self) -> int:
        """Size of the block buffer"""
        return self._bufferLimit

    @bufferLimit.setter
    def bufferLimit(self, value: int):
        self._bufferLimit = value
        if len(self._buffer) >= self.bufferLimit:
            self.sendBufferedBlocks()

    @property
    def caching(self):
        """Whether caching retrieved blocks is enabled"""
        return self._caching

    @caching.setter
    def caching(self, value: bool):
        self._caching = value
        # TODO: do something with an internal/global WorldSlice?

    @property
    def cacheLimit(self):
        """Size of the block cache"""
        return self._cache.maxsize

    @cacheLimit.setter
    def cacheLimit(self, value: int):
        self._cache.maxsize = value

    @property
    def multithreading(self):
        """Whether multithreaded buffer flushing is enabled"""
        return self._multithreading

    @multithreading.setter
    def multithreading(self, value: bool):
        self._multithreading = value
        if value and self._bufferFlushExecutor is None:
            self._bufferFlushExecutor = futures.ThreadPoolExecutor(self._multithreadingWorkers)

    @property
    def multithreadingWorkers(self):
        """The amount of buffer flush worker threads.\n
        Modifying the amount of workers after class construction is not supported."""
        return self._multithreadingWorkers

    # TODO: Add support for the other block placement flags?
    # https://github.com/nilsgawlik/gdmc_http_interface/wiki/Interface-Endpoints
    @property
    def doBlockUpdates(self):
        return self._doBlockUpdates

    @doBlockUpdates.setter
    def doBlockUpdates(self, value: bool):
        self._doBlockUpdates = value


    def runCommand(self, command: str):
        """Executes one or multiple Minecraft commands (separated by newlines).\n
        The leading "/" can be omitted.\n
        If buffering is enabled, the command is deferred until after the next buffer flush."""
        if self.buffering:
            self._commandBuffer.append(command)
        else:
            runCommand(command)


    def getBlock(self, position: ivec3):
        """Returns the namespaced ID of the block at [position].\n
        If the given coordinates are invalid, returns "minecraft:void_air"."""
        return self.getBlockGlobal(self.transform * position)


    # TODO: old gdpc code; refactor?
    def getBlockGlobal(self, position: ivec3):
        positionTuple = tuple(position)

        if self.caching and positionTuple in self._cache.keys():
            return self._cache[positionTuple]

        blockId: str = di.getBlock(*position)[0]["id"]
        if self.caching:
            self._cache[positionTuple] = blockId

        return blockId


    def placeBlock(
        self,
        transformLike:  TransformLike,
        block:          Block,
        replace:        Optional[Union[str, List[str]]] = None,
        doBlockUpdates: Optional[bool] = None
    ):
        """Places [block] at [transformOrVec].\n
        [transformOrVec] is interpreted as local to the coordinate system defined by
        self.transform.\n
        Returns whether the placement succeeded fully.\n
        If [block].name is a list, names are sampled randomly."""
        return self.placeBlockGlobal(self.transform @ toTransform(transformLike), block, replace, doBlockUpdates)


    def placeBlockGlobal(
        self,
        transform:      Transform,
        block:          Block,
        replace:        Optional[Union[str, List[str]]] = None,
        doBlockUpdates: Optional[bool] = None
    ):
        """Places [block] at [transform], ignoring self.transform.\n
        If [block].name is a list, names are sampled randomly.\n
        Returns whether the placement succeeded fully.\n
        This is an internal function that is made available for advanced usage."""
        return self.placeStringGlobal(
            transform.translation,
            transform.scale,
            block.name,
            block.blockStateString(transform.rotation, scaleToFlip3D(transform.scale)),
            block.nbt,
            replace,
            doBlockUpdates,
        )


    def placeStringGlobal(
        self,
        position:       ivec3,
        scale:          ivec3,
        blockString:    Union[str, List[str]],
        blockState:     str = "",
        nbt:            Optional[str] = None,
        replace:        Optional[Union[str, List[str]]] = None,
        doBlockUpdates: Optional[bool] = None
    ):
        """Places blocks defined by [blockString], [blockState] and [nbt] in the box ([position],
        [scale]), ignoring self.transform.\n
        Note that any flips caused by [scale] must already be applied to [blockState].\n
        If [block].name is a list, names are sampled randomly.\n
        Returns whether the placement succeeded fully.\n
        This is an internal function that is made available for advanced usage. It can be used
        to avoid unnecessary repeated transform compositions and Block.stateString() calls when
        a geometrical region of blocks is placed."""

        totalSuccess = True

        for x in range(position.x, position.x + scale.x, non_zero_sign(scale.x)):
            for y in range(position.y, position.y + scale.y, non_zero_sign(scale.y)):
                for z in range(position.z, position.z + scale.z, non_zero_sign(scale.z)):
                    # Select block from palette
                    if isinstance(blockString, str):
                        chosen_block_string = blockString
                    else:
                        chosen_block_string = random.choice(blockString)
                    # Place the block
                    success = self._placeSingleStringGlobal(ivec3(x,y,z), chosen_block_string + blockState, nbt, replace, doBlockUpdates)
                    if not success:
                        totalSuccess = False

        return totalSuccess


    # TODO: rethink block placing functions. Do we really need this many?
    # TODO: merged with gdpc code; refactor more?
    def _placeSingleStringGlobal(
        self,
        position:       ivec3,
        blockString:    str,
        nbt:            Optional[str],
        replace:        Optional[Union[str, List[str]]],
        doBlockUpdates: Optional[bool]
    ):
        if isinstance(replace, str):
            if self.getBlockGlobal(position) != replace:
                return True
        elif is_sequence(replace) and self.getBlockGlobal(position) not in replace:
            return True
        elif (self.caching and blockString in self.getBlockGlobal(position)):
            return True

        if self._buffering:
            success = self._placeSingleStringGlobalBuffered(position, blockString, doBlockUpdates)
        else:
            success = self._placeSingleStringGlobalDirect(position, blockString, doBlockUpdates)

        if not success:
            return False

        self._cache[tuple(position)] = blockString

        if nbt is not None:
            self.runCommand(blockNBTCommand(position, nbt))

        return True


    # TODO: old gdpc code, refactor more?
    def _placeSingleStringGlobalDirect(self, position: ivec3, blockString: str, doBlockUpdates: Optional[bool]):
        """Place a single block in the world directly.\n
        Returns whether the placement succeeded."""
        if doBlockUpdates is None: doBlockUpdates = self.doBlockUpdates

        result = di.placeBlock(*position, blockString, doBlockUpdates, customFlags=None)
        if not result.isnumeric():
            eprint(f"{TCOLORS['orange']}Warning: Server returned error upon placing block:\n\t{TCOLORS['CLR']}{result}")
            return False
        return True


    # TODO: old gdpc code, refactor more?
    def _placeSingleStringGlobalBuffered(self, position: ivec3, blockString: str, doBlockUpdates: Optional[bool]):
        """Place a block in the buffer and send once limit is exceeded.\n
        Returns whether placement succeeded."""
        if doBlockUpdates is None: doBlockUpdates = self.doBlockUpdates

        if doBlockUpdates != self._bufferDoBlockUpdates:
            self.sendBufferedBlocks()
            self._bufferDoBlockUpdates = doBlockUpdates

        elif len(self._buffer) >= self.bufferLimit:
            self.sendBufferedBlocks()

        self._buffer.append((position, blockString))
        return True


    def sendBufferedBlocks(self, retries = 5):
        """Flushes the block placement buffer.\n
        If multithreaded buffer flushing is enabled, the threads can be awaited with
        awaitBufferFlushes()."""

        def flush(blockBuffer: List[Tuple[ivec3, str]], commandBuffer: List[str]):
            # Flush block buffer
            if blockBuffer:
                blockStr = "\n".join((f"{t[0].x} {t[0].y} {t[0].z} {t[1]}" for t in blockBuffer))
                response = di.placeBlock(0, 0, 0, blockStr, doBlockUpdates=self._bufferDoBlockUpdates, retries=retries)
                blockBuffer.clear()

                for line in response:
                    if not line.isnumeric():
                        eprint(f"{TCOLORS['orange']}Warning: Server returned error upon placing buffered block:\n\t{TCOLORS['CLR']}{line}")


            # Flush command buffer
            if commandBuffer:
                response = runCommand("\n".join(commandBuffer))
                commandBuffer.clear()

                for line in response:
                    if not line.isnumeric():
                        eprint(f"{TCOLORS['orange']}Warning: Server returned error upon sending buffered command:\n\t{TCOLORS['CLR']}{line}")

        if self._multithreading:
            # Clean up finished buffer flush futures
            self._bufferFlushFutures = [
                future for future in self._bufferFlushFutures if not future.done()
            ]

            # Shallow copies are good enough here
            block_buffer_copy   = copy(self._buffer)
            command_buffer_copy = copy(self._commandBuffer)
            def task():
                flush(block_buffer_copy, command_buffer_copy)

            # Submit the task
            future = self._bufferFlushExecutor.submit(task)
            self._bufferFlushFutures.append(future)

            # Empty the buffers (the thread has copies of the references)
            self._buffer = []
            self._commandBuffer = []

        else: # No multithreading
            flush(self._buffer, self._commandBuffer)


    def awaitBufferFlushes(self, timeout: Optional[float] = None):
        """Awaits all pending buffer flushes.\n
        If [timeout] is not None, waits for at most [timeout] seconds.\n
        Does nothing if no buffer flushes have occured while multithreaded buffer flushing was
        enabled."""
        self._bufferFlushFutures = futures.wait(self._bufferFlushFutures, timeout).not_done


    @contextmanager
    def pushTransform(self, transformLike: Optional[TransformLike] = None):
        """Creates a context that reverts all changes to self.transform on exit.
        If <transformOrVec> is not None, it is pushed to self.transform on enter.

        Can be used to create a local coordinate system on top of the current local coordinate
        system.

        Not to be confused with Transform.push()!"""

        originalTransform = deepcopy(self.transform)
        if transformLike is not None:
            self.transform @= toTransform(transformLike)
        try:
            yield
        finally:
            self.transform = originalTransform

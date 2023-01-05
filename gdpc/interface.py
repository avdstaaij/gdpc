"""Provide tools for placing and getting blocks and more.

This module contains functions to:
- Request the build area as defined in-world
- Run Minecraft commands
- Get the block ID at a particular coordinate
- Place blocks in the world
"""


from typing import Union, Optional, List, Tuple, Iterable
from contextlib import contextmanager
from copy import copy, deepcopy
from concurrent import futures

import numpy as np
from glm import ivec3
from termcolor import colored

from .utility import eprint, eagerAll, OrderedByLookupDict
from .vector_tools import Rect, Box, addY, dropY
from .transform import Transform, TransformLike, toTransform
from .block import Block
from . import lookup
from . import direct_interface as di
from .worldSlice import WorldSlice


def getBuildArea(default = Box(ivec3(0,0,0), ivec3(128,256,128))):
    """Returns the build area that was specified by /setbuildarea in-game.\n
    If no build area was specified, returns <default>."""
    success, result = di.getBuildArea()
    if not success:
        return deepcopy(default)
    beginX, beginY, beginZ, endX, endY, endZ = result
    return Box.between(ivec3(beginX, beginY, beginZ), ivec3(endX, endY, endZ))


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


def runCommand(command: str):
    """Executes one or multiple Minecraft commands (separated by newlines).\n
    The leading "/" can be omitted.\n
    Returns a list with one string for each command. If the command was successful, the string
    is its return value. Otherwise, it is the error message."""
    if command[0] == '/':
        command = command[1:]
    return di.runCommand(command)


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
        buffering             = False,
        bufferLimit           = 1024,
        caching               = False,
        cacheLimit            = 8192,
        multithreading        = False,
        multithreadingWorkers = 1,
    ):
        """Constructs an Interface instance with the specified transform and settings"""
        self._transform = Transform() if transformLike is None else toTransform(transformLike)

        self._buffering = buffering
        self._bufferLimit = bufferLimit
        self._buffer: List[Tuple[ivec3, str]] = []
        self._commandBuffer: List[str] = []

        self._caching = caching
        self._cache = OrderedByLookupDict[ivec3,Block](cacheLimit)

        self._multithreading = False
        self._multithreadingWorkers = multithreadingWorkers
        self.multithreading = multithreading # The property setter initializes the multithreading system.
        self._bufferFlushFutures: List[futures.Future] = []

        self._doBlockUpdates = True
        self._bufferDoBlockUpdates = True

        self._worldSlice: Optional[WorldSlice] = None
        self._worldSliceDecay: Optional[np.ndarray] = None


    def __del__(self):
        """Cleans up this Editor instance"""
        # awaits any pending buffer flush futures and shuts down the buffer flush executor
        self.multithreading = False # awaits any pending buffer flush futures and shuts down the buffer flush executor
        # Flush any remaining blocks in the buffer.
        # This is purposefully done *after* disabling multithreading! This __del__ may be called at
        # interpreter shutdown, and it appears that scheduling a new future at that point fails with
        # "RuntimeError: cannot schedule new futures after shutdown" even if the executor has not
        # actually shut down yet. For safety, the last buffer flush must be done on the main thread.
        self.sendBufferedBlocks()


    @property
    def transform(self):
        """This editor's local coordinate transform"""
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
        """Whether caching placed and retrieved blocks is enabled"""
        return self._caching

    @caching.setter
    def caching(self, value: bool):
        self._caching = value

    @property
    def cacheLimit(self):
        """Size of the block cache"""
        return self._cache.maxSize

    @cacheLimit.setter
    def cacheLimit(self, value: int):
        self._cache.maxSize = value

    @property
    def multithreading(self):
        """Whether multithreaded buffer flushing is enabled"""
        return self._multithreading

    @multithreading.setter
    def multithreading(self, value: bool):
        if not self._multithreading and value:
            self._bufferFlushExecutor = futures.ThreadPoolExecutor(self._multithreadingWorkers)
            if self._multithreadingWorkers > 1:
                eprint(colored(color="yellow", text=\
                    "WARNING: An editor has been set to use multithreaded buffer flushing with more\n"
                    "than one worker thread.\n"
                    "The editor can no longer guarantee that blocks will be placed in the same order\n"
                    "as they were sent. If caching is used, this can also cause the cache to become\n"
                    "inconsistent with the actual world.\n"
                    "Multithreading with more than one worker thread can speed up block placement on\n"
                    "some machines, which can be nice during development, but it is NOT RECOMMENDED\n"
                    "for production code."
                ))
        elif self._multithreading and not value:
            self._bufferFlushExecutor.shutdown(wait=True)
            del self._bufferFlushExecutor
        self._multithreading = value

    @property
    def multithreadingWorkers(self):
        """The amount of buffer flush worker threads."""
        return self._multithreadingWorkers

    @multithreadingWorkers.setter
    def multithreadingWorkers(self, value: int):
        restartExecutor = self.multithreading and self._multithreadingWorkers != value
        self._multithreadingWorkers = value
        if restartExecutor:
            self.multithreading = False
            self.multithreading = True

    # TODO: Add support for the other block placement flags?
    # https://github.com/nilsgawlik/gdmc_http_interface/wiki/Interface-Endpoints
    @property
    def doBlockUpdates(self):
        return self._doBlockUpdates

    @doBlockUpdates.setter
    def doBlockUpdates(self, value: bool):
        self._doBlockUpdates = value

    @property
    def worldSlice(self):
        """The cached WorldSlice"""
        return self._worldSlice

    @property
    def worldSliceDecay(self):
        """3D boolean array indicating whether the block at the specified position in the cached
        worldSlice is still valid.\n
        Do not edit the returned array.\n
        Note that the lowest Y-layer is at [:,0,:], despite Minecraft's negative Y coordinates."""
        return self._worldSliceDecay


    def runCommand(self, command: str):
        """Executes one or multiple Minecraft commands (separated by newlines).\n
        The leading "/" can be omitted.\n
        If buffering is enabled, the command is deferred until after the next buffer flush."""
        if self.buffering:
            self._commandBuffer.append(command)
        else:
            runCommand(command)


    # TODO: getBlockData option (waiting for HTTP backend update)
    def getBlock(self, position: ivec3, getBlockStates: bool = True):
        """Returns the block at [position].\n
        <position> is interpreted as local to the coordinate system defined by self.transform.
        The returned block's orientation is also from the perspective of self.transform.\n
        If the given coordinates are invalid, returns Block("minecraft:void_air")."""
        block = self.getBlockGlobal(self.transform * position, getBlockStates)
        invTransform = ~self.transform
        block.transform(invTransform.rotation, invTransform.flip)
        return block


    # TODO: getBlockData option (waiting for HTTP backend update)
    def getBlockGlobal(self, position: ivec3, getBlockStates: bool = True):
        """Returns the block at [position], ignoring self.transform.\n
        If the given coordinates are invalid, returns Block("minecraft:void_air")."""
        if self.caching and position in self._cache.keys():
            return self._cache[position]

        if (
            self._worldSlice is not None and
            self._worldSlice.rect.contains(dropY(position)) and
            not self._worldSliceDecay[tuple(position - addY(self._worldSlice.rect.offset, lookup.BUILD_Y_MIN))]
        ):
            block = Block.fromBlockCompound(self._worldSlice.getBlockCompoundAt(position))
        else:
            blockDict = di.getBlock(*position, includeState=getBlockStates, includeData=False)[0]
            block = Block(blockDict["id"], blockDict["state"])

        if self.caching:
            self._cache[position] = copy(block)

        return block


    def placeBlock(
        self,
        position:       Union[ivec3, Iterable[ivec3]],
        block:          Block,
        replace:        Optional[Union[str, List[str]]] = None,
        doBlockUpdates: Optional[bool] = None
    ):
        """Places <block> at <position>.\n
        <position> is interpreted as local to the coordinate system defined by self.transform.\n
        If <position> is iterable (e.g. a list), <block> is placed at all positions.
        This is slightly more efficient than calling this method in a loop.\n
        If <block>.name is a list, names are sampled randomly.\n
        Returns whether the placement succeeded fully."""
        return self.placeBlockGlobal(
            self.transform * position if isinstance(position, ivec3) else (self.transform * pos for pos in position),
            block.transformed(self.transform.rotation, self.transform.flip),
            replace,
            doBlockUpdates
        )


    def placeBlockGlobal(
        self,
        position:       Union[ivec3, Iterable[ivec3]],
        block:          Block,
        replace:        Optional[Union[str, Iterable[str]]] = None,
        doBlockUpdates: Optional[bool] = None
    ):
        """Places <block> at <position>, ignoring self.transform.\n
        If <position> is iterable (e.g. a list), <block> is placed at all positions.
        In this case, buffering is temporarily enabled for better performance.\n
        If <block>.name is a list, names are sampled randomly.\n
        Returns whether the placement succeeded fully."""

        if isinstance(position, ivec3):
            return self._placeSingleBlockGlobal(position, block, replace, doBlockUpdates)

        oldBuffering = self.buffering
        self.buffering = True
        success = eagerAll(self._placeSingleBlockGlobal(pos, block, replace, doBlockUpdates) for pos in position)
        self.buffering = oldBuffering
        return success


    def _placeSingleBlockGlobal(
        self,
        position:       ivec3,
        block:          Block,
        replace:        Optional[Union[str, Iterable[str]]] = None,
        doBlockUpdates: Optional[bool] = None
    ):
        """Places <block> at <position>, ignoring self.transform.\n
        If <block>.name is a list, names are sampled randomly.\n
        Returns whether the placement succeeded fully."""

        # Check replace condition
        if replace is not None:
            if isinstance(replace, str):
                replace = [replace]
            if self.getBlockGlobal(position) not in replace:
                return True

        # Select block from palette
        block = block.chooseId()

        # Support for "no placement" in block palettes
        if not block.id:
            return True

        if (self.caching and block.id in self.getBlockGlobal(position)): # TODO: this is very error-prone! "stone" is in "stone_stairs". Also, we may want to change only block state or nbt data.
            return True

        blockStr = block.id + block.blockStateString() + (f"{{{block.data}}}" if block.data else "")

        if self._buffering:
            success = self._placeSingleBlockStringGlobalBuffered(position, blockStr, doBlockUpdates)
        else:
            success = self._placeSingleBlockStringGlobalDirect(position, blockStr, doBlockUpdates)

        if not success:
            return False

        if self.caching:
            self._cache[position] = block

        if self._worldSlice is not None and self._worldSlice.rect.contains(dropY(position)):
            self._worldSliceDecay[tuple(position - addY(self._worldSlice.rect.offset, lookup.BUILD_Y_MIN))] = True

        return True


    def _placeSingleBlockStringGlobalDirect(self, position: ivec3, blockString: str, doBlockUpdates: Optional[bool]):
        """Place a single block in the world directly.\n
        Returns whether the placement succeeded."""
        if doBlockUpdates is None: doBlockUpdates = self.doBlockUpdates

        result = di.placeBlock(*position, blockString, doBlockUpdates=doBlockUpdates)
        if not result[0].isnumeric():
            eprint(colored(color="yellow", text=f"Warning: Server returned error upon placing block:\n\t{result}"))
            return False
        return True


    def _placeSingleBlockStringGlobalBuffered(self, position: ivec3, blockString: str, doBlockUpdates: Optional[bool]):
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
                        eprint(colored(color="yellow", text=f"Warning: Server returned error upon placing buffered block:\n\t{line}"))

            # Flush command buffer
            if commandBuffer:
                response = runCommand("\n".join(commandBuffer))
                commandBuffer.clear()

                for line in response:
                    if not line.isnumeric():
                        eprint(colored(color="yellow", text=f"Warning: Server returned error upon sending buffered command:\n\t{line}"))

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


    def loadWorldSlice(self, rect: Rect):
        """Loads and caches the world slice for the given XZ-rectangle.\n
        If a world slice was already cached, it is replaced.\n
        The cached world slice is used for faster block retrieval. Note that the editor assumes
        that nothing besides itself changes the given area of the world. If the given world area is
        changed other than through this editor, call .updateWorldSlice() to update the cached world
        slice.\n
        There is no local coordinate version of this method. The rectangle must be given in global
        coordinates."""
        self._worldSlice      = WorldSlice(rect)
        self._worldSliceDecay = np.zeros(addY(self._worldSlice.rect.size, lookup.BUILD_HEIGHT), dtype=np.bool)
        return self._worldSlice


    def updateWorldSlice(self):
        """Updates the cached world slice."""
        if (self._worldSlice is None):
            raise RuntimeError("No world slice is cached. Call .loadWorldSliceGlobal() first.")
        return self.loadWorldSlice(self._worldSlice.rect)


    @contextmanager
    def pushTransform(self, transformLike: Optional[TransformLike] = None):
        """Creates a context that reverts all changes to self.transform on exit.
        If <transformLine> is not None, it is pushed to self.transform on enter.

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

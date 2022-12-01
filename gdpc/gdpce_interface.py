"""Functions and classes that communicate with the GDMC mod's HTTP interface.

Wraps gdpc v5.0's interface module to work with vectors, and extends it.
"""


from typing import Union, Optional, List
from contextlib import contextmanager
from copy import copy, deepcopy
import random
import time
from concurrent import futures
from glm import ivec3

from .util import non_zero_sign, stdoutToStderr, eprint

with stdoutToStderr(): # GDPC outputting to stdout on import messes with some scripts
    from gdpc import interface, direct_interface, worldLoader

from .vector_util import scaleToFlip3D, Rect, boxBetween
from .transform import Transform, toTransform
from .block import Block


def getBuildArea():
    """Returns the build area that was specified by /setbuildarea in-game"""
    with stdoutToStderr():
        beginX, beginY, beginZ, endX, endY, endZ = interface.requestBuildArea()
    return boxBetween(ivec3(beginX, beginY, beginZ), ivec3(endX, endY, endZ))


def getWorldSlice(rect: Rect):
    """Returns a gdpc WorldSlice of the region specified by [rect]"""
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
    """Executes one or multiple Minecraft commands (separated by newlines)"""
    direct_interface.runCommand(command)


def blockNBTCommand(position: ivec3, nbt: str):
    """Returns the command required to merge the nbt data of the block at the global position
    [position] with [nbt]"""
    return f"data merge block {position.x} {position.y} {position.z} {{{nbt}}}"


class Interface:
    """Provides functions to place blocks in the world by interacting with the GDMC mod's HTTP
    interface.

    Stores various settings, resources, buffers and caches related to block placement, and a
    transform that defines a local coordinate system.

    Wraps gdpc v5.0's Interface class to work with vectors and transforms, and extends it, but
    also removes some features. The wrapped gdpc Interface is available as .gdpcInterface. """

    def __init__(
        self,
        transformOrVec: Optional[Union[Transform, ivec3]] = None,
        buffering             = True,
        bufferLimit           = 1024,
        multithreading        = False,
        multithreadingWorkers = 8,
        caching               = False,
        cacheLimit            = 8192,
    ):
        """Constructs an Interface instance with the specified transform and settings"""
        self.transform = Transform() if transformOrVec is None else toTransform(transformOrVec)
        self.gdpcInterface = interface.Interface(
            buffering   = buffering,
            bufferlimit = bufferLimit + 1, # +1 so we can intercept the buffer flushes
            caching     = caching,
            cachelimit  = cacheLimit
        )
        self._multithreadingWorkers = multithreadingWorkers
        self._bufferFlushExecutor   = None
        self.multithreading = multithreading # Creates the buffer flush executor if True
        self._bufferFlushFutures: List[futures.Future] = []
        self._command_buffer:     List[str]            = []


    def __del__(self):
        """Cleans up this Interface instance"""
        self.sendBufferedBlocks()
        self.awaitBufferFlushes()


    @property
    def buffering(self) -> bool:
        """Whether block placement buffering is enabled"""
        return self.gdpcInterface.isBuffering()

    @buffering.setter
    def buffering(self, value: bool):
        if self.buffering and not value:
            self.sendBufferedBlocks()
        self.gdpcInterface.setBuffering(value, notify=False)

    @property
    def bufferLimit(self) -> int:
        """Size of the block buffer"""
        return self.gdpcInterface.getBufferLimit() - 1

    @bufferLimit.setter
    def bufferLimit(self, value: int):
        self.gdpcInterface.setBufferLimit(value + 1)

    @property
    def caching(self):
        """Whether caching retrieved blocks is enabled"""
        return self.gdpcInterface.isCaching()

    @caching.setter
    def caching(self, value: bool):
        self.gdpcInterface.setCaching(value)

    @property
    def cacheLimit(self):
        """Size of the block cache"""
        return self.gdpcInterface.getCacheLimit()

    @cacheLimit.setter
    def cacheLimit(self, value: int):
        self.gdpcInterface.setCacheLimit(value)

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


    def runCommand(self, command: str):
        """Executes one or multiple Minecraft commands (separated by newlines).
        If buffering is enabled, the command is deferred until after the next buffer flush."""
        if self.buffering:
            self._command_buffer.append(command)
        else:
            runCommand(command)


    def placeStringGlobal(
        self,
        position:    ivec3,
        scale:       ivec3,
        blockString: Union[str, List[str]],
        blockState:  str = "",
        nbt:         Optional[str] = None,
        replace:     Optional[Union[str, List[str]]] = None,
    ):
        """Places blocks defined by [blockString], [blockState] and [nbt] in the box ([position],
        [scale]), ignoring self.transform.\n
        Note that any flips caused by [scale] must already be applied to [blockState].\n
        If [block].name is a list, names are sampled randomly.\n
        This is an internal function that is made available for advanced usage. It can be used
        to avoid unnecessary repeated transform compositions and Block.stateString() calls when
        a geometrical region of blocks is placed."""
        for x in range(position.x, position.x + scale.x, non_zero_sign(scale.x)):
            for y in range(position.y, position.y + scale.y, non_zero_sign(scale.y)):
                for z in range(position.z, position.z + scale.z, non_zero_sign(scale.z)):
                    # Select block from palette
                    if isinstance(blockString, str):
                        chosen_block_string = blockString
                    else:
                        chosen_block_string = random.choice(blockString)
                    # Place the block
                    if chosen_block_string != "": # Support for "nothing" in palettes
                        with stdoutToStderr():
                            self.gdpcInterface.placeBlock(
                                x, y, z,
                                chosen_block_string + blockState,
                                replace
                            )

        if nbt is not None:
            self.runCommand(blockNBTCommand(position, nbt))

        # Redirect all buffer flushes to self.sendBufferedBlocks, so we can implement automatic
        # multithreaded buffer flushing.
        if len(self.gdpcInterface.buffer) == self.bufferLimit:
            self.sendBufferedBlocks()


    def placeBlockGlobal(
        self,
        transform: Transform,
        block:     Block,
        replace:   Optional[Union[str, List[str]]] = None,
    ):
        """Places [block] at [transform], ignoring self.transform.\n
        If [block].name is a list, names are sampled randomly.\n
        This is an internal function that is made available for advanced usage."""
        self.placeStringGlobal(
            transform.translation,
            transform.scale,
            block.name,
            block.blockStateString(transform.rotation, scaleToFlip3D(transform.scale)),
            block.nbt,
            replace
        )


    def placeBlock(
        self,
        transformOrVec: Union[Transform, ivec3],
        block:          Block,
        replace:        Optional[Union[str, List[str]]] = None,
    ):
        """Places [block] at [transformOrVec].\n
        [transformOrVec] is interpreted as local to the coordinate system defined by
        self.transform.\n
        If [block].name is a list, names are sampled randomly."""
        self.placeBlockGlobal(self.transform @ toTransform(transformOrVec), block, replace)


    def sendBufferedBlocks(self, retries = 5):
        """Flushes the block placement buffer.\n
        If multithreaded buffer flushing is enabled, the threads can be awaited with
        awaitBufferFlushes()."""

        if self._multithreading:

            # Clean up finished buffer flush futures
            self._bufferFlushFutures = [
                future for future in self._bufferFlushFutures if not future.done()
            ]

            # Shallow copies are good enough here
            gdpc_interface_copy = copy(self.gdpcInterface)
            command_buffer_copy = copy(self._command_buffer)
            def task():
                with stdoutToStderr():
                    gdpc_interface_copy.sendBlocks(retries=retries)
                for command in command_buffer_copy:
                    runCommand(command)

            # Submit the task
            future = self._bufferFlushExecutor.submit(task)
            self._bufferFlushFutures.append(future)

            # Empty the buffers (the thread has copies of the references)
            self.gdpcInterface.buffer = []
            self._command_buffer     = []

        else: # No multithreading

            with stdoutToStderr():
                self.gdpcInterface.sendBlocks(retries=retries)
            for command in self._command_buffer:
                runCommand(command)
            self._command_buffer = []


    def awaitBufferFlushes(self, timeout: Optional[float] = None):
        """Awaits all pending buffer flushes.\n
        If [timeout] is not None, waits for at most [timeout] seconds.\n
        Does nothing if no buffer flushes have occured while multithreaded buffer flushing was
        enabled."""
        self._bufferFlushFutures = futures.wait(self._bufferFlushFutures, timeout).not_done


    # TODO: if need be, we can wrap gdpcInterface.getBlock() as well.


    @contextmanager
    def pushTransform(self, transformOrVec: Optional[Union[Transform, ivec3]] = None):
        """Creates a context that reverts all changes to self.transform on exit.

        If [transformOrVec] is not None, it is pushed to self.transform on enter.

        Can be used to create a local coordinate system on top of the current local coordinate
        system.

        Not to be confused with Transform.push()!"""

        originalTransform = deepcopy(self.transform)
        if transformOrVec is not None:
            self.transform @= toTransform(transformOrVec)
        try:
            yield
        finally:
            self.transform = originalTransform

# Improving Editor performance

## Introduction

The {class}`Editor` class has a number of features that can significantly
improve performance, but which are disabled by default because they can
occasionally cause unexpected behavior.

## Block Buffering

The performance feature with by far the greatest effect is *block buffering*.
When buffering is enabled, blocks no longer get placed immediately, but are
instead collected in a buffer until the buffer is full. They are then
sent to the GDMC HTTP interface all at once, in a single request.

Buffering can be enabled by setting {attr}`.Editor.buffering` to `True`:

```python
editor.buffering = True
```

The buffer limit (the number of blocks that are buffered before the buffer is
flushed) can be accessed and modified through {attr}`.Editor.bufferLimit`:

```python
# Set buffer limit to 1024
editor.bufferLimit = 1024
```

If you disable buffering (with `editor.buffering = False`) or if the program
ends, the buffer is automatically flushed. You can also manually trigger a
buffer flush with {meth}`.Editor.flushBuffer`.

Buffering is almost completely transparent: the behavior of your program will
probably not change if you turn it on. For example, block retrieval functions
like `Editor.getBlock()` take the buffer into account:

```python
from gdpc import Editor, Block

editor = Editor()
editor.buffering = True

editor.placeBlock((1,2,3), Block("red_concrete"))
block = editor.getBlock((1,2,3))
print(block) # Prints "red_concrete" even though the block is still in the buffer.
```

The only side-effects are:
- Block placements become delayed.
- If the Minecraft world is changed by something other than the buffering
  `Editor` (such as as a different `Editor`, an in-game effect like flowing
  water or a piston, or an in-game player) after blocks have been buffered but
  before they have been placed, then the buffered blocks may overwrite those
  changes.

Because of its transparency and significant performance impact, it is highly
recommended to enable buffering for most GDPC programs.

Some more notes on buffering:
- If you call `Editor.placeBlock()` with an
  [Iterable](https://docs.python.org/3/glossary.html#term-iterable) of positions
  rather than a single one (as explained in [Overview - Building
  shapes](#building-shapes)), buffering is automatically temporarily enabled for
  that call. The same holds for the functions from the {mod}`.geometry` module.
- {meth}`.Editor.runCommand` has an optional parameter `syncWithBuffer`. If
  buffering is enabled and this parameter is set to `True`, the command is
  deferred until after the next buffer flush. This can be useful if the command
  depends on possibly buffered block changes.


## Block caching

Another toggleable performance feature is *block caching*. While buffering is
for speeding up block *placement*, caching is for speeding up block *retrieval*.
When caching is enabled, the `Editor` caches the last {attr}`.Editor.cacheLimit`
placed or retrieved blocks and their positions. If a block at a cached position
is later accessed (such as with `Editor.getBlock()`), the block is retrieved
from the cache instead of the HTTP interface.

Caching can be enabled by setting {attr}`.Editor.caching` to `True`:

```python
editor.caching = True
```

The cache limit (the maximum number of cached positions) can be
accessed and modified through {attr}`.Editor.cacheLimit`:

```python
# Set cache limit to 8192
editor.cacheLimit = 8192
```

Note that if buffering is enabled, the buffer also acts as a cache (to guarantee
transparency). If both buffering and caching are enabled, this "buffering cache"
supersedes the "caching cache".

Just like buffering, caching is mostly transparent. However, caching does have a
slightly more significant side-effect: if the world is changed by something
other than the caching `Editor`, the cache will **not** reflect those changes,
and `Editor.getBlock()` may return incorrect blocks.

Although regular caching can greatly improve performance when the same positions
are accessed multiple times, you do still need to pay the cost for each first
retrieval. If you need to access many blocks in a fixed area, it is recommended
to use a [world slice](#world-slices-and-heightmaps) instead. This can however
be simplified with the next `Editor` feature...


## World slice caching

As was briefly mentioned in [Overview - World slices and
heightmaps](#world-slices-and-heightmaps), it is also possible to set a world
slice as an `Editor` cache. If a block or biome is requested whose position is
contained in the world slice cache and which has not been changed since the
world slice was loaded, then the `Editor` reads it from the world slice instead
of sending a HTTP request.

To load a WorldSlice and use it as a cache, call {meth}`.Editor.loadWorldSlice`
with `cache=True`:

```python
editor.loadWorldSlice(someRect, cache=True)
```

World slice caching and regular caching are quite similar, but there are some
differences. The regular cache acts as a "sparse cache", containing only a
limited amount of blocks, but having no restrictions on their spatial distance.
In contrast, a world slice cache acts is a "dense cache": it contains *all*
blocks within its bounds, but none outside of it. Furthermore, a world slice
cache also works for biomes, while the regular cache does not.

It is possible to use both regular caching and world slice caching at the same
time. If a block is available in both caches, the world slice cache takes
precedence (because the lookup is faster).

Unlike the regular cache, a world slice cache is not updated if you edit the
world. The `Editor` instead maintains a boolean array that indicates which
blocks have been changed since the WorldSlice was cached, and it only uses
the cached WorldSlice for unchanged blocks.

World slice caching does have the same side-effect as regular caching: if a
block is changed by something other than the caching `Editor`, the block is not
marked as invalid in the boolean array, and `Editor.getBlock()` may therefore
return outdated blocks.

If you load a new world slice with `Editor.loadWorldSlice(cache=True)`, the
stored world slice is replaced and all positions are marked as valid again.
There is a convenience method to load and cache a new world slice for the same
area as the currently cached one: {meth}`.Editor.updateWorldSlice`.

If you need direct access to the stored `WorldSlice` (for example,
to access its heightmaps), it is available as {attr}`.Editor.worldSlice`.
For advanced usage, the boolean array that indicates which blocks are valid is
available as {attr}`.Editor.worldSliceDecay`.


## Multithreaded buffer flushing

The `Editor` class has one more optional performance feature, but this one is a
bit more dangerous: it can use multiple threads to perform buffer flushing. The
speed impact of this feature seems to differ widely between systems. On some
machines, it has no effect at all, while on others, the effect can be
significant.

Using multithreaded buffer flushing with only one worker thread (the default
amount) is relatively safe, but usually does not improve performance much. To
use multithreaded buffer flushing, set {attr}`.Editor.multithreading` to `True`.
Note that buffering must also be enabled.

```python
editor.buffering = True
editor.multithreading = True
```

If you disable multithreading (with `editor.multithreading = False`) or if the
program ends, any remaining buffer flush tasks are automatically waited upon.
You can also manually await all pending buffer flushes with
{meth}`.Editor.awaitBufferFlushes`. (You may want to call
{meth}`.Editor.flushBuffer` first.)

It is also possible to use more than one worker thread. On some systems, this
has been shown to improve performance significantly. However, it comes with a
**MAJOR** side-effect: it will make the `Editor` unable to guarantee that blocks
will be placed in the same order as they were issued. If buffering or caching is
used, this can also cause the caches to become inconsistent with the actual
world, even if only the multithreading `Editor` is modifying it. Although the
speedup can be convenient during development, multithreading is therefore **NOT
RECOMMENDED** for production code. If you enable multithreaded buffer flushing
with more than one worker thread, GDPC will also log a warning.

Regardless, here's how to enable it:

```python
# Set the amount of worker threads to 4 (causing a warning to be logged).
editor.multithreadingWorkers = 4
```


## Initializing an Editor with performance features enabled

Instead of using the properties (e.g. {attr}`.Editor.buffering`), you can also
construct an `Editor` instance with certain features enabled immediately:

```python
editor = Editor(buffering=True, caching=True, cacheLimit=1024)
```

See the [API reference](../api/gdpc.editor.rst) for more details.

{#improving-performance}
# Improving performance

The {class}`Editor` class has a number of features that can significantly
improve performance, but which are disabled by default because they can
occasionally have unexpected side-effects.

## Block Buffering

The performance feature with by far the greatest effect is the *buffering mode*.
When buffering is enabled, blocks no longer get placed immediately, but are
instead collected in a buffer until the buffer limit is reached. They are then
sent to the GDMC HTTP interface all at once, in a single request. Buffering can
be enabled by constructing the `Editor` with `buffering=True` or by setting
{attr}`.Editor.buffering` to `True`:

```python
# Either of these will do:
editor = Editor(buffering=True)
editor.buffering = True
```

The buffer limit (the number of blocks that are buffered before the buffer is
flushed) can be accessed and modified through {attr}`.Editor.bufferLimit`:

```python
# Set buffer limit to 1024
editor.bufferLimit = 1024
```

You can also manually trigger a buffer flush by calling
{meth}`.Editor.flushBuffer`.

Except for the fact that block placements are delayed, buffering is completely
transparent. Block retrieval functions like `Editor.getBlock()` take the buffer
into account:

```python
from gdpc import Editor, Block

editor = Editor(buffering=True)

editor.placeBlock((1,2,3), Block("red_concrete"))
block = editor.getBlock((1,2,3))
print(block) # Prints "red_concrete" even though the block is still in the buffer.
```

It is highly recommended to enable buffering in your programs. The main reason
why it is not enabled by default, is to avoid confusion when blocks are not
immediately placed.

If you call `Editor.placeBlock()` with an
[Iterable](https://docs.python.org/3/glossary.html#term-iterable) of positions
rather than a single one (as explained in [Overview - Building
shapes](#building-shapes)), buffering is automatically temporary enabled for
that call. The same holds for the functions in the {mod}`.geometry` module.

If you disable buffering (with `editor.buffering = False`) or if the program
ends, the buffer is automatically flushed.


## Caching

## WorldSlice caching

## Multithreaded buffer flushing

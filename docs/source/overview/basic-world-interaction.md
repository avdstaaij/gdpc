# Basic world interaction

<!-- ## The Editor class

In GDPC, All forms of world interaction go through the {class}`.Editor` class --
it serves as the main point of communication between GDPC and the GDMC HTTP
interface, and thus, the Minecraft world. It has methods like
`placeBlock()` and `getBlock()`,
and it stores various settings, resources, buffers and caches related to world
interaction.

The `Editor` class is central to most of GDPC, and as such, it is involved in
many other documentation topics besides this one. This topic page will only
describe its basic functionality. For more specialized features, refer to the
corresponding topic pages or the [API reference](#editor).

The `Editor` class is defined in the {mod}`gdpc.editor` module, but it can also
be imported directly from the root package: {python}`from gdpc import Editor`. -->


## The Editor and Block classes

The most important GDPC objects for world interaction are the {class}`.Editor`
and {class}`.Block` classes.
They are defined in the {mod}`gdpc.editor` and {mod}`gdpc.block`
modules, but they can also be imported directly from the root package:
{python}`from gdpc import Editor, Block`.

The `Editor` class is the main point of communication between GDPC and
the GDMC HTTP interface, and thus, the Minecraft world. Almost every form of
world interaction goes through it. It has methods like
`placeBlock()` and `getBlock()`,
and it stores various settings, resources, buffers and caches related to world
interaction.

<!-- The `Editor` class is central to most of GDPC, and as such, it is involved in
many other overview topics besides this one. This overview page will only
describe its basic functionality. For more specialized features, refer to the
corresponding overview pages or the [API reference](#editor). -->

The `Block` class represents a Minecraft block, which is what you pass
to functions like `Editor.placeBlock` and what functions like
`Editor.getBlock` return. `Block` instances that represent "simple" blocks can
be created by passing the technical ID of the block to the constructor:
{python}`block = Block("stone")`. For more details and more complex cases, see
[Overview - Advanced blocks](#advanced-blocks).


## Getting/setting blocks

Blocks can be placed with {meth}`.Editor.placeBlock`. It has two required
parameters: the (X,Y,Z)-coordinates to place a block at, and the
block to place (a {class}`.Block` object).

```python
from gdpc import Editor, Block

editor = Editor()

editor.placeBlock((0,128,0), Block("red_concrete"))
```

Similarly, blocks can be retrieved with {meth}`.Editor.getBlock`:

```python
block = editor.getBlock((0,128,0))
print(block) # e.g. "minecraft:red_concrete"
```

```{note}
In the snippets above, `(0,128,0)` is an example of a 3D vector: three numbers
that indicate a position in space. In GDPC, any object that "behaves like a
vector" will work for vector parameters. This includes things like tuples, lists
and numpy arrays.
More info will follow in [Overview - Vectors](../overview/vectors.md).
```


## More basic interaction

To get the biome at a position, use {meth}`.Editor.getBiome`. This will return
the biome's namespaced ID, such as "minecraft:plains".

```python
biome = editor.getBiome((0,128,0))
print(biome) # e.g. "minecraft:plains"
```

To run a [Minecraft command](https://minecraft.wiki/w/Commands) in the world,
use {meth}`.Editor.runCommand()`. The leading "/" must be omitted.

```python
editor.runCommand("say hello world!")
```

To get the Minecraft version you're interacting with, use
{meth}`.Editor.getMinecraftVersion()`

```python
version = editor.getMinecraftVersion()
print(version) # e.g. "1.19.2"
```


<!-- ## Checking the connection to the GDMC HTTP interface

... -->

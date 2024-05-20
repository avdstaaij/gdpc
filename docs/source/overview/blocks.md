# Blocks

The basic unit of all Minecraft worlds is the block. In GDPC, blocks are
represented by the {class}`.Block` class. `Block` objects have three attributes:

{attr}`.Block.id` ({python}`str | None`) -- The block's (namespaced) id.
: This is the main identifier that all Minecraft blocks have (e.g.
  "minecraft:stone").
  In GDPC, the standard namespace "minecraft:" can be omitted when placing
  blocks, though it will be there when retrieving them.
  If this is set to `None`, the block represents "nothing". Placing such a block
  has no effect. This is opposed to blocks of air, which do replace existing
  blocks.

{attr}`.Block.states` ({python}`Dict[str, str]`) -- Optional *block states*/*block properties* [^blockstates].
: In Minecraft, block states are simple key-value properties that usually
  denote basic variations in the state of a block. For example, a stairs block
  can be facing in one of six possible directions (north, south, east, west, up,
  down).
  A full list of all block states can be found
  [here](https://minecraft.wiki/w/Block_states).

{attr}`.Block.data` ({python}`str | None`) -- Optional *block entity data* as an SNBT string.
: Some Minecraft blocks have particularly complex data attached to them, such as
  the items in a chest or the text on a sign. Minecraft stores this kind of data
  in a so-called "block entity" (also known as a "tile entity"). This data is
  stored in the [NBT format](https://minecraft.wiki/NBT_format) (Named Binary Tag), a binary data structure. NBT also
  has a human-readable text representation called
  [SNBT](https://minecraft.wiki/w/NBT_format#SNBT_format) (Stringified NBT). The
  GDMC HTTP Interface and GDPC both use this SNBT format.
  A full list of all blocks with block entities can be found
  [here](https://minecraft.wiki/w/Block_entity).



```{image} ../images/f3-block.png
:width: 500px
:align: right
```

To get the technical ID of a block in Minecraft (like "red_concrete"),
press {keys}`F3` and point at the the block. The ID will be shown at the bottom
right, below "Targeted Block". You can leave out the "minecraft:" part.

To get the ID of a block in your inventory, you can also press {keys}`F3 + H`
and then hover over the block. The ID should be shown at the bottom of the
tooltip.

You can also "delete" a block by placing Block("air") at its position.


[^blockstates]: GDPC uses the term "block states". Note, however, that Minecraft also sometimes uses "BlockState" to refer to the *combination*
  (block id, block states). Yes, the terminology is confusing.

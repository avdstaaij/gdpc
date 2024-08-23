# World slices and heightmaps

Reading many blocks from the world with {func}`.Editor.getBlock()` can quickly
slow down your program, because every block retrieval requires a separate HTTP
request under the hood. To alleviate this issue, you can make use of a
{class}`.WorldSlice` object.

A `WorldSlice` contains all kinds of information about a "slice" of the world,
like blocks, biomes and heightmaps. All of its data is extracted directly from
Minecraft's [chunk format](https://minecraft.wiki/Chunk_format).
World slices take a while to load initially, but accessing data from them is
very fast.

TODO

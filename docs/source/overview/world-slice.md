# World slices and heightmaps

## Introduction

In GDPC, a *world slice* is a snapshot of a box-shaped "slice" of the world,
obtained by requesting a large amount of raw Minecraft world data at once and
parsing it.
World slices serve two purposes:




As opposed to direct world reading functions, like `Editor.getBlock()`, the
data in a WorldSlice is obtained by requesting


1. *Improved performance.*\
   World slices can greatly improve performance when reading many blocks or
   biomes in a fixed area


	Under the hood, GDPC's direct world reading functions
	(like `Editor.getBlock()`) require a separate HTTP request for each call.

    The regular world reading functions, like {func}`.Editor.getBlock()`, can quickly
slow down your program, because under the hood, every block retrieval requires a
separate HTTP request. To alleviate this issue, you can make use of a
{class}`.WorldSlice` object.

They can greatly improve performance when reading many blocks or biomes in
   a fixed area.
   Regular world reading functions, like

2. *Heightmaps.*\
   World slices provide access to multiple *heightmaps*, which can be very
   helpful when building on the world surface.



<!-- As opposed to regular world-reading methods, such as `Editor.getBlock()` and
`Editor.getBiome()`, the information in a world slice is obtained by requesting
a large amount of raw Minecraft world data at once and parsing it. -->




short descripton

purposes:
- faster access to blocks and biomes
- heightmaps - World slices provide access to *heightmaps*, ...



## TODO





Reading many blocks from the world with {func}`.Editor.getBlock()` can quickly
slow down your program, because under the hood, every block retrieval requires a
separate HTTP request. To alleviate this issue, you can make use of a
{class}`.WorldSlice` object.

A `WorldSlice` in

A `WorldSlice` contains all kinds of information about a box-shaped "slice" of
the world, like blocks, biomes and heightmaps. All of its data is extracted
directly from Minecraft's [chunk format](https://minecraft.wiki/Chunk_format).
World slices take a while to load initially, but accessing data from them is
very fast.



TODO
- Is a snapshot
- Getting (directly or via `Editor`)
-`Editor` cache, `.worldSliceDecay`
- Getting blocks and biomes
- Getting heightmaps

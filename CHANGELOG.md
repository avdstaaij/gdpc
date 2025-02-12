# In development

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0** and Minecraft **1.20.2**.


# 7.4.0

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0** and Minecraft **1.20.2**.

**Additions**:
- Added an extensive [documentation website](https://gdpc.readthedocs.io)!
- The transformation system now supports the `half` state of stairs blocks.
- `Rect` and `Box` are now iterable, yielding the same values as `Rect.inner`/`Box.inner`. (Thanks [Flashing-Blinkenlights](https://github.com/Flashing-Blinkenlights)!)

**Deprecations**:
- `Rect.inner` and `Box.inner` are deprecated, since the classes can now be directly iterated over.


# 7.3.0

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0** and Minecraft **1.20.2**.

**Additions:**
- Added ZERO_2D/ZERO_3D/ZERO constants to `vector_tools`. (Thanks [Flashing-Blinkenlights](https://github.com/Flashing-Blinkenlights)!)
- Added various ordered vector list constants to `vector_tools`. (Thanks [Flashing-Blinkenlights](https://github.com/Flashing-Blinkenlights)!)
- Added `utils.rotateSequence`. (Thanks [Flashing-Blinkenlights](https://github.com/Flashing-Blinkenlights)!)

**Fixes:**
- Made some previously mutable constants immutable. (Thanks [Flashing-Blinkenlights](https://github.com/Flashing-Blinkenlights)!)


# 7.2.0

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0** and Minecraft **1.20.2**.

**Additions:**
- Added `vector_tools.rotate2Ddeg` and `rotate3Ddeg`. (Thanks [Flashing-Blinkenlights](https://github.com/Flashing-Blinkenlights)!)
- Added many new constants to `vector_tools`. (Thanks [Flashing-Blinkenlights](https://github.com/Flashing-Blinkenlights)!)

**Fixes:**
- Added missing return type hints to many functions in `vector_tools`. (Thanks [Flashing-Blinkenlights](https://github.com/Flashing-Blinkenlights)!)


# 7.1.0

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0** and Minecraft **1.20.2**.

**Additions**
- Added `interface` bindings for GDMC-HTTP `GET /entities` and `GET /players`. (Thanks [Niels-NTG](https://github.com/Niels-NTG)!)


# 7.0.0

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0** and Minecraft **1.20.2**.

**Breaking:**
- GDPC now assumes Minecraft 1.20.2 in places where the Minecraft version matters (see the change below).
- Updated `signData()`, `signBlock()` and `placeSign()` to the Minecraft 1.20 format, which supports text on both sides of signs. The parameter names have changed, but the positions of the original parameters have not.
- Changed the VecLike classes to `Protocol`s, making them play nicer with static type checkers (thanks [boerdereinar](https://github.com/boerdereinar)!). It is highly unlikely that this will affect your code.

**Additions:**
- Added `interface` functions for the GDMC-HTTP `/structure` endpoint. (Thanks [Niels-NTG](https://github.com/Niels-NTG) and [ZeLiu1](https://github.com/ZeLiu1)!)
- Made `Rect` and `Box` hashable. (Thanks [Niels-NTG](https://github.com/Niels-NTG)!)

**Fixes:**
- Fixed `Transform.inverted()`/`Transform.__invert__()`, which were implemented incorrectly and did not actually give the inverse in some cases. (Discovered by [xlenstra](https://github.com/xlenstra).)
- Fixed certain `vector_tools` functions that accept `Iterable` arguments failing when receiving a `Set`. In particular, this fixes `circle(filled=True)` and related calls. (Discovered by AHumanIBelieve and ShinryuSHH on Discord.)
- Fixed `bookData()` adding extra empty lines after full-width lines.
- Fixed `Transform.apply()` failing when receiving a non-`pyglm` vector.
- Fixed `lineSequence` functions failing for non-sizable `Iterable`s.
- Fixed `filled3D(Array)` functions failing when a bounding box is not passed.
- Fixed `WorldSlice` crashing when the world has a non-standard height. (Discovered by MrSQ on Discord.)
- Updated all Minecraft wiki links to use [minecraft.wiki](https://minecraft.wiki).


# 6.1.1

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0**.

**Fixes:**
- Fixed `Block.fromBlockStateTag()` -- and therefore, `WorldSlice.getBlock()` -- crashing when retrieving certain block entities. (Discovered by [Phobos97](https://github.com/Phobos97).)


# 6.1.0

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0**.

**Additions:**
- Added sphere and ellipsoid functions to `vector_tools` and `geometry`. (Thanks [cmoyates](https://github.com/cmoyates)!)

**Fixes:**
- Fixed in-buffer block overwrites not going to the end of the buffer, which could sometimes cause incorrect behavior. (Discovered by [Phobos97](https://github.com/Phobos97).)


# 6.0.3

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0**.

**Fixes:**
- Fixed a bug when constructing a `Model` without blocks. (Thanks [Phobos97](https://github.com/Phobos97)!)
- Fixed off-by-one in `Rect`/`Box` `.corners`.


# 6.0.2

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0**.

**Fixes:**
- Added missing "not"s to some WorldSlice docstrings.
- Fixed some broken `Box` functions. (Thanks [MTTVDN](https://github.com/MTTVDN)!)


# 6.0.1

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0**.

**Fixes:**
- Set `scikit-image` minimum version to `0.19.0`.


# 6.0.0 (Transformative Update)

Starting from this version, GDPC will use
[semantic versioning](https://semver.org/).

Compatible with GDMC-HTTP **>=1.0.0, <2.0.0**.\
Note that the GDMC-HTTP repository has changed! It can now be found at
<https://github.com/Niels-NTG/gdmc_http_interface>


## Changes

This version is a complete overhaul of the entire library. It brings **many,
many** new features, improvements and bugfixes, but it also breaks compatibility
almost everywhere.

Due to the sheer amount of breaking changes, this entry won't list them
exhaustively. You can assume that nothing is compatible. It is recommended to
re-learn the API using the examples and tutorials mentioned in the README.
The good news is that the significant architectural improvements in this version
will reduce the need for substantial breaking changes in the future.

Now, on to the changes - mostly in prose. This listing may be incomplete, but
should mention everything major.


### Compatibility with Minecraft 1.19.2

Mostly thanks to work in the GDMC-HTTP mod, GDPC is now compatible with
Minecraft 1.19.2! On the technical side, that means it now supports negative
Y-coordinates and cubic biomes.

Unfortunately, the GDMC-HTTP mod is not backwards compatible with Minecraft
1.16.5, so support for Minecraft 1.16.5 has been dropped. (Strictly speaking,
GDPC itself is still compatible with 1.16.5, but its only HTTP backend - the
GDMC-HTTP mod - is not.)


### New and renamed modules

All of GDPC's modules have changed substantially, but many have held the same
general purpose. Most of these have been renamed, however:
- `direct_interface` -> `interface`
- `interface` -> `editor`\
  (The `Interface` class is now the `Editor` class.)
- `toolbox` -> `minecraft_tools` and `editor_tools`\
  The latter contains tools that require an `Editor`, while the former contains
  tools that don't.
- `bitarray` and `worldLoader` -> `world_slice`

Lots of new modules have been added:
- `block`: Provides the `Block` class, more on this later.
- `block_state_tools`: Provides tools to work with orientation-related
  [block states](https://minecraft.wiki/Block_states).
  This is mainly for internal use.
- `exceptions`: Contains exception classes for GDPC.
- `model.py`: Provides the `Model` class, which can be used to store a structure
  in memory. Future versions will add features like scanning in models from
  Minecraft.
- `nbt_tools`: Provides some low-level tools for the
  [NBT format](https://minecraft.wiki/NBT_format). This is mainly for
  internal use.
- `transform`: Provides the `Transform` class and related utilities, more on
  this later.
- `utils`: Provides various generic utilities that GDPC uses internally, but
  may also be useful to others.
- `vector_tools`: Provides lots of vector math utilities, including the helpful
  classes `Rect` and `Box`. Vectors are described further below.


### Tutorials

The `examples` directory now contains various small tutorial-like scripts that
demonstrate and explain one particular feature of GDPC.


### Editor class

The class that was previously called `Interface` is now called `Editor`, and
has received many new features. Most of these are described below. An important
change, however, is that there is no longer a "global" editor: there is no
more free `placeBlock()` function. You have to create an `Editor` instance and
then use `Editor.placeBlock()`.


### Block class

This version introduces the `Block` class, which represents a Minecraft block.
The API for placing and retrieving blocks now uses this class instead of
strings: you place and get `Block("stone")` instead of `"stone"`.

Blocks consist of three components:
- A (namespaced) id (e.g. `minecraft:chest`).
- Optional [block states](https://minecraft.wiki/Block_states)
  (e.g. `facing=north`).
- Optional [block entity](https://minecraft.wiki/Block_entity)
  (S)NBT data (e.g. `{Items: [{Slot: 13b, id: "apple", Count: 1b}]}`).

The `Block` class supports all three of these. In other words, GDPC now fully
supports both placing and retrieving blocks with block states and NBT data!
No longer do you need to send separate commands to modify a block's NBT data
after placing it!
See `Block.py` and the advanced block tutorial for more details.

The `Block` class also plays an important role in enabling GDPC's new
transformation system - more on that further below.


### Vectors

All GDPC functions that take position paramaters (i.e. nearly all of them) now
work with *vectors*, rather than separate x, y and z coordinates. GDPC is
however quite flexible in the types of vectors it accepts: any sequence of
numbers will do. That includes things like lists, tuples, numpy arrays and more.

Internally, GDPC now uses vector objects from the `pyGLM` package. Whenever a
GDPC function returns a vector, it will also be from this module. The `pyGLM`
vectors support various vector math operators that make lots of common
operations much easier and faster. They are also the basis of many of the more
advanced additions listed below.

See the the vector tutorial for more details about vectors.


### Transformations

The most important addition is probably the transformation system. It allows you
to "transform" your frame of reference for placing and retrieving blocks, so
that you can always build using local coordinates instead of global ones. The
idea is based on the use of transformation matrices in typical 3D graphics
applications.

If you're programming, say, a house function, you could just always build the
house at (0,0,0) with its door pointing north, and then later call the function
with different transformations to place the house at any position and under any
rotation!

GDPC 5.0.0 already provided a basic transformation system: you could construct
an Interface instance with x, y and z offsets. That is, GDPC 5.0.0 supported
*translations*. This version, however, enhances this with 90-degree rotations
around the Y-axis and flipping/mirroring operations.

At the core of the transformation system lies the `Transform` class, which
essentially acts as a transformation matrix. It stores a translation (a 3D
vector), a rotation around the Y-axis (0, 1, 2 or 3) and a boolean flip vector.
Transforms can be multiplied like matrices, and they can be applied to vectors.

The `Block` class contains functionality that ensures that even *individual
blocks* which have an orientation (such as stairs) are rotated and flipped
correctly.

The `Editor` class now has a `.transform` attribute that defines that editor's
"point of view". It is applied to all block placement and retrieval positions.
You can modify this transform to change the editor's local coordinate system.

See the transformation tutorial for more details about the transformation
system.


### Other changes

**Additions:**

- GDPC is now fully type hinted!

- Some important objects are now re-exported from `__init__.py`. That means
  you can now use\
  `from gdpc import Editor, Block, Transform, Rect, Box`.

- Mostly thanks to a change in GDMC-HTTP, you can now interact with different
  dimensions! Simply modify `Editor.dimension`
  (e.g. `Editor.dimension = "the_nether"`).

- Mostly thanks to a change in GDMC-HTTP, you can now directly retrieve biomes
  using `Editor.getBiome()`.

- `Editor.placeBlock()` can now place multiple of the same block at once, with
  improved performance.

- `Editor.runCommand()` can now run the command with a specific execution
  position.

- `Editor.runCommand()` can now optionally defer the command until after the
  next block buffer flush.

- `Editor` now has a new optional performance feature: it can automatically
  multithread buffer flushes. Note however that this feature only rarely
  improves performance and may come with some significant downsides. See the
  editor performance tutorial for more information.

- You can now change the GDMC HTTP interface host from the default
  `"http://localhost:9000"` - simply modify `Editor.host`.

- Block palettes now support "no placement" entries - simply use `Block(None)`.
  Contrary to `Block("air")`, these "empty" blocks don't overwrite existing
  blocks on placement.

- For most functions in `geometry`, there is now a corresponding function in
  `vector_tools` that will yield all points of the shape directly, without
  placing any blocks.

- `bookData()` (previously called `writeBook()`) now properly escapes the passed
  text, title, author and description strings. You can now freely use characters
  like `'` and `\`.

- `lookup.py` has been updated with all Minecraft 1.18 blocks, and most 1.19
  blocks.


**Changes:**

- GDPC no longer prints anything directly. Most prints have been removed or
  replaced with exceptions, and for those where this was not possible, GDPC now
  uses the `logging` module. You can now disable all GDPC console output using
  `logging.getLogger("gdpc").setLevel(logging.CRITICAL + 1)`.

- Exception messages are no longer colored.

- GDPC no longer checks the build area - it no longer prints warnings when
  placing blocks outside of it. Build area warnings/enforcement may be added
  to GDMC-HTTP in a future version.

- Various custom exception types have been added for specific GDPC errors.

- Exception messages for GDMC HTTP interface-related errors are now more
  descriptive.

- Various functions that previously silently returned a default value on error
  now throw an exception instead.

- All requests to the GDMC HTTP interface now perform some retries before
  throwing an exception. The amount of retries is configurable.

- GDPC no longer sends any requests on import, so it will no longer crash on
  import when Minecraft is not running.

- Thanks to a change in GDMC-HTTP, you now only need to place one block of a
  multi-block object such as a door or a bed to place the entire thing.

- The block buffer of an `Editor` now also acts as a cache, ensuring that the
  buffering mode is fully transparent.

- The integration of `Editor` and `WorldSlice` has been improved. See the
  editor performance tutorial for more details.

- Some functions have been removed from `geometry`, and various new ones have
  been added.

- `bookData()` no longer adds hardcoded pages to the created book.

- Metadata dunders like `__version__` are now only available from `__init__.py`,
  but there are now more of them.


**Fixes:**

- Lots of bugs have been fixed, though no doubt many new ones have been
  introduced as well. ;)


# Older versions

For older versions, see
<https://github.com/nikigawlik/gdmc_http_client_python/releases>

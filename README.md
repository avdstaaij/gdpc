# GDPC

GDPC (Generative Design Python Client) is a Python framework for use in conjunction with the [GDMC-HTTP](https://github.com/Niels-NTG/gdmc_http_interface) mod for Minecraft Java edition.
It is designed for the [Generative Design in Minecraft Competition (GDMC)](https://gendesignmc.engineering.nyu.edu).

You need to be playing in a Minecraft world with the mod installed to use the framework.

The latest version of GDPC is compatible with GDMC-HTTP versions **>=1.0.0, <2.0.0** and Minecraft **1.19.2** (see [note](#note-on-supported-minecraft-version)).


## Quick example

```python
from gdpc import Editor, Block, geometry

editor = Editor(buffering=True)

# Get a block
block = editor.getBlock((0,48,0))

# Place a block
editor.placeBlock((0,80,0), Block("stone"))

# Build a cube
geometry.placeCuboid(editor, (0,80,2), (2,82,4), Block("oak_planks"))
```

## What's the difference between GDMC, GDMC-HTTP and GDPC?

These abbreviations are all very similar, but refer to different things.

**GDMC:** Short for the [Generative Design in Minecraft Competition](https://gendesignmc.engineering.nyu.edu), a yearly competition for generative AI systems in Minecraft.
The challenge is to write an algorithm that creates a settlement while adapting to the pre-existing terrain. The competition also has a [Discord server](https://discord.gg/YwpPCRQWND).

**GDMC-HTTP:** A [Minecraft Forge mod](https://github.com/Niels-NTG/gdmc_http_interface) that provides a HTTP interface to edit the world.
It allows you to modify the world live, while you're playing in it. This makes it possible to iterate quickly on generator algorithms.
The mod is an official submission method for the competition.

**GDPC:** This repository (notice the "P"). A Python framework for interacting with the GDMC-HTTP interface.
It provides many high-level tools that make working with the interface much simpler.


## Installation

GDPC requires Python 3.7 or above. It is available on PyPI; to install, run:
```
python3 -m pip install gdpc
```
To update, run:
```
python3 -m pip install --upgrade gdpc
```
On Windows, you may need to replace `python3` with `py`.

If you would like to install the latest cutting-edge development version directly from GitHub, replace `gdpc` with\
`git+https://github.com/avdstaaij/gdpc`\
For more information on installing from GitHub (such as getting old versions), see the [pip documentation](https://pip.pypa.io/en/stable/topics/vcs-support/).


## Tutorials and examples

There are various tutorial scripts that will help to get you started:
| Tutorial                                                                                                               | Description                                                                   |
|------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| [Hello block](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/tutorials/1_hello_block.py)               | Place and retrieve a single block in the world.                               |
| [Vectors](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/tutorials/2_vectors.py)                       | Use vector math and some of GDPC's various vector utilities.                  |
| [Build area](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/tutorials/3_build_area.py)                 | Get the specified build area and use it to place a block inside the bounds.   |
| [World slice](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/tutorials/4_world_slice.py)               | Load and use a world slice for faster read access.                            |
| [Geometry](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/tutorials/5_geometry.py)                     | Use the geometry module to place geometrical regions of blocks.               |
| [Advanced blocks](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/tutorials/6_advanced_blocks.py)       | Place blocks with block states and block entity data, and use block palettes. |
| [Editor performance](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/tutorials/7_editor_performance.py) | Use the Editor class's various optional performance features.                 |
| [Transformation](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/tutorials/8_transformation.py)         | Use GDPC's powerful transformation system.                                    |

Some practical examples are also available, though they're slightly older and may not reflect the latest features:

| Example                                                                                          | Description                                                                           |
|--------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| [Visualize map](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/visualize_map.py) | Displays a map of the Minecraft world using OpenCV.                                   |
| [Emerald city](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/emerald_city.py)   | Demonstrates basic GDPC functionality by building a simple model of the Emerald City. |

**Note:** the links above always point to tutorials/examples for the latest release of GDPC. To view the examples for an older version, switch to the tag for that version (using the dropdown box at the top left of the file list, where it probably says "master"), and manually navigate to the examples.


## Note on supported Minecraft version

We list a specific compatible version of Minecraft, but most of GDPC actually supports a wide range of Minecraft versions.
In particular, basic block getting and setting should work with any Minecraft version for which there is a compatible version of GDMC-HTTP.
The parts of GDPC that may not be compatible with Minecraft versions other than the listed one are those that interact with "Minecraft data". These include:
- Rotation and flipping of individual blocks.
- Utility functions from the `minecraft_tools` and `editor_tools` modules that generate Minecraft data, such as `bookData` and `placeSign`.
- The `WorldSlice` class and associated functions like `Editor.loadWorldSlice()`.

If a breaking change needs to be made to support a newer version of Minecraft, it will always be listed as such in the [Changelog](CHANGELOG.md).

We are working on fully supporting multiple versions of Minecraft simultaneously ([#99](https://github.com/avdstaaij/gdpc/issues/99)), but this probably won't be done soon.


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information about how to contribute.


## Acknowledgements

GDPC was progressively developed with the help of various members of the GDMC community. Of special note are [Niki Gawlik](https://github.com/nikigawlik), who started both GDMC-HTTP and GDPC, and [Blinkenlights](https://github.com/flashing-blinkenlights), who previously maintained the project.

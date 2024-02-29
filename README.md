# GDPC 6.0 (Transformative Update)

GDPC (Generative Design Python Client) is a Python framework for use in conjunction with the [GDMC-HTTP](https://github.com/Niels-NTG/gdmc_http_interface) mod for Minecraft Java edition.
It is designed for the [Generative Design in Minecraft Competition (GDMC)](https://gendesignmc.engineering.nyu.edu).

You need to be playing in a Minecraft world with the mod installed to use the framework.

The latest version of GDPC is compatible with GDMC-HTTP versions **>=1.0.0, <2.0.0**.


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

These abbreviations are all very similar, but stand for different things.

GDMC is short for the [Generative Design in Minecraft Competition](https://gendesignmc.engineering.nyu.edu), a yearly competition for generative AI systems in Minecraft.
The challenge is to write an algorithm that creates a settlement while adapting to the pre-existing terrain. The competition also has a [Discord server](https://discord.gg/YwpPCRQWND).

[GDMC-HTTP](https://github.com/Niels-NTG/gdmc_http_interface) is a Minecraft Forge mod that provides a HTTP interface to edit the world.
It allows you to modify the world live, while you're playing in it. This makes it possible to iterate quickly on generator algorithms.
The mod is an official submission method for the competition.

GDPC (notice the "P") is a Python framework for interacting with the GDMC-HTTP interface.
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

There are various [**tutorial scripts**](https://github.com/avdstaaij/gdpc/tree/latest-release/examples/tutorials) that will help to get you started.

Some practical examples are also available, though they're slightly older and may not reflect the latest features:
- [**`visualize_map.py`**](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/visualize_map.py): Displays a map of the Minecraft world using OpenCV.
- [**`emerald_city.py`**](https://github.com/avdstaaij/gdpc/blob/latest-release/examples/emerald_city.py): Demonstrates basic GDPC functionality by building a simple model of the Emerald City.

**Note:** the links above always point to examples for the latest release of GDPC. To view the examples for an older version, switch to the tag for that version (using the dropdown box at the top left of the file list, where it probably says "master"), and manually navigate to the examples.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information about how to contribute.

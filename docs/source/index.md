# Welcome to GDPC's documentation!

GDPC (Generative Design Python Client) is a Python framework for use with the [GDMC-HTTP Interface mod](https://github.com/Niels-NTG/gdmc_http_interface) for Minecraft Java edition.

The GDMC-HTTP mod provides a HTTP interface that allows you to edit a Minecraft world live, while you're playing in it, making it possible to rapidly iterate on generative algorithms. GDPC provides Python bindings for the mod, along with many high-level tools that make development much easier.

GDPC is primarily designed for the [Generative Design in Minecraft Competition (GDMC)](https://gendesignmc.wikidot.com/), a yearly competion for generative AI systems in Minecraft where the challenge is to write an algorithm that creates a settlement that adapts to the pre-existing terrain. Feel free to join us on [Discord](https://discord.gg/YwpPCRQWND)!


Quick code example:
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




```{toctree}
:hidden:

getting-started/index
api/index
changelog/index
```

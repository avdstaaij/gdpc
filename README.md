# GDPC

GDPC (Generative Design Python Client) is a Python framework for the [GDMC HTTP
Interface mod](https://github.com/Niels-NTG/gdmc_http_interface) for Minecraft
Java edition.

The GDMC HTTP mod implements a HTTP interface that allows you to edit a
Minecraft world live, while you're playing in it, making it possible to rapidly
iterate on generative algorithms. GDPC provides Python bindings for the
GDMC-HTTP interface, along with many high-level tools that make development much
easier.

GDPC is primarily designed for the [Generative Design in Minecraft Competition
(GDMC)](https://gendesignmc.wikidot.com/), a yearly competition for procedural
generation in Minecraft where the challenge is to write an algorithm that
creates a settlement that adapts to the pre-existing terrain. Feel free to join
us on [Discord](https://discord.gg/YwpPCRQWND)!


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


## Documentation

You can find installation instructions, guides and an API reference in our
documentation on [Read the Docs](https://gdpc.readthedocs.io)!


## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information about how to contribute.


## Acknowledgements

GDPC was progressively developed with the help of various members of the GDMC community. Of special note are [Niki Gawlik](https://github.com/nikigawlik), who started both GDMC-HTTP and GDPC, and [Blinkenlights](https://github.com/flashing-blinkenlights), who previously maintained the project.

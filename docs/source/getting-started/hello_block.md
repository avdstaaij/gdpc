# Hello block

The following snippet uses GDPC to place and retrieve a single block:

```python
from gdpc import Editor, Block

# Create an editor object.
# The Editor class is the main point of communication between GDPC and the
# Minecraft world.
editor = Editor()

# Place a block of red concrete at (X=0, Y=80, Z=0)!
editor.placeBlock((0,80,0), Block("red_concrete"))

# Retrieve the block at (0,80,0) and print it.
block = editor.getBlock((0,80,0))
print(f"Block at (0,80,0): {block}")
```

```{important}
Make sure you have a world open with the [GDMC HTTP Interface mod](https://github.com/Niels-NTG/gdmc_http_interface) installed! If you don't, GDPC will raise an {exc}`.InterfaceConnectionError`.
```

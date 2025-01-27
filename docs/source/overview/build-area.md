{#the-build-area}
# The build area

## What is it?

The GDMC HTTP interface provides a utility feature called the *build area*: a 3D
box that can be set with a command in-game and which can then be retrieved
with code.

The purpose of the build area is to be a standardized and in-game way to specify
the bounds in which your program should operate.
Because it is standardized, it is the main way of doing so in the
[Generative Design in Minecraft Competition (GDMC)](https://gendesignmc.wikidot.com/).
It also saves you the effort of implementing an input system for the build area
yourself (such as a command-line interface).


## Setting the build area

To set the build area, use the following in-game command:
```
/setbuildarea <xFrom> <yFrom> <zFrom> <xTo> <yTo> <zTo>
```
The six parameters should be set to the coordinates of two corners (inclusive)
of the desired build area.

The command supports Minecraft's
[Relative coordinate notation](https://minecraft.wiki/Coordinates#Commands):
a parameter value of `~10` indicates "the player's position in that axis, plus
10 blocks".
For example, the following command would set the build area to a 64x256x64 box
starting at the player's current (X,Z)-position and spanning from Y=0 to Y=255:

```
/setbuildarea ~ 0 ~ ~63 255 ~63
```

```{image} ../images/setbuildarea-example.png
:width: 10000
```

```{tip}
You can re-use a previous `/setbuildarea` command by pressing {keys}`Up` while
the chat is open. This is particularly useful when using relative coordinates,
like in the above example.
```


## Retrieving the build area

To retrieve the build area in your program, use {meth}`.Editor.getBuildArea`.
It returns the build area as a {class}`.Box` object:

```python
from gdpc import Editor

editor = Editor()

buildArea = editor.getBuildArea()
```

```{note}
In GDPC, the build area is merely a suggestion: its bounds are not enforced. It
is up to you to request the build area and adhere to it. Future versions may
however add (optional) enforcement.
```

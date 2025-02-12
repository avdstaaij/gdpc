# Installation


## Prerequisites

To use GDPC, you first need to install Minecraft Java edition and the
[GDMC HTTP Interface mod](https://github.com/Niels-NTG/gdmc_http_interface).

The version of GDPC whose docs you're currently looking at is compatible
with GDMC HTTP versions **>=1.0.0, <2.0.0** and Minecraft **1.20.2**.


If you've correctly installed the GDMC-HTTP mod, you should be able to use
the `/setbuildarea` command in-game:

```{image} ../images/setbuildarea.png
:width: 300px
:align: center
```


## Installing GDPC

GDPC is available on [PyPI](https://pypi.org/project/gdpc/); to install, run:
```
python3 -m pip install gdpc
```
To update, run:
```
python3 -m pip install --upgrade gdpc
```

On Windows, you may need to replace `python3` with `py`.

```{note}
If you would like to install the latest cutting-edge development version
directly from GitHub, replace `gdpc` with
`git+https://github.com/avdstaaij/gdpc`.
For more information on installing from GitHub (such as getting old versions),
see the [pip documentation](https://pip.pypa.io/en/stable/topics/vcs-support/).
```


## Note on supported Minecraft version

We list a specific compatible version of Minecraft, but most of GDPC actually
supports a wide range of Minecraft versions. In particular, basic block getting
and setting should work with any Minecraft version for which there is a
compatible version of GDMC-HTTP. The parts of GDPC that may not be compatible
with Minecraft versions other than the listed one are those that interact with
"Minecraft data". For those already familiar with GDPC, these include:
- Rotation and flipping of individual blocks.
- Utility functions from the `minecraft_tools` and `editor_tools` modules that
  generate Minecraft data, such as `bookData` and `placeSign`.
- The `WorldSlice` class and associated functions like
  `Editor.loadWorldSlice()`.

We have [plans](https://github.com/avdstaaij/gdpc/issues/99) for fully
supporting multiple versions of Minecraft simultaneously, but this probably
won't be done anytime soon.

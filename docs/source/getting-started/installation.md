# Installation


## Prerequisites

To use GDPC, you first need to install Minecraft Java edition and the
[GDMC-HTTP Interface mod](https://github.com/Niels-NTG/gdmc_http_interface).


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

On Windows, you may need to replace `python3` with `py`.

```{note}
If you would like to install the latest cutting-edge development version directly from GitHub, replace `gdpc` with `git+https://github.com/avdstaaij/gdpc`.
For more information on installing from GitHub (such as getting old versions), see the [pip documentation](https://pip.pypa.io/en/stable/topics/vcs-support/).
```

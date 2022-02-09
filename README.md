## GDPC 5.0

GDPC (Generative Design Python Client) is a framework for use in conjunction with the [Minecraft HTTP Interface Mod](https://github.com/nilsgawlik/gdmc_http_interface) built for the [GDMC competition](https://gendesignmc.engineering.nyu.edu).

Requirements are in `requirements.txt`. Functionality is not guaranteed with older versions.

You need to be playing in a Minecraft world with the mod installed to use the framework.

### Installation
**Keep in mind that tool and example scripts are not included in the package!** See 'Scripts' below for details.

To install the latest stable release, type one of the following commands:
- On Linux/MacOS: `python3 -m pip install gdpc`
- On Windows: `py -m pip install gdpc`

For the latest sexy-but-might-break-something release, type the following instead:
- On Linux/MacOS: `python3 -m pip install --pre gdpc`
- On Windows: `py -m pip install --pre gdpc`

To update your package, type the following:
- On Linux/MacOS: `python3 -m pip install --update gdpc`
- On Windows: `py -m pip install --update gdpc`

If you would like to install the latest stable version directly from GitHub, replace `gdpc` with

`git+https://github.com/nilsgawlik/gdmc_http_client_python`

For more information on installing from GitHub (such as getting old or dev versions) see the [pip documentation](https://pip.pypa.io/en/stable/topics/vcs-support/).
*(Hint: You can also use this command to import forks of this repository, just change the URL!)*

### Scripts:
To download one of the following scripts, click on the link, then right-click and `Save As...` *(I know it's tedious, if you have a better idea we'd be glad to hear it)*.

- [**`visualizeMap.py`**](https://raw.githubusercontent.com/nilsgawlik/gdmc_http_client_python/master/visualizeMap.py): Displays a map of the Minecraft world using OpenCV
- **`example.py`**: Demonstrates all of the basic gdmc-http functionality by building a very simple village. It uses the utility functions implemented in `worldLoader.py` and `mapUtils.py`.

#### Developed by:
- Nils Gawlik
- Blinkenlights
- Claus Aranha

with contributions from:
- Mayank Jain

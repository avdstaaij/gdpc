"""
The Generative Design Python Client (GDPC) is a Python-based framework for the
Minecraft GDMC HTTP Interface mod.
It was created for use in the Generative Design in Minecraft Competition (GDMC).
"""

__title__            = "gdpc"
__description__      = "The Generative Design Python Client (GDPC) is a Python-based interface for the Minecraft GDMC HTTP Interface mod.\nIt was created for use in the Generative Design in Minecraft Competition (GDMC)."
__url__              = "https://github.com/avdstaaij/gdpc"
__author__           = "Arthur van der Staaij, Blinkenlights, Nils Gawlik"
__author_email__     = "arthurvanderstaaij@gmail.com, blinkenlights@pm.me, nilsgawlik@gmx.de"
__maintainer__       = "Arthur van der Staaij"
__maintainer_email__ = "arthurvanderstaaij@gmail.com"
__license__          = "MIT"
__copyright__        = "Copyright 2022-2023 Arthur van der Staaij, Copyright 2021-2022 Blinkenlights, Copyright 2020-2021 Nils Gawlik"
__version__          = "6.0.0"


from .vector_tools import Rect, Box
from .transform import Transform
from .block import Block
from .world_slice import WorldSlice
from .editor import Editor

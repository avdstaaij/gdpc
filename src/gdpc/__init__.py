"""
GDPC top-level package.

Several important classes are re-exported here, so you can more easily import them.
For example, you can use :python:`from gdpc import Editor` instead of :python:`from gdpc.editor import Editor`.

The following classes are re-exported:

- :class:`.Editor` (from module :mod:`.gdpc.editor`)
- :class:`.WorldSlice` (from module :mod:`.gdpc.world_slice`)
- :class:`.Block` (from module :mod:`.gdpc.block`)
- :class:`.Transform` (from module :mod:`.gdpc.transform`)
- :class:`.Rect`, :class:`.Box` (from module :mod:`.gdpc.vector_tools`)
"""

#: Package title.
#:
#: :meta hide-value:
__title__            = "gdpc"

#: Package description.
#:
#: :meta hide-value:
__description__      = "GDPC (Generative Design Python Client) is a Python framework for use in conjunction with the GDMC-HTTP mod for Minecraft Java edition. It is designed for the Generative Design in Minecraft Competition (GDMC)."

#: Package URL.
#:
#: :meta hide-value:
__url__              = "https://github.com/avdstaaij/gdpc"

#: Package author names.
#:
#: :meta hide-value:
__author__           = "Arthur van der Staaij, Blinkenlights, Nils Gawlik"


#: Package author emails.
#:
#: :meta hide-value:
__author_email__     = "arthurvanderstaaij@gmail.com, blinkenlights@pm.me, nilsgawlik@gmx.de"

#: Package maintainer name.
#:
#: :meta hide-value:
__maintainer__       = "Arthur van der Staaij"


#: Package maintainer email.
#:
#: :meta hide-value:
__maintainer_email__ = "arthurvanderstaaij@gmail.com"

#: Package license.
#:
#: :meta hide-value:
__license__          = "MIT"

#: Package copyright.
#:
#: :meta hide-value:
__copyright__        = "Copyright 2022-2024 Arthur van der Staaij, Copyright 2021-2022 Blinkenlights, Copyright 2020-2021 Nils Gawlik"


#: Package version
#:
#: :meta hide-value:
__version__          = "7.4.0"


from .vector_tools import Rect, Box
from .transform import Transform
from .block import Block
from .world_slice import WorldSlice
from .editor import Editor

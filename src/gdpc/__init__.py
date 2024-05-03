"""
GDPC top-level package.

Several important classes are re-exported here, so you can more easily import them.
For example, you can use :python:`from gdpc import Editor` instead of :python:`from gdpc.editor import Editor`.

The following classes are re-exported:

- :class:`.Editor` (from :mod:`.editor`)
- :class:`.WorldSlice` (from :mod:`.world_slice`)
- :class:`.Block` (from :mod:`.block`)
- :class:`.Transform` (from :mod:`.transform`)
- :class:`.Rect`, :class:`.Box` (from :mod:`.vector_tools`)
"""

#: Package title.
#:
#: :meta hide-value:
__title__            = "gdpc"

#: Package description.
#:
#: :meta hide-value:
__description__      = "The Generative Design Python Client (GDPC) is a Python-based interface for the Minecraft GDMC HTTP Interface mod.\nIt was created for use in the Generative Design in Minecraft Competition (GDMC)."
"""Package description\n\n :meta hide-value:"""

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
__version__          = "7.1.0"


from .vector_tools import Rect, Box
from .transform import Transform
from .block import Block
from .world_slice import WorldSlice
from .editor import Editor

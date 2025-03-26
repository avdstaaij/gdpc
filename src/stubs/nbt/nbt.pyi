from typing import List, Optional, Literal, Sequence, Any
from collections.abc import MutableSequence, MutableMapping


class TAG(object):
    name: Optional[str]


class _TAG_Numeric(TAG):
    value: Any


class _TAG_End(TAG):
    value: Literal[0]


class TAG_Byte(_TAG_Numeric):
    ...


class TAG_Short(_TAG_Numeric):
    ...


class TAG_Int(_TAG_Numeric):
    ...


class TAG_Long(_TAG_Numeric):
    ...


class TAG_Float(_TAG_Numeric):
    ...


class TAG_Double(_TAG_Numeric):
    ...


class TAG_Byte_Array(TAG, MutableSequence[int]):
    value: bytearray


class TAG_Int_Array(TAG, MutableSequence[int]):
    value: List[int]


class TAG_Long_Array(TAG, MutableSequence[int]):
    value: List[int]


class TAG_String(TAG, Sequence[str]):
    value: str


class TAG_List(TAG, MutableSequence[TAG]):
    tags: List[TAG]


class TAG_Compound(TAG, MutableMapping[str, TAG]):
    tags: List[TAG]


class NBTFile(TAG_Compound):
    def __init__(self, filename: Any = None, buffer: Any = None, fileobj: Any = None) -> None: ...

    def write_file(self, filename: Any = None, buffer: Any = None, fileobj: Any = None) -> None: ...

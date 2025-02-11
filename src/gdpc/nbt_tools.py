"""Utilities for working with Minecraft's NBT and SNBT formats"""


from typing import Union
from pathlib import Path
from nbt import nbt


def nbtToSnbt(tag: nbt.TAG) -> str:
    """Recursively converts an NBT tag to an SNBT string"""
    if isinstance(tag, nbt.TAG_List):
        return f"[{','.join(nbtToSnbt(t) for t in tag)}]"
    if isinstance(tag, nbt.TAG_Compound):
        return f"{{{','.join(f'{k}:{nbtToSnbt(v)}' for k, v in tag.items())}}}"
    if isinstance(tag, nbt.TAG_Byte_Array):
        return f"[B;{','.join(f'{b}b' for b in tag.value)}]"
    if isinstance(tag, nbt.TAG_Int_Array):
        return f"[I;{','.join(f'{i}' for i in tag.value)}]"
    if isinstance(tag, nbt.TAG_Long_Array):
        return f"[L;{','.join(f'{l}l' for l in tag.value)}]"
    if isinstance(tag, nbt.TAG_Byte):
        return f"{tag.value}b"
    if isinstance(tag, nbt.TAG_Short):
        return f"{tag.value}s"
    if isinstance(tag, nbt.TAG_Int):
        return f"{tag.value}"
    if isinstance(tag, nbt.TAG_Long):
        return f"{tag.value}l"
    if isinstance(tag, nbt.TAG_Float):
        return f"{tag.value}f"
    if isinstance(tag, nbt.TAG_Double):
        return f"{tag.value}d"
    if isinstance(tag, nbt.TAG_String):
        return repr(tag.value)
    raise TypeError(f"Unrecognized tag type: {type(tag)}")


def parseNbtFile(
    filePath: Union[Path, str]
) -> nbt.NBTFile:
    """Create NBT object from stored NBT file."""
    if isinstance(filePath, str):
        filePath = Path(filePath)
    fileObject = open(filePath, 'rb')
    return nbt.NBTFile(fileobj=fileObject)


def saveNbtFile(
    filePath: Union[Path, str],
    data: Union[bytes, nbt.NBTFile]
) -> None:
    """Save string of bytes or NBTFile object to a file."""
    if isinstance(filePath, str):
        filePath = Path(filePath)

    with open(filePath, 'wb') as file:
        if isinstance(data, bytes):
            file.write(data)
            file.close()
        elif isinstance(data, nbt.NBTFile):
            data.write_file(fileobj=file)
        print(f"File saved to: {filePath}")

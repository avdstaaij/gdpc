"""Utilities for working with Minecraft's NBT and SNBT formats"""
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


def openNBTFile(
    filePath: Path | str = None
):
    """Opens stored NBT file and returns it as a file object."""
    if isinstance(filePath, str):
        filePath = Path(filePath)

    if not filePath.name.endswith('.nbt'):
        filePath = filePath.with_suffix('.nbt')

    return open(filePath, 'rb')


def createByteStringFromNBTFile(
    filePath: Path | str = None
):
    """Get string of bytes derived from stored NBT file."""
    fileObject = openNBTFile(filePath)
    rawBytes = fileObject.read()
    fileObject.close()
    return rawBytes


def createNBTObjectFromNBTFile(
    filePath: Path | str = None
):
    """Create NBT object from stored NBT file."""
    fileObject = openNBTFile(filePath)
    return nbt.NBTFile(fileobj=fileObject)


def saveNBTFile(
    filePath: Path | str = None,
    fileContent: bytes | nbt.NBTFile = b''
):
    if isinstance(filePath, str):
        filePath = Path(filePath)
    elif filePath is None or not isinstance(filePath, Path):
        raise TypeError(f"Not a valid path: {filePath}")
    if not filePath.parent.exists():
        raise FileNotFoundError(f"Save location does not exist: {filePath.parent}")

    if not filePath.name.endswith('.nbt'):
        filePath = filePath.with_suffix('.nbt')

    with open(filePath, 'wb') as file:
        if isinstance(fileContent, bytes):
            file.write(fileContent)
            file.close()
        elif isinstance(fileContent, nbt.NBTFile):
            fileContent.write_file(fileobj=file)
        print(f"File saved to: {filePath}")

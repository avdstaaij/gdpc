"""Utilities for working with Minecraft's NBT and SNBT formats"""


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

"""Utilities for working with Minecraft's NBT format"""


from nbt import nbt


def nbtToPythonObject(tag: nbt.TAG):
    """Recursively converts an NBT tag to a JSON-like structure of built-in Python objects"""
    if isinstance(tag, nbt.TAG_List):
        return [nbtToPythonObject(t) for t in tag]
    if isinstance(tag, nbt.TAG_Compound):
        return {k: nbtToPythonObject(v) for k, v in tag.items()}
    return tag.value


# TODO: pythonObjectToNbt


def pythonObjectToSnbt(obj) -> str:
    """Recursively converts a JSON-like structure of built-in Python objects to an SNBT string"""
    if isinstance(obj, (list, tuple)):
        return f"[{','.join(pythonObjectToSnbt(o) for o in obj)}]"
    if isinstance(obj, dict):
        return f"{{{','.join(f'{k}:{pythonObjectToSnbt(v)}' for k, v in obj.items())}}}"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (str, int, float)):
        return repr(obj)
    raise TypeError(f'Cannot convert type "{type(obj)}" to SNBT')


# TODO: SnbtToPythonObject

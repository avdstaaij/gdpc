# Python module structure



This page gives an overview of how GDPC is structured in terms of importable
modules. You may find it useful when browsing the [API reference](../api/index)
or when contributing to GDPC.

GDPC has a flat module structure, but its modules roughly fit in one of three
categories:

1. **Core interface.**

   These modules are tightly connected, and form the core interface of GDPC.
   Most classes defined in these modules can also be imported directly from
   the root package {mod}`.gdpc`.

   - {mod}`.gdpc.editor`
   - {mod}`.gdpc.world_slice`
   - {mod}`.gdpc.block`
   - {mod}`.gdpc.transform`
   - {mod}`.gdpc.vector_tools`

   <!-- &nbsp; -->


2. **Additional tools.**

   These modules contain additional utility functions/classes that work on top
   of the core interface. You could in principle re-implement anything from
   these modules yourself without losing any functionality.

   - {mod}`.gdpc.minecraft_tools`
   - {mod}`.gdpc.editor_tools`
   - {mod}`.gdpc.geometry`
   - {mod}`.gdpc.lookup`
   - {mod}`.gdpc.model`

   <!-- &nbsp; -->


3. **Internal utilities.**

   These modules contain utilities that are mostly just for the internal
   workings of the library, but may still be useful. It's recommended to use the
   higher-level tools from the previous two categories when possible.

   - {mod}`.gdpc.utils`
   - {mod}`.gdpc.nbt_tools`
   - {mod}`.gdpc.block_state_tools`
   - {mod}`.gdpc.interface`

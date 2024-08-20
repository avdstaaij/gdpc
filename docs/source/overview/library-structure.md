# Library structure

This page gives a general overview of how GDPC is structured, where every
component can be found, and what its typical usage patterns are.

## Structure

### Core interface

The core interface of the library consists of the following modules:
- {mod}`.editor`
- {mod}`.world_slice`
- {mod}`.block`
- {mod}`.transform`
- {mod}`.vector_tools`

The most important objects in GDPC are the {class}`.Editor` and {class}`.Block`
classes. They are defined in the {mod}`gdpc.editor` and {mod}`gdpc.block`
modules, but they can also be imported directly from the root package:
{python}`from gdpc import Editor, Block`.

The `Editor` class is the main point of communication between GDPC and
the GDMC HTTP mod, and thus, the Minecraft world. Every form of world
interaction goes through it. It has methods like
{meth}`~.Editor.placeBlock` and {meth}`~.Editor.getBlock`,
and it stores various settings, resources, buffers and caches related to world
interaction.
The `Block` class represents a Minecraft block, which is what you pass
to functions like `Editor.placeBlock` and what functions like
`Editor.getBlock` return.



### Toolbox modules

There are several modules of utility functions that work on top of the core
interface.

- minecraft_tools
- editor_tools
- geometry
- lookup
- model


### Internal utilities

- utils
- nbt_tools
- block_state_tools
- interface



## Typical usage patterns

Most GDPC programs revolve around an {class}`Editor` object, which serves as the
primary point of communication between GDPC and the GDMC HTTP mod.

## python client scripts for the Minecraft HTTP Interface Mod

This a collection of scripts for demonstrating the [Minecraft HTTP Interface Mod](https://github.com/nilsgawlik/gdmc_http_interface) build for the GDMC competition.

Requirements are in requirements.txt. Feel free to use different versions, the versions are just what is installed on my machine.

You need to have Minecraft running, the mod installed and a world open for this to work!

Scripts:

**frameworkTest**: This is an example of loading a bunch of chunks and displaying a bunch of heightmaps

**simpleAgentTest**: This is an example purely build on the command interface. It doesn't requite matplotlib or numpy or OpenCV to be installed. You need to put sensible coordinates into the startPos variable and it'll build a bunch of tree roots.

### License

License is MIT, except for the bitarray class which is ported from the Minecraft source, so copyright might be in a gray area for now.
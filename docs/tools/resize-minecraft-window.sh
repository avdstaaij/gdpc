#!/bin/bash

# Resizes the Minecraft window to 1376x688, for the purposes of taking
# screenshots for the documentation.
#
# The base width of a full-width image on a page using Sphinx-immaterial is 688 px.
# This may be increased by 10% or 20% depending on the size of the browser screen.
# 1376 px is 2x the default width of 688, which seems like a good size to use for full-width images.
# We match the name "- Singleplayer" because "Minecraft" also matches the launcher.

wmctrl -r "- Singleplayer" -e 0,0,0,1376,688

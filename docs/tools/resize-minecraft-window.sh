#!/bin/bash

# Usage: resize-minecraft-window.sh [<width>] (default 1376)
# Resizes the Minecraft window to <width>x688, for the purposes of taking
# screenshots for the documentation.

# The base width of a full-width image on a page using Sphinx-immaterial is 688 px.
# This may be increased by 10% or 20% depending on the size of the browser screen.
# 1376 px is 2x the default width of 688, which seems like a good size to use for full-width images.


set -e # Quit on error
CMD="$(basename "$0")"


if [[ $# -gt 1 ]]; then
	echo "Usage: $CMD [<width>]"
	exit 1
fi

if [[ $# -eq 1 ]]; then
	if [[ $1 =~ ^[0-9]+$ ]]; then
		width="$1"
	else
		echo "Usage: $CMD [<width>]"
		exit 1
	fi
else
	width=1376
fi


# We match the name "- Singleplayer" because "Minecraft" also matches the launcher.
wmctrl -r "- Singleplayer" -e 0,0,0,${width},688

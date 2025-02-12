# Release guide

This guide describes how to release a new version of GDPC. It's only relevant for the maintainer, but it's good to have this written down in case maintenance is ever passed on to someone else.

Steps to make a release:

- Create a release commit.
	- In `__init__.py`, update `__version__` to the new version number.
	- Change the "In development" header in the changelog to the new version number, and add a new "In development" section with only the compatibility line.
	- If necessary, update the compatible GDMC-HTTP and Minecraft versions listed on the installation page of the docs.
	- If necessary, update the minimum Python version listed on the installation page of the docs.
	- Commit the changes above with the title "Updated version to X.X.X".
	- Push changes to GitHub (things will be public from here).

- Create a new GitHub release.
	- Set tag to "vX.X.X" (notice the "v"). This should be a new tag.
	- Set title to "X.X.X" (no "v").
	- Set the body text to the changelog section for this version (without the header).

- Publish to PyPI.
	- Remove `/dist` (probably not necessary, but seems safer).
	- Install requirements: `python3 -m pip install --upgrade build twine`
	- Run `python3 -m build`
	- Run `python3 -m twine upload dist/*`

- Update `latest_release` branch to the "Updated version to X.X.X" commit.
- (Optional) Make a post in #frameworks on Discord.

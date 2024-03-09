# How to contribute to GDPC

## Reporting bugs

First, check if your bug has already been reported in the [issues](https://github.com/avdstaaij/gdpc/issues).

If it's not there, [open a new issue](https://github.com/avdstaaij/gdpc/issues/new/choose). Please describe the bug in as much detail as possible.


## Contributing code

To propose code changes, please create a GitHub pull request.
After you've opened a pull request, we'll review it (and may request some changes). If everything looks good, we'll merge it into the main repository!

If you're new to GitHub pull requests, here's a very basic guide:
1. Fork this repository using the fork button at the top right of the webpage. This will create a public copy of the repository in your own GitHub account.
2. Create a new feature branch from `master` in your fork.
3. Commit your code on the feature branch.
4. Open a pull request for your feature branch. If you've recently committed code to it, there should be a button for this in the main GDPC repository. You can also use the *Contribute -> Open pull request* button in your fork.

To test your additions, you may want to run code that imports from `gdpc` (like the examples). To make `gdpc` "point" to your local version (instead of the latest published version), you can install your local version in *editable mode*: `pip install -e .`. Note that this will replace the version of `gdpc` in your current environment, so it is recommended to use some kind of virtual environment when doing this. Using `pip install -r requirements-dev` will install fixed versions of all dependencies, install gdpc in editable mode, and install some additional packages that are only needed for development.


## Discussion

You can chat with the developers of GDPC (and other GDMC-related frameworks) in the [#frameworks](https://discord.gg/43eTuUNx5U) channel of the [GDMC Discord](https://discord.gg/YwpPCRQWND)!

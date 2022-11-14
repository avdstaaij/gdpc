import os
from setuptools import setup


SCRIPT_DIR         = os.path.abspath(os.path.dirname(__file__))
METADATA_FILE_PATH = os.path.join(SCRIPT_DIR, "gdpc/__init__.py")


# Based on https://github.com/pypa/pip/blob/9aa422da16e11b8e56d3597f34551f983ba9fbfd/setup.py
def get_metadata(name: str) -> str:
    with open(METADATA_FILE_PATH) as file:
        contents = file.read()
    for line in contents.splitlines():
        dunderString = f"__{name}__"
        if line.startswith(f"{dunderString}"):
            # __{name}__ = "{value}"
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError(f"Unable to find {dunderString} value.")


with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()


setup(
    name="gdpc",
    version=get_metadata("version"),
    description=(
        "The Generative Design Python Client is a Python-based "
        "interface for the Minecraft HTTP Interface mod.\n"
        "It was created for use in the "
        "Generative Design in Minecraft Competition."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/avdstaaij/gdpc",
    author=get_metadata("author"),
    author_email="blinkenlights@pm.me",
    maintainer="Arthur van der Staaij",
    maintainer_email="arthurvanderstaaij@gmail.com",
    license="MIT",
    packages=["gdpc"], # Note: subpackages must be listed explicitly
    install_requires=[
        "matplotlib",
        "NBT",
        "numpy",
        "opencv_python",
        "requests"
    ],
    python_requires=">=3.6, <4",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Version Control :: Git"
    ],
    keywords="GDMC, generative design, Minecraft, HTTP, development",
    project_urls={
        "Bug Reports": "https://github.com/avdstaaij/gdpc/issues",
        "Official Competition": "https://gendesignmc.engineering.nyu.edu",
        "Chat about it on Discord": "https://discord.gg/V9MW65bD",
        "Source": "https://github.com/avdstaaij/gdpc",
    },
    zip_safe=False
)

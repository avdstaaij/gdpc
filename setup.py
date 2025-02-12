import os
from setuptools import setup


SCRIPT_DIR         = os.path.abspath(os.path.dirname(__file__))
METADATA_FILE_PATH = os.path.join(SCRIPT_DIR, "src/gdpc/__init__.py")


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
    name                          = get_metadata("title"),
    version                       = get_metadata("version"),
    description                   = get_metadata("description"),
    long_description              = long_description,
    long_description_content_type = "text/markdown",
    url                           = get_metadata("url"),
    author                        = get_metadata("author"),
    author_email                  = get_metadata("author_email"),
    maintainer                    = get_metadata("maintainer"),
    maintainer_email              = get_metadata("maintainer_email"),
    license                       = get_metadata("license"),
    packages = ["gdpc"], # Note: subpackages must be listed explicitly
    package_dir={"": "src"},
    install_requires=[
        "Deprecated",
        "matplotlib",
        "more-itertools",
        "NBT",
        "numpy",
        "opencv_python",
        "PyGLM >= 2.7.0",
        "pyglm-typing",
        "requests",
        "scikit-image >= 0.19.0",
        "scipy",
        "termcolor",
        "typing_extensions"
    ],
    python_requires=">=3.7, <4",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    keywords="GDMC, generative design, Minecraft, HTTP, development",
    project_urls={
        "Documentation":                "https://gdpc.readthedocs.io",
        "Bug Reports":                  "https://github.com/avdstaaij/gdpc/issues",
        "Changelog":                    "https://github.com/avdstaaij/gdpc/blob/master/CHANGELOG.md",
        # "Official Competition Website": "https://gendesignmc.engineering.nyu.edu",
        "Official Competition wiki":    "https://gendesignmc.wikidot.com/start",
        "Chat about it on Discord":     "https://discord.gg/YwpPCRQWND",
        "Source":                       "https://github.com/avdstaaij/gdpc",
    },
    zip_safe=False
)

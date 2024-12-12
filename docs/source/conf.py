# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import os
import shutil
import re

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# Problems with imports? Could try `export PYTHONPATH=$PYTHONPATH:`pwd`` from root project dir...

# import os
# import sys
# sys.path.insert(0, os.path.abspath(f"{__file__}/../../.."))  # Source code dir relative to this file


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'GDPC'
copyright = '2024, avdstaaij'
author = 'avdstaaij'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    # "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "myst_parser",
]

templates_path = ['_templates']
exclude_patterns = []

rst_prolog = """
.. role:: python(code)
   :language: python
"""

intersphinx_mapping = {
    "python":   ("https://docs.python.org/3", None),
    "numpy":    ("https://numpy.org/doc/stable/", None),
    "scipy":    ("https://docs.scipy.org/doc/scipy/", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
}

myst_enable_extensions = [
    "amsmath",
    "deflist",
    "smartquotes",
    "attrs_block",
    "attrs_inline",
]


# -- Autodoc -------------------------------------------------------------------

add_module_names = False
autodoc_class_signature = "separated"
autodoc_member_order = "bysource"
autodoc_type_aliases = {"TransformLike": "TransformLike"}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

extensions += ["sphinx_immaterial", "sphinx_immaterial.kbd_keys"]
html_theme = "sphinx_immaterial"
html_theme_options = {
    "icon": {
        "repo": "fontawesome/brands/github",
        "edit": "material/file-edit-outline",
    },
    "site_url": "https://jbms.github.io/sphinx-immaterial/",
    "repo_url": "https://github.com/avdstaaij/gdpc",
    "repo_name": "gdpc",
    "edit_uri": "blob/master/docs/source",
    "globaltoc_collapse": False,
    "features": [
        # "header.autohide",
        # "navigation.expand",
        # "navigation.tabs",
        # "toc.integrate",
        # "navigation.sections",
        # "navigation.instant",
        # "header.autohide",
        # "navigation.top",
        "navigation.tracking",
        # "search.highlight",
        # "search.share",
        "toc.follow",
        # "toc.sticky",
        "content.tabs.link",
        "announce.dismiss",
    ],
    "palette": [
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "blue",
            "accent": "light-green",
            "toggle": {
                "icon": "material/weather-sunny",
                "name": "Switch to light mode",
            },
        },
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "blue",
            "accent": "green",
            "toggle": {
                "icon": "material/weather-night",
                "name": "Switch to dark mode",
            },
        }
    ],
    # "version_dropdown": True,
    # "version_info": [
    #     {
    #         "version": "https://sphinx-immaterial.rtfd.io",
    #         "title": "ReadTheDocs",
    #         "aliases": [],
    #     },
    #     {
    #         "version": "https://jbms.github.io/sphinx-immaterial",
    #         "title": "Github Pages",
    #         "aliases": [],
    #     },
    # ],
    "toc_title_is_page_title": True,
    # Social icons
    "social": [
        {
            "icon": "fontawesome/brands/github",
            "link": "https://github.com/avdstaaij/gdpc",
            "name": "Source on github.com",
        },
        {
            "icon": "fontawesome/brands/python",
            "link": "https://pypi.org/project/gdpc/",
            "name": "GDPC on PyPI",
        },
        {
            "icon": "fontawesome/brands/discord",
            "link": "https://discord.gg/YwpPCRQWND",
            "name": "GDMC Discord server",
        },
    ],
}
html_static_path = ["_static"]
html_css_files = ["styles.css"]


# -- API Reference -----------------------------------------------------------

def generate_reference():
    shutil.rmtree(f"{SCRIPT_DIR}/api/", ignore_errors=True)
    os.makedirs(f"{SCRIPT_DIR}/api/", exist_ok=True)

    # TODO: adjust this if we add subpackages

    target_names = []
    for filename in sorted(os.listdir(f"{SCRIPT_DIR}/../../src/gdpc")):
        if filename == "__pycache__":
            continue

        source_name = filename.split(".")[0]
        target_name = "gdpc" if source_name == "__init__" else f"gdpc.{source_name}"
        target_names.append(target_name)

    content = (
        "API Reference\n" +
        "=============\n" +
        "This part of the documentation details every public object of GDPC.\n" +
        "\n" +
        ".. rubric:: Modules\n" +
        "\n" +
        ".. autosummary::\n" +
        "   :toctree: .\n" +
        "   :template: autosummary/module-template.rst\n" +
        "\n" +
        "\n".join(f"   {name}" for name in target_names) + "\n"
    )

    with open(f"{SCRIPT_DIR}/api/index.rst", "w") as file:
        file.write(content)

generate_reference()


# -- Changelog ---------------------------------------------------------------

# Function 1: separate pages
# Function 2: single page with downgraded headers

# def generate_changelog():
#     with open(f"{SCRIPT_DIR}/../../CHANGELOG.md", "r") as file:
#         changelog = file.read()

#     changelog_sections = re.split("^(# .*)$", changelog, flags=re.MULTILINE)

#     shutil.rmtree(f"{SCRIPT_DIR}/changelog/", ignore_errors=True)
#     os.makedirs(f"{SCRIPT_DIR}/changelog/", exist_ok=True)

#     headers = []
#     for i in range(1, len(changelog_sections), 2):
#         header = changelog_sections[i][2:].strip().replace(" ", "-").lower()

#         # It's no use to include this, since the documentation will only
#         # update on a version release, in which case this section is always
#         # empty.
#         if header == "in-development":
#             continue

#         headers.append(header)
#         with open(f"{SCRIPT_DIR}/changelog/{header}.md", "w") as file:
#             file.write(changelog_sections[i] + changelog_sections[i+1])

#     index = (
#         "# Changelog\n" +
#         "\n" +
#         "```{toctree}\n" +
#         ":maxdepth: 1\n" +
#         "\n" +
#         "\n".join(f"{header}.md" for header in headers) + "\n" +
#         "```\n"
#     )

#     with open(f"{SCRIPT_DIR}/changelog/index.md", "w") as file:
#         file.write(index)

def generate_changelog():
    with open(f"{SCRIPT_DIR}/../../CHANGELOG.md", "r") as file:
        changelog = file.read()

    # Cut off "In Development" section
    # It's no use to include it, since the documentation will only
    # update on a version release, in which case the section is always
    # empty.
    lines = changelog.splitlines()
    for i, line in enumerate(lines[1:]):
        if line.startswith("# "):
            break
    changelog = "\n".join(lines[i+1:])

    # "Downgrade" all headings by one level
    changelog = (
        "# Changelog\n" +
        "\n" +
        re.sub("^#", "##", changelog, flags=re.MULTILINE)
    )

    shutil.rmtree(f"{SCRIPT_DIR}/changelog/", ignore_errors=True)
    os.makedirs(f"{SCRIPT_DIR}/changelog/", exist_ok=True)

    with open(f"{SCRIPT_DIR}/changelog/index.md", "w") as file:
        file.write(changelog)

generate_changelog()

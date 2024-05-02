# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


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
    "sphinx.ext.autosummary",
    "myst_parser",
]

templates_path = ['_templates']
exclude_patterns = []


# -- Autodoc -------------------------------------------------------------------

add_module_names = False
autodoc_class_signature = "separated"
autodoc_member_order = "bysource"
autodoc_type_aliases = {"TransformLike": "TransformLike"}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ['_static']
html_css_files = ["styles.css"]

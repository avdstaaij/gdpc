# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from shutil import rmtree
import os

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# Problems with imports? Could try `export PYTHONPATH=$PYTHONPATH:`pwd`` from root project dir...
# import os
# import sys
# sys.path.insert(0, os.path.abspath(f"{__file__}/../../.."))  # Source code dir relative to this file
# print(sys.path)

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
]

templates_path = ['_templates']
exclude_patterns = []




# Custom:
autosummary_generate = True # TODO: is this the default?

#rmtree(f"{SCRIPT_DIR}/generated", ignore_errors=True)

autodoc_member_order = "bysource"




# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
#html_static_path = ['_static']

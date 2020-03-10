# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Path setup --------------------------------------------------------------

import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.append(os.path.abspath(".."))

source_suffix = ".rst"

# -- Project information -----------------------------------------------------

project = "BidFX API Python"
copyright = "2020, BidFX Systems Ltd"
author = "BidFX Systems Ltd"

from bidfx import __version__ as version

release = version

# -- General configuration ---------------------------------------------------

# Sphinx extensions.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
]

# Cross-references to online lib docs.
intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}
exclude_patterns = ["build"]

# HTML -----------------------------------------------------------------

master_doc = "index"
html_theme = "bizstyle"
html_style = "bidfxstyle.css"

html_static_path = ["_static"]
html_favicon = "_static/favicon32.png"
html_logo = "_static/bidfx_logo_128.png"
html_title = "{} ({})".format(project, version)
html_show_sourcelink = False
html_show_sphinx = False

default_role = "any"
autodoc_member_order = "bysource"
autoclass_content = "both"


# PDF -----------------------------------------------------------------

latex_logo = "_static/bidfx_logo_128.png"

# latex_elements = {
#     "papersize": "a4paper",
#     "pointsize": "12pt",
#     "preamble": "",
#     "figure_align": "htbp",
# }
# latex_paper_size = "a4paper"
# latex_documents = [
#     (
#         "index",
#         u"bidfx-public-api-python.pdf",
#         u"BidFX Public API for Python",
#         u"Paul Sweeny",
#         u"manual",
#     ),
# ]

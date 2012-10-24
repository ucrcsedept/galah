# -*- coding: utf-8 -*-
#
# Galah documentation build configuration file, created by
# sphinx-quickstart on Sun Oct 14 01:32:18 2012. Since modified (see git log)
#
# This file is execfile()d with the current directory set to its containing dir.

import sys, os

sys.path.insert(0, os.path.abspath('../../../'))

# -- General configuration -----------------------------------------------------

extensions = ['sphinx.ext.autodoc']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Galah'
copyright = u'2012, John Sullivan'

# The version info for the project you're documenting.
version = release = '0.2'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'galah.api.commands', u'Galah\'s API Documentation',
     [u'John Sullivan'], 1)
]

# -- Autodoc signal handlers ---------------------------------------------------

# Will skip all documentable objects that aren't exposed API functions
def should_skip(app, what, name, obj, skip, options):
	from types import FunctionType

	return name.startswith("_") or type(obj) is not FunctionType

def setup(app):
	app.connect('autodoc-skip-member', should_skip)
# -*- coding: utf-8 -*-
#
# Galah documentation build configuration file, created by
# sphinx-quickstart on Sun Oct 14 01:32:18 2012. Since modified (see git log)
#
# This file is execfile()d with the current directory set to its containing dir.

import sys, os

# -- General configuration -----------------------------------------------------

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

# -- Options for html output ---------------------------------------------------

html_static_path = ["./html_static/"]

html_style = "galah.css"

# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
def get_man_pages(root_dir):
	from os import listdir
	from os.path import isfile, join, splitext

	pages = []
	for i in listdir(root_dir):
		file_path = join(root_dir, i)
		file_name = splitext(i)[0]

		if not isfile(file_path):
			continue

		pages.append((
			join(root_dir, file_name), 
			file_name,
			u"Galah API: %s documentation" % file_name,
			[u"John Sullivan"],
			1
		))

	return pages


man_pages = get_man_pages("commands")

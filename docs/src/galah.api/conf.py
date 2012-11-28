# -*- coding: utf-8 -*-

# Copyright 2012 John Sullivan
# Copyright 2012 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

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

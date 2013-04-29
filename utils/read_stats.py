#!/usr/bin/env python

# Copyright 2012-2013 Galah Group LLC
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# You can redistribute Galah and/or modify it under the terms of
# the Galah Group General Public License as published by
# Galah Group LLC, either version 1 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Galah Group General Public License for more details.
#
# You should have received a copy of the Galah Group General Public License
# along with Galah.  If not, see <http://www.galahgroup.com/licenses>.

import os
import os.path
import sys

def resolve_path(path):
	"Resolves a user provided path in a sane way."

	return os.path.abspath(os.path.expanduser(path))

def parse_arguments(args = sys.argv[1:]):
    from optparse import OptionParser, make_option

    option_list = [
       	make_option(
        	"-v", "--verbose", dest = "verbose", action = "store_true",
        	default = False,
        	help = "If present, lots of stuff will be printed."
       	),
       	make_option(
       		"-p", "--prefix", dest = "prefix", action = "store",
       		type = "string", default = "cprof",
       		help = "When a directory is given as the first positional "
       		       "argument that directory will be searched for files with "
       		       "this prefix, and those files will be considered the source "
       		       "files (default: %default)."
       	),
       	make_option(
       		"-s", "--sort", dest = "sort", action = "store", type = "string",
       		default = "cumulative",
       		help = "Sorts the output on the given column. See the Python "
       		       "documentation for pstats.Stats.sort_stats() for available "
       		       "values (default: %default)."
       	)
    ]

    parser = OptionParser(
        usage = "usage: %prog [options] [DIRECTORY OR FILE(S)]",
        description = "Tool for parsing cProfile stat files.",
        option_list = option_list
    )

    options, args = parser.parse_args(args)

    args = [resolve_path(i) for i in args]

    if len(args) < 1:
        parser.error("At least one argument must be supplied.")

    return (options, args)

def main():
	options, args = parse_arguments()

	if len(args) == 1 and os.path.isdir(args[0]):
		source_files = [os.path.join(args[0], i) for i in os.listdir(args[0])
			if i.startswith(options.prefix)]
	else:
		source_files = args

	# Ignore empty files
	source_files = [i for i in source_files if os.path.getsize(i) > 0]

	if not source_files:
		print >> sys.stderr, "No source files. Aborting."
		exit(1)

	import pstats
	stats = pstats.Stats(*source_files)
	stats.sort_stats(*options.sort.split(","))

	stats.print_stats()

if __name__ == "__main__":
	main()

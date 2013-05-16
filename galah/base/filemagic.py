# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributors as noted in the CONTRIBUTORS file
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

import tempfile
import os
import subprocess

TAR_PATH = "/bin/tar"
UNZIP_PATH = "/usr/bin/unzip"

def _uncompress_targz(compressed_filepath, dest_dir):
	subprocess.check_call(
		[TAR_PATH, "--extract", "--gzip", "--file", compressed_filepath],
		cwd = dest_dir
	)

def _uncompress_tar(compressed_filepath, dest_dir):
	subprocess.check_call(
		[TAR_PATH, "--extract", "--file", compressed_filepath],
		cwd = dest_dir
	)

def _uncompress_zip(compressed_filepath, dest_dir):
	subprocess.check_call([UNZIP_PATH, compressed_filepath], cwd = dest_dir)

def uncompress(compressed_file, dest_dir = None):
	"""
	Uncompresses a werkzeug.FileStorage object that represents some uploaded
	archive.

	The contents of the directory will be placed into dest_dir (which is assumed
	to already exist).

	"""

	routing_pairs = (
		(".tar.gz", _uncompress_targz),
		(".tgz", _uncompress_targz),
		(".tar", _uncompress_tar),
		(".zip", _uncompress_zip)
	)

	found_handler = None
	for suffix, handler in routing_pairs:
		if compressed_file.filename.endswith(suffix):
			found_handler = handler
			break
	else:
		raise ValueError("Compressed file does not have known format.")

	# If we didn't get a directory to place the uncompressed files into, create
	# a temporary one.
	if dest_dir is None:
		dest_dir = tempfile.mkdtemp()

	tempfile_handle, tempfile_path = tempfile.mkstemp()
	os.close(tempfile_handle)

	try:
		compressed_file.save(tempfile_path)

		found_handler(tempfile_path, dest_dir)
	finally:
		os.remove(tempfile_path)

	return dest_dir
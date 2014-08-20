import tempfile
import zipfile
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

# Adapted from http://stackoverflow.com/a/1855118: How to Zip a Directory
def zipdir(path, archive_file):
	os.remove(archive_file)

	which_files = []
	os.chdir(path)
	dirname, subdirs, files = os.walk('.').next()
	which_files = subdirs + files

	subprocess.check_call(
		[
			"zip", "-r", archive_file, "-q"
		] + which_files
	)

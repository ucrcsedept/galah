import os, config

def id_to_path(id):
    return os.path.join(config.options.data_directory, str(id))
    
def id_to_checksum(id):
    "Retrieves the checksum of the file associated with the given id"
    
    return open(id_to_path(id) + ".checksum", "rb").read()

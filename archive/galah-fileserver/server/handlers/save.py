import json, hashlib

def handle_save(socket, addresses, request):
    try:
        # Determine where we will save the file
        path = id_to_path(request["id"])
        
        # Open the file for writing
        save_to = open(path, "wb")
        
        while True:
            header, chunk = socket.recv_multipart()
            
            header = json.loads(header)
            
            if header["start"] == header["end"]:
                checksum = chunk
                break
            
            save_to.seek(header["start"])
            save_to.write(chunk)
            
            assert save_to.tell() == header["end"]

        hash = hashlib.md5()
        save_to.seek(0)
        while True:
            block = save_to.read(256)
            
            if not block:
                break
            
            hash.update(block)
        
        if hash.hexdigest() != checksum.strip():
            raise RuntimeError("Checksums do not match")
            
        checksum_file = open(id_to_checksum(request["id"]), "wb")
        checksum_file.write(hash.digest())
        
        return save_to
    except:
        raise

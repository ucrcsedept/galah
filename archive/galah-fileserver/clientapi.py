import zmq, tempfile, json, hashlib

def get_file(file_id, address, context = None, port = 4545, chunk_hint = None,
             save_to = None, check_hash = True):
    
    # Create a new context if one isn't provided
    if context is None:
        context = zmq.Context()
        
    # Create a temporary file we'll save into if none was provided
    if save_to is None:
        save_to = tempfile.TemporaryFile()
    
    # Craft the request
    request = {
        "action": "retrieve",
        "id": str(file_id)
    }
    
    if chunk_hint:
        request["chunk_hint"] = chunk_hint
        
    socket = context.socket(zmq.DEALER)
    socket.connect("tcp://%s:%s" % (address, str(port)))
    
    socket.send_json(request)
        
    while True:
        header, chunk = socket.recv_multipart()
        
        header = json.loads(header)
        
        if "error" in header:
            raise RuntimeError(header["code"] + ": " + chunk)
        
        if header["start"] == header["end"]:
            checksum = chunk
            break
        
        assert str(header["id"]) == str(file_id)
        
        save_to.seek(header["start"])
        save_to.write(chunk)
        
        assert save_to.tell() == header["end"]

    if check_hash:
        hash = hashlib.md5()
        save_to.seek(0)
        while True:
            block = save_to.read(256)
            
            if not block:
                break
            
            hash.update(block)
        
        if hash.hexdigest() != checksum.strip():
            raise RuntimeError("Checksums do not match")
    
    return save_to
    
get_file("1", "localhost", chunk_hint = 100)

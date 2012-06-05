import json, config
from helpers.ids import *
from helpers.error import ServerError
import helpers.misc as misc

def handle_retrieve(socket, addresses, request):
    try:
        # Determine the location of the requested file
        path = id_to_path(request["id"])
        
        # Will contain meta-data about the reply, sent as JSON in a seperate
        # part of the message from the binary data
        header = {
            "id": request["id"],
            "start": -1,
            "end": -1
        }
        
        # Open the file for reading
        try:
            file = open(path, "rb")
        except IOError:
            raise ServerError("not_found",
                              "File with id %s was not found" % request["id"])
        
        # Determine the optimal chunk size
        chunk_size = request.get("chunk_hint", config.options.chunk_size)
        chunk_size = misc.clamp(
            chunk_size,
            config.options.min_chunk_size,
            config.options.max_chunk_size
        )
        
        more = True
        while more:
            # Grab data from the file and mark where we started and stopped
            header["start"] = file.tell()
            chunk = file.read(chunk_size)
            header["end"] = file.tell()
            
            print "sending chunk: ", header["start"], "-", header["end"]
            
            # Check if we've reached the end of the file
            if header["start"] == header["end"]:
                # The last chunk is the checksum
                chunk = id_to_checksum(request["id"])
                
                more = False
            
            socket.send_multipart(addresses + [json.dumps(header), chunk])
    except:
        raise

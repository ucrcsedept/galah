### NOTE #######################################################################
# This is a prototype/proof of concept. While speed is kept in mind, it is not
# held as a priority primarily because this should not be written in python in
# the first place if speed is a priority...
#
# This server should not be written as python. It should be written in C++ to
# have fine-grained control over memory. The mapping from ObjectId to file-path
# should be done via a hash table, or alternatively via a B Tree stored on the
# file system if memory is tight (a hybrid of the two would be even better).
# The server should be highly capable of serving multiple requests at once (the
# number of parallel requests capable of being served should be the same as the
# number of reads & writes the file system can do in parrellel.. RAID).
################################################################################

import zmq, os, hashlib, json, helpers, config

from handlers import *

options = None

def parse_arguments():
    from optparse import OptionParser, make_option

    # Craete the list of command line options
    option_list = [
        make_option("-d", "--data", dest = "data_directory", type = str,
                    help = "The directory the files will be stored in."),
        make_option("--chunk-size", dest = "chunk_size", type = int,
                    default = 1024,
                    help = "The default size in bytes of each chunk of the "
                           "file that is sent. If the request specifies a "
                           "chunk_hint this value will be ignored."),
        make_option("--max-chunk-size", dest = "max_chunk_size", type = int,
                    default = 2048,
                    help = "The maximum size a chunk may be. If the request "
                           "specifies a chunk_hint larger than this value this "
                           "value will be used instead."),
        make_option("--min-chunk-size", dest = "min_chunk_size", type = int,
                    default = 256,
                    help = "The 'minimum' size a chunk may be. If the request "
                           "specifies a chunk_hint smaller than this value, "
                           "this value will be used instead.")
    ]

    parser = OptionParser(
        description = "Acts as a simple file server",
        option_list = option_list
    )
    
    options = parser.parse_args()[0]
    
    if not options.data_directory:
        parser.error("--data is not an optional argument")
        
    return options

def main():
    # ZMQ needs a monolithic context
    context = zmq.Context()
    
    # Open up a router socket (prepends addressing information)
    socket = context.socket(zmq.ROUTER)
    socket.bind("tcp://*:4545")

    # Start the server loop
    while True:
        # Listen for a request for a file (note the router socket adds
        # addressing data and the payload may have multiple such addressing
        # parts, the request is guarenteed to be at the end of the payload
        # however)
        addresses = socket.recv_multipart()
        request = json.loads(addresses.pop())
        
        try:
            handle_request(socket, addresses, request)
        except ServerError as e:
            helpers.error.send_error(socket, addresses, e)

if __name__ == "__main__":
    config.options = parse_arguments()
    
    main()

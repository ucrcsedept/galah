import json

class ServerError(Exception):
    def __init__(self, code, message):
        self.code = str(code)
        self.message = str(message)
        
        Exception.__init__(self, code, message)
    
    def __str__(self):
        return "%s: %s" % (self.code, self.message)

def send_error(socket, addresses, error):
    header = json.dumps({
        "error": 1,
        "code": error.code
    })
    
    socket.send_multipart(addresses + [header, error.message])

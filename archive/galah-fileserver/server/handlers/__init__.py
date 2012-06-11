import retrieve, save

from helpers.error import ServerError

def handle_request(socket, addresses, request):
    if "action" not in request:
        raise ServerError("bad_request", "action field is required")
    
    # Instead of a list of if statements to map from action to function this
    # seemed more appropriate
    function_map = {
        "retrieve": retrieve.handle_retrieve,
        "save": save.handle_save
    }
    
    # Find the function that knows how to handle this action
    func = function_map.get(request["action"])
    
    if not func:
        raise ServerError("bad_request",
                          "unrecognized action %s" % request["action"])

    # Pass the buck
    return func(socket, addresses, request)

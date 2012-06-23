# This module should hopefully remain **small**. Use other libraries and such
# if you can. There shouldn't be that much shared code among the different
# views.

from werkzeug.exceptions import NotFound, HTTPException
from flask import request
def is_url_on_site(app, url):
    """
    Determines if *app* can handle *url*, if this function returns False it
    means url points to a resource off-site.
    
    """
    
    try:
        # Will raise an exception if no endpoint exists for the url
        app.create_url_adapter(request).match(url)
    except NotFound:
        return False
    except HTTPException:
        # Any other exceptions are harmless (I think)
        pass
        
    return True

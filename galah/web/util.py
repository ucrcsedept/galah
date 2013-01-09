# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributers as noted in the CONTRIBUTERS file
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

from galah.base.pretty import pretty_time_distance
import datetime
def create_time_element(timestamp, now = None):
    if now is None:
        now = datetime.datetime.today()

    return '<time datetime"%s" title="%s">%s</time>' % (
        timestamp.strftime("%Y-%m%dT%H:%M:%S"),
        timestamp.strftime("%B %d, %Y at %I:%M:%S %p"),
        pretty_time_distance(now, timestamp)
    )

import logging
from flask.ext.login import current_user
from flask import request
class GalahWebAdapter(logging.LoggerAdapter):
    def __init__(self, logger):
        logging.LoggerAdapter.__init__(self, logger, {})

    def process(self, msg, kwargs):
        prefix = "(user=%s;ip=%s;path=%s) " % (
            current_user.email,
            request.remote_addr,
            request.path
        )

        return (prefix + msg, kwargs)
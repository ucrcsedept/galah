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

# The actual view
from galah.web import app
from flask import render_template, url_for
from collections import namedtuple
from werkzeug.exceptions import InternalServerError, NotFound

AsciiPiece = namedtuple("AsciiPiece", ["author", "art"])
ascii_art = {
    500: AsciiPiece(
        author = "pb", 
        art = """     __     __------           
  __/o `\ ,~   _~~  . ..   . ..
 ~ -.   ,'   _~-----           
     `\     ~~~--_'__          
       `~-==-~~~~~---          """        
    ),
    404: AsciiPiece(
        author = "Stephen Morgana",
        art = """             /\\              
              .\\\..          
              \\   \\         
              \ (o) /         
              (/    \         
               /\    \        
              ///     \       
             ///|     |       
            ////|     |       
           //////    /        
           |////    /         
          /|////--V/          
         //\//|   |           
     ___////__\___\__________ 
    ()_________'___'_________)"""
    )
}

messages = {
    500: """It appears something broke, I'm going to go fix it... In the meantime <a href="%s">Try Here</a>.""",
    404: """You seem to have landed in the wrong place... <a href="%s">Try Here</a>."""
}

from galah.web.util import GalahWebAdapter
import logging
logger = GalahWebAdapter(logging.getLogger("galah.web.views.error"))

@app.errorhandler(404)
@app.errorhandler(500)
def error(e):
    # Log the error if it's not a 404 or purposeful abort(500).
    if type(e) is not InternalServerError and type(e) is not NotFound:
        logger.exception("An error occurred while rendering a view.")

    code = e.code if hasattr(e, "code") else 500
    
    if code == 500:
        error_description = "500: Internal Server Error"
    else:
        error_description = str(e)
    
    return render_template(
        "error.html",
        error_description = error_description,
        message = messages[code] % "/home", 
        art_piece = ascii_art[code]
    ), code

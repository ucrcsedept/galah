"""
This module provides a similar interface to the standard library's ``json``.

This module should be used instead of the standard library module throughout
Galah. Reasons for this are

 * When serializing JSON data we typically want to be space efficient rather
   then having it look pretty. This module performs such optimizations
   automatically and consistently.
 * Whenever creating data to be shipped to another process (which is typically
   what JSON is used for) encoding needs to always be considered. This module
   handles encoding consistently by always outputting and expecting UTF-8
   encoded text.
 * The ``json`` module is not available in Python 2.5 so having this module
   serve as a proxy will let us smoothly handle that case.

"""

# stdlib
import json as _json
import codecs

def dumps(obj):
    """
    Serializes an object into a JSON string.

    :param obj: A dictionary-like object.

    :returns: A UTF-8 encoded ``str`` object.

    """

    # If the result is all ASCII this will be a str, but if the result contains
    # non-ASCII characters a unicode object will be returned.
    unencoded = _json.dumps(obj, separators = (",", ":"), ensure_ascii = False)

    # This will always give us a str object
    return codecs.encode(unencoded, "utf_8")

def loads(raw):
    """
    Deserialize a UTF-8 encoded string containing JSON data.

    :param raw: The string to deserialize. Can be a ``unicode`` object or UTF-8
        encoded ``str``.

    :returns: A Python dictionary.

    """

    # The standard JSON library's loads handles UTF-8 encoded data just fine
    return _json.loads(raw)

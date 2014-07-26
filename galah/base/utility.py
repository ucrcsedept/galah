# Copyright (c) 2012-2014 John Sullivan
# Copyright (c) 2012-2014 Chris Manghane
# Licensed under the MIT License <http://opensource.org/licenses/MIT>

def tuplify(target):
    "Transforms a single item into a tuple if it is not already a tuple."

    if type(target) is not tuple:
        return (target, )
    else:
        return target

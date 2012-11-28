..
    Copyright 2012 John Sullivan
    Copyright 2012 Other contributers as noted in the CONTRIBUTERS file

    This file is part of Galah.

    Galah is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Galah is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with Galah.  If not, see <http://www.gnu.org/licenses/>.

find_class
==========

Finds a classes or classes that match the given query and displays
information on them. Instructor will default to the current user, meaning
by default only classes you are teaching will be displayed (this is not the
case for admins).

Reference
---------

.. function:: find_class([name_contains = '', enrollee = '']):
    
    :param name_contains: A part of (or the whole) name of the class. Case
                          insensitive.

    :param enrollee: Someone enrolled in the class. Defaults to the current
                     user (unless you are an admin). "any" may be specified
                     to search all classes.

Example Usage
-------------

When you call :func:`find_class` without parameters, all classes you are
enrolled in/teaching are listed (unless you are an admin).

>>> find_class
find_class
--Acting as user teacher@ucr.edu--
You are teaching 1 class(es) with '' in their name.
	Class [id = 5090634855c448134f67b3e3, name = CS 9000]

If we would like to find all classes, you can specify **any** for enrollee.

>>> find_class "" any
--Acting as user teacher@ucr.edu--
Anyone is teaching 3 class(es) with '' in their name.
	Class [id = 5090634855c448134f67b3e3, name = CS 9000]
	Class [id = 509066e855c448134f67b3e4, name = CS 10]
	Class [id = 5090671655c448134f67b3e5, name = Woodshop 101]

Finally, we can find all CS classes Galah knows about.

>>> find_class CS any
--Acting as user teacher@ucr.edu--
Anyone is teaching 2 class(es) with 'CS' in their name.
	Class [id = 5090634855c448134f67b3e3, name = CS 9000]
	Class [id = 509066e855c448134f67b3e4, name = CS 10]

Permissions
-----------

**admin** and **teacher** users can use this command.
find_class
==========

Finds a classes or classes that match the given query and displays
information on them. Instructor will default to the current user, meaning
by default only classes you are teaching will be displayed (this is not the
case for admins).

Reference
---------

.. function:: find_class([name_contains = "", enrollee = ""])
    
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
--Logged in as teacher@ucr.edu--
You are teaching 1 class(es) with '' in their name.
	Class [id = 5090634855c448134f67b3e3, name = CS 9000]

If we would like to find all classes, you can specify **any** for enrollee.

>>> find_class "" any
--Logged in as teacher@ucr.edu--
Anyone is teaching 3 class(es) with '' in their name.
	Class [id = 5090634855c448134f67b3e3, name = CS 9000]
	Class [id = 509066e855c448134f67b3e4, name = CS 10]
	Class [id = 5090671655c448134f67b3e5, name = Woodshop 101]

Finally, we can find all CS classes Galah knows about.

>>> find_class CS any
--Logged in as teacher@ucr.edu--
Anyone is teaching 2 class(es) with 'CS' in their name.
	Class [id = 5090634855c448134f67b3e3, name = CS 9000]
	Class [id = 509066e855c448134f67b3e4, name = CS 10]
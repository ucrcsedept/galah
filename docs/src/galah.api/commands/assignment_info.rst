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

assignment_info
===============

Gets all the properties of an assignment.

Reference
---------

.. function:: assignment_info(id):
    
    :param id: The exact id of the assignment.

Example Usage
-------------

>>> assignment_info 50907cca55c4481a5027103c
--Acting as user jsull003@ucr.edu--
Properties of Assignment [id = 50907cca55c4481a5027103c, name = World Domination Domination]:
	for_class = 509066e855c448134f67b3e4
	due_cutoff = 2012-12-01 23:59:59
	name = World Domination Domination
	due = 2012-12-01 23:59:59

Permissions
-----------

**admin** and **teacher** users can use this command.
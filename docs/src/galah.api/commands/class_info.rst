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

class_info
==========

Lists all assignments for a class along with any other class info.

Reference
---------

.. function:: class_info(for_class):
    
    :param for_class: A part of the name of the class or the class's id.

Example Usage
-------------

Here we will get all assignments for the class **CS 10**.

>>> class_info "CS 10"
--Acting as user jsull003@ucr.edu--
Class [id = 509066e855c448134f67b3e4, name = CS 10] has assignments:
	Assignment [id = 50907cca55c4481a5027103c, name = World Domination Domination]

Permissions
-----------

**admin** and **teacher** users can use this command.
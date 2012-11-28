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

modify_class
============

Changes the name of a class.

Reference
---------

.. function:: modify_class(the_class, name):
    
    :param the_class: The partial name or ID of the class to modify.

    :param name: The new name of the class.

Example Usage
-------------

Here we will change the name of the class **CS 9000** to **CS 9001**.

>>> modify_class "CS 9000" "CS 9001"
--Acting as user jsull003@ucr.edu--
Success! Class [id = 5090634855c448134f67b3e3, name = CS 9000] has been renamed to 'CS 9001'

Permissions
-----------

**admin** users can use this command.
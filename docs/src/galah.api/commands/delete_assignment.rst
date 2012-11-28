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

delete_assignment
=================

Deletes the given assignment.

Because deletion of assignments is a very expensive process (because all of the
submissions made to that assignment need to be deleted from the database AND the
filesystem), this call will pass off the task to Galah's errand boy,
galah.sisyphus, and return immediately.

Reference
---------

.. function:: delete_assignment(id):
    
    :param id: The exact id of the user to delete.

Example Usage
-------------

Here we delete the assignment **Lots of Assignments - Part 4**.

>>> delete_assignment 9001/"part 4"
--Acting as user jsull003@ucr.edu--
Assignment [id = 509c595a55c44810f90ec14f, name = Lots of Assignments - Part 4] has been queued for deletion. Please allow a few minutes for the task to complete.

Permissions
-----------

**admin** and **teacher** users can use this command. Teacher users can only
delete assignments for classes they are assigned to.
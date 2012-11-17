delete_assignment
=================

Deletes the given assignment.

Reference
---------

.. function:: delete_assignment(id):
    
    :param id: The exact id of the user to delete.

Example Usage
-------------

Here we delete the assignment **World Domination Domination**.

>>> delete_assignment 50907cca55c4481a5027103c
--Acting as user jsull003@ucr.edu--
Success! Assignment [id = 50907cca55c4481a5027103c, name = World Domination Domination] deleted.

Permissions
-----------

**admin** and **teacher** users can use this command. Teacher users can only
delete assignments for classes they are assigned to.
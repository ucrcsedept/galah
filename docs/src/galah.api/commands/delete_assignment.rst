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
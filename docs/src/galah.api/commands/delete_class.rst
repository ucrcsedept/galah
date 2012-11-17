delete_class
============

Deletes a given class and all of its assignments.

Because deletion of assignments is a very expensive process (because all of the
submissions made to that assignment need to be deleted from the database AND the
filesystem), this call will pass off the task to Galah's errand boy,
galah.sisyphus, and return immediately.

Reference
---------

.. function:: delete_class(to_delete):
    
    :param to_delete: The name, partial name, or ID of the class to delete.

Example Usage
-------------

Here we will delete the class **CS 9001**.

>>> delete_class 9001
--Acting as user jsull003@ucr.edu--
Class [id = 5090734255c448184a8ffabe, name = CS 9001] has been queued for deletion. Please allow a few minutes for the task to complete.

Permissions
-----------

**admin** users can use this command.
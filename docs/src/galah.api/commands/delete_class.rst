delete_class
============

Deletes a given class and all of its assignments.

Reference
---------

.. function:: delete_class(to_delete)
    
    :param to_delete: The name, partial name, or ID of the class to delete.

Example Usage
-------------

Here we will delete the class **CS 9001**.

>>> delete_class "CS 9001"
--Logged in as jsull003@ucr.edu--
Success! Class [id = 5090734255c448184a8ffabe, name = CS 9001] deleted, and all of its assignments:
	Assignment [id = 509073bf55c448184a8ffabf, name = World Domination]

If we want to delete a class that shares its name with another, you have to
reference the class by the ID.

>>> delete_class Boring\ Class
--Logged in as jsull003@ucr.edu--
An error occurred processing your request: 2 classes match your query of 'Boring Class', however, this API expects 1 class. Refine your query and try again.
	Class [id = 5090754855c4481920ca9325, name = Boring Class]
	Class [id = 5090769855c448196874a4ed, name = Boring Class]
>>> delete_class 5090754855c4481920ca9325
--Logged in as jsull003@ucr.edu--
Success! Class [id = 5090754855c4481920ca9325, name = Boring Class] deleted, and all of its assignments:
	(No assignments found)

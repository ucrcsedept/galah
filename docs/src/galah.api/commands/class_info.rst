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
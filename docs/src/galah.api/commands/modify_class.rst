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
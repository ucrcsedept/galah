drop_student (unassign_teacher)
===============================

Drops a student (or un-enrolls) a student from a given class. May be used on
teachers to un-assign them from classes.

Both :func:`unassign_teacher` and :func:`drop_student` have the same
functionality and in fact are aliases of eachother.

Reference
---------

.. function:: drop_student(email, drop_from):
    
    :param email: The student's email.

    :param drop_from: The ID or name of the class to drop the student from.

.. function:: unassign_teacher(email, drop_from):
    
    :param email: The teacher's email.

    :param drop_from: The ID or name of the class to unassign the teacher from.

Example Usage
-------------

Here we will unassign **teacher@ucr.edu** from **Woodshop 101**. Note that even
though we are using :func:`unassign_teacher`, the result says "dropped." This is
because :func:`unassign_teacher` just calls :func:`drop_student` behind the
scenes.

>>> unassign_teacher teacher@ucr.edu Woodshop
--Acting as user jsull003@ucr.edu--
Success! Dropped User [email = teacher@ucr.edu, account_type = teacher] from Class [id = 5090671655c448134f67b3e5, name = Woodshop 101].

For completeness, we will also drop the student **student@ucr.edu** from
woodshop as well. The command is pretty much the same.

>>> drop_student student@ucr.edu Woodshop
--Acting as user jsull003@ucr.edu--
Success! Dropped User [email = student@ucr.edu, account_type = student] from Class [id = 5090671655c448134f67b3e5, name = Woodshop 101].

Permissions
-----------

**admin** and **teacher** users can use this command. Teacher users can only
drop students from classes they are assigned to.
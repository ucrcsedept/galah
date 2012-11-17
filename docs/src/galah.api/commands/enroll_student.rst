enroll_student (assign_teacher)
===============================

Enrolls a student in a given class. May be used on teachers to assign them to
classes.

Both :func:`assign_teacher` and :func:`enroll_student` have the same
functionality and in fact are aliases of eachother.

Reference
---------

.. function:: enroll_student(email, enroll_in):
    
    :param email: The student's email.
    
    :param enroll_in: Part of the name (case-insensitive) or the ID of the
                      class to enroll the student in.

.. function:: assign_teacher(email, enroll_in):
    
    :param email: The teacher's email.
    
    :param enroll_in: Part of the name (case-insensitive) or the ID of the
                      class to assign the teacher to.

Example Usage
-------------

Here we will assign **teacher@ucr.edu** to **Woodshop 101**. Note that even
though we are using :func:`assign_teacher`, the result says "enrolled." This is
because :func:`assign_teacher` just calls :func:`enroll_student` behind the
scenes.

>>> assign_teacher teacher@ucr.edu Woodshop
--Acting as user jsull003@ucr.edu--
Success! User [email = teacher@ucr.edu, account_type = teacher] enrolled in Class [id = 5090671655c448134f67b3e5, name = Woodshop 101].

For completeness, we will also enroll the student **student@ucr.edu** in
woodshop as well. The command is pretty much the same.

>>> enroll_student student@ucr.edu Woodshop
--Acting as user jsull003@ucr.edu--
Success! User [email = student@ucr.edu, account_type = student] enrolled in Class [id = 5090671655c448134f67b3e5, name = Woodshop 101].

Permissions
-----------

**admin** and **teacher** users can use this command. Teacher users can only
enroll students in classes they are assigned to.
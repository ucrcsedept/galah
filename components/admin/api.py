from galah.db.models import User, Class, Assignment
from galah.db.crypto.passcrypt import seal, serialize_seal

## Users ##
def create_user(email, password, account_type = "student"):
    new_user = User(
        email = email, 
        seal = serialize_seal(seal(password)), 
        account_type = "student"
    )
    
    new_user.save()
    
    return new_user

def delete_user(email):
    to_delete = User.objects.get(email = email).delete()
    
def enroll_student(email, enroll_in):
    # Will throw exception if class does not exist
    Class.objects.get(id = enroll_in)
    
    user = User.objects.get(email = email)
    user.classes.append(enroll_in)
    user.save()
    
def drop_student(email, drop_from):
    user = User.objects.get(email = email)
    user.classes.remove(drop_from)
    user.save()
    
## Classes ##    
def create_class(name):
    new_class = Class(name = name)
    new_class.save()
    
    return new_class
    
def delete_class(id):
    to_delete = Class.objects.get(id = id)
        
    # Delete all the assignments for the class
    assignments = Assignment.objects(for_class = id)
    for i in assignments:
        i.remove()
        
    to_delete.remove()

## Assignments ##
def create_assignment(name, due, for_class):
    new_assignment = Assignment(name = name, due = due, for_class = for_class)
    new_assignment.save()
    
    return new_assignment
    
def delete_assignment(id):
    Assignment.objects.get(id = id).remove()

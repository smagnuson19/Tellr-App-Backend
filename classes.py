from datetime import *

class Family:
    def __init__(self, adults, children, ID, username):
        self.adults = adults #list of person objects
        self.children = children #list of person objects
        self.ID = ID
        self.username = username
    def add_child(childObject):
        self.children.append(childObject)
    def add_adult(adultObject):
        self.adults.append(adultObject)

class Person:
    def __init__(self, email, password, familyID, id, adult, children, allowance=0, savings=0):
        self.email = email
        self.password = password
        self.familyID = familyID
        self.id = id
        self.adult = adult #boolean
        self.family = family #family object
        self.allowance = allowance
        self.savings = savings

    def is_adult(self):
        return self.adult

    def get_email(self):
        return self.email

    def get_password(self):
        return self.password

    def get_familyID(self):
        return self.familyID

    def get_id(self):
        return self.id

    def get_family(self):
        return self.family

    def add_savings(add):
        self.savings = self.savings + add

class Tasks:
    def __init__(self, name, value, deadline, description, personID, familyID, complete=False):
        self.name=name
        self.value=value
        self.deadline = deadline
        self.description = description
        self.personID = personID
        self.familyID = familyID
        self.complete = complete

    def change_deadline(self, deadline):
        self.deadline = deadline

    def change_name(self,newname):
        self.name = (newname)

    def get_name(self):
        return self.name

    def change_description(newdescript):
        self.description = newdescript 

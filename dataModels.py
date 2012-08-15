from google.appengine.ext import db

class Person(db.Model):
    user_account = db.UserProperty(required=True) # Used to store User account
    permissions = db.IntegerProperty(required=True) # Five levels of permissions: Admin, manager, user, requested, banned
	
class Items(db.Model):
    id_number = db.IntegerProperty(required=True) # Unique ID to sort item duplicates
    name = db.StringProperty(required=True) # Primary name of item (book title, product number, etc)
    name2 = db.StringProperty() # Secondary name to search on (eg author name, type of equipment)
    content = db.StringProperty(multiline=True) # Storage of supplimentary details (eg brief description/specs)
    category = db.StringProperty() # Which type/category item is (book, electronics, tool, etc)

    checked_out = db.BooleanProperty() # Flag if checked out
    requested = db.BooleanProperty() # Flag if item has been requested

class Checkout_transaction(db.Model):
    item_id = db.IntegerProperty(required=True)
    holder = db.UserProperty(required=True) # Who currently has this item checked out
    checkout_date = db.DateProperty(auto_now_add=True) # Record checkout date
	
class Request_transaction(db.Model):
    item_id = db.IntegerProperty(required=True)
    requestor = db.UserProperty() # If requested, by who
    request_date = db.DateProperty(auto_now_add=True) # Record request date

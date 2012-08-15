from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Person(db.Model):
    user_account = db.UserProperty(required=True) # Used to store User account
    permissions = db.IntegerProperty(required=True) # Five levels of permissions: Admin, manager, user, requested, banned
	
class Item(polymodel.PolyModel):
    id_number = db.IntegerProperty(required=True) # Unique ID to sort item duplicates
    name = db.StringProperty(required=True) # Primary name of item (book title, product number, etc)
    name2 = db.StringProperty() # Secondary name to search on (eg author name, type of equipment)
    content = db.StringProperty(multiline=True) # Storage of supplimentary details (eg brief description/specs)
    category = db.StringProperty() # Which type/category item is (book, electronics, tool, etc)
    
    store_location = db.StringProperty() # Where should the Thing be stored?
    
    @property
    def is_checked_out(self):
        q = CheckoutTransaction.all().filter('item =', self).filter('checkin_date =', None)
        return q.get() is not None        
    
    @property
    def is_requested(self):
        q = RequestTransaction.all().filter('item =', self).filter('resolved_date =', None)
        return q.get() is not None
    
class BookItem(Item):
    isbn = db.StringProperty(required=True) # Must be a string to support checksum-10 digit "X".
    author = db.StringProperty(required=True)

class CheckoutTransaction(db.Model):
    item = db.ReferenceProperty(Item, required=True)
    holder = db.ReferenceProperty(Person, required=True) # Who currently has this item checked out
    checkout_date = db.DateProperty(auto_now_add=True) # Record checkout date
    checkin_date = db.DateProperty(auto_now_add=False) 
	
class RequestTransaction(db.Model):
    item = db.ReferenceProperty(Item, required=True)
    requestor = db.ReferenceProperty(Person, required=True) # If requested, by who
    request_date = db.DateProperty(auto_now_add=True) # Record request date
    resolved_date = db.DateProperty(auto_now_add=False)

#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# dataModels.py: Definitions of GAE Data Store models.
##
# © 2012 Steven Casagrande (scasagrande@galvant.ca) and
#     Christopher E. Granade (cgranade@cgranade.com).
# This file is a part of the ThingPool Server project.
# Licensed under the AGPL version 3.
##
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##

from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Person(db.Model):
    user_account = db.UserProperty(required=True) # Used to store User account
    permissions = db.IntegerProperty(required=True) # Five levels of permissions: Admin, manager, user, requested, banned
	
class Item(polymodel.PolyModel):
    item_id = db.IntegerProperty(required=True) # Unique ID to sort item duplicates
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

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

## TODO ########################################################################

# Change all instances of "id" in __api__ methods to "uri". This has not been
# done yet, as it depends on a final decision about API paths.

## IMPORTS #####################################################################

## GAE API ##
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

## PYTHON STANDARD LIBRARY ##
import json

## THINGPOOL MODULES ##
import security as s

## DATA MODELS #################################################################

class Person(db.Model):
    user_account = db.UserProperty(required=True) # Used to store User account
    permissions = db.IntegerProperty(required=True) # Five levels of permissions: Admin, manager, user, requested, banned
    
    @property
    def uri(self):
        raise NotImplementedError()
        
    @property
    def can_query_user(self):
        # TODO: check that this is how you query a property of Person, or if
        #       we need to run a query here.
        # TODO: check if is a GAE admin, in which case all other checks are bypassed.
        #       Consider adding that check as a decorator.
        return self.permissions >= s.USER_STATUS_USER
        
    def __api__(self):
        return {
            'id': self.key().id(),
            'nickname': self.user_account.nickname(),
            'g_account': self.user_account.email(),
            'role': s.USER_STATUS_DESCRIPTIONS[self.permissions]
        }
        
    def __json__(self):
        # TODO: move this into the as_json function in api.py.
        return json.dumps(self.__api__())
	
class Category(db.Model):
    name = db.StringProperty(required=True)
    category_parent = db.SelfReferenceProperty()
        # We don't use the GAE built-in parent/child relation support here,
        # as that association is permenant, and we want user reconfigurable
        # categories.
        
    @property
    def uri(self):
        raise NotImplementedError()
        
    def __api__(self):
        return {
            'id': self.key().id(),
            'name': self.name,
            'parent': self.category_parent.key().id() # FIXME: make this a URI.
        }
	
class Item(polymodel.PolyModel):
    name = db.StringProperty(required=True) # Primary name of item (book title, product number, etc)
    name2 = db.StringProperty() # Secondary name to search on (eg author name, type of equipment)
    content = db.StringProperty(multiline=True) # Storage of supplimentary details (eg brief description/specs)
    category = db.ReferenceProperty(Category, required=True) # Which type/category item is (book, electronics, tool, etc)
    
    store_location = db.StringProperty() # Where should the Thing be stored?
    
    @property
    def uri(self):
        raise NotImplementedError()
        
    def __api__(self):
        data = {
            'id': self.key().id(),
            'name': self.name,
            'category': self.category.uri
        }
        
        if self.name2 is not None:
            data['subname'] = self.name2
            
        if self.content is not None:
            data['content'] = self.content
            
        if self.store_location is not None:
            data['store_location'] = self.store_location
            
        return data
    
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
    
    def __api__(self):
        data = super(BookItem, self).__api__()
        data['isbn'] = self.isbn
        data['author'] = self.author
        return data        

class CheckoutTransaction(db.Model):
    item = db.ReferenceProperty(Item, required=True)
    holder = db.ReferenceProperty(Person, required=True) # Who currently has this item checked out
    checkout_date = db.DateProperty(auto_now_add=True) # Record checkout date
    checkin_date = db.DateProperty(auto_now_add=False) 
    
    def __api__(self):
        data = {
            'item': self.item.uri,
            'holder': self.holder.uri,
            'checkout_date': self.checkout_date
        }
        if self.checkin_date is not None:
            data['checkin_date'] = self.checkin_date
        return data
	
class RequestTransaction(db.Model):
    item = db.ReferenceProperty(Item, required=True)
    requestor = db.ReferenceProperty(Person, required=True) # If requested, by who
    request_date = db.DateProperty(auto_now_add=True) # Record request date
    resolved_date = db.DateProperty(auto_now_add=False)
    
    
    def __api__(self):
        data = {
            'item': self.item.uri,
            'requestor': self.requestor.uri,
            'request_date': self.request_date
        }
        if self.resolved_date is not None:
            data['resolved_date'] = self.resolved_date
        return data

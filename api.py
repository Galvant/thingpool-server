#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# api.py: Definitions of API methods.
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

## IMPORTS #####################################################################

## GAE API ##
from google.appengine.api import users
from google.appengine.ext import db

import webapp2

## PYTHON STANDARD LIBRARY ##
import json
import datetime

## THINGPOOL MODULES ##
from dataModels import *
from security import *

## API REQUEST HANDLERS ########################################################

def as_json(obj):
    # TODO: Generate error if list contents do not have __api__()
    #assert hasattr(obj, '__api__'), "Cannot serialize {} to JSON.".format(obj)
    if hasattr(obj,'__api__'):
        return json.dumps(obj.__api__())
    else:
        return json.dumps([o.__api__() for o in obj])

class UserHandler(webapp2.RequestHandler):

    @require_permission('query_user')
    @require_gae_login('deny')
    def get(self, user_id):
        """
        GET /users/{id}
        Queries the user given by the ID {id}.
        """
        q = Person.get_by_id(user_id)
        self.response.write(as_json(q.get()))

    # Permissions checking is a little more complicated here, so we
    # don't use @require_permission.
    @require_gae_login('deny')
    def modify(self, user_id):
        """
        MODIFY /users/{id}
        Modifies the user given by ID {id}.
        """
        user = users.get_current_user()
        q = Person.get_by_id(user_id)
        target_user = q.get()
        new_permission = self.request.get('permissions')
        
        # Filter invalid permission settings
        # TODO: move this filter to security.py
        if (new_permission < USER_STATUS_BANNED) or (new_permission > USER_STATUS_ADMIN):
            self.error(400)
            return
            
        # Manager can change those below
        # TODO: Add can_change_permissions to UserModel.
        if (user.permissions >= USER_STATUS_MANAGER) and (new_permission < USER_STATUS_MANAGER):
            target_user.permissions = new_permission
            db.put(target_user)            
        # Admins can add more admins. GAE admin should not have to handle system at all.
        elif (user.permissions >= USER_STATUS_ADMIN) and (new_permission <= USER_STATUS_ADMIN):
            target_user.permissions = new_permission
            db.put(target_user)
        
        
class UserListHandler(webapp2.RequestHandler):
    @require_permission('query_users')
    @require_gae_login('deny')
    def get(self):
        """
        GET /users
        Returns a list of all users matching a given filter, paginated and
        starting at a given index.
        """
        user = users.get_current_user()
        q = Person.all().filter('user_account = ', user)
        
        # TODO: build a filter from query strings, paginate, serialize to JSON.
        if q.get().permissions >= USER_STATUS_MANAGER: # if admin or manager
            q = Person.all().filter('permissions = ', self.request.get('permissions'))
            
    
    @require_permission('request_account', reason="Banned users cannot request accounts.") # Denied only for banned users.
    @require_gae_login('deny')
    def post(self):
        """
        POST /users
        Creates a new user as specified by the POST content.
        """
        # Note, anyone can request an account 
        user = users.get_current_user()
        q = Person.all().filter("user_account = ", user)
        q = q.get()
        if not q: # If does not currently have account, add to list
            p = Person(
                    user_account = users.get_current_user(),
                    permissions = USER_STATUS_REQUESTED # Set to 'requested' status
                    ) 
            p.put()
        # else silently fail


class ItemListHandler(webapp2.RequestHandler):
    @require_permission('new_item')
    @require_gae_login('deny')
    def post(self):
        """
        POST /items
        Creates a new item as specified by the POST content.
        """
        item = Item(
                    name = self.request.get('name')
                    )
        item.put()
        
    @require_permission('query_items')
    @require_gae_login('deny')
    def get(self):
        """
        GET /items
        Returns a list of all items matching a given filter
        """
        #TODO: Filter results and whatnot, serialize to JSON
        q = Item.all()


class ItemHandler(webapp2.RequestHandler):
    @require_permission('query_item')
    @require_gae_login('deny')
    def get(self, item_id):
        """
        GET /items/{id}
        Queries the item given by the ID {id}.
        """
        q = Item.get_by_id(item_id)
        self.response.write(as_json(q.get()))
    
    @require_permission('modify_item')
    @require_gae_login('deny')
    def modify(self, item_id):
        """
        MODIFY /items/{id}
        Modifies the item given by ID {id}.
        """
        q = Item.get_by_id(item_id)
        item = q.get()
        new_category = Category.get_by_id( self.query.get('category_id') )
        new_category = new_category.get()
        
        item.name = self.request.get('name')
        item.category = new_category
        
        if self.request.get('name2') is not "":
            item.name2 = self.request.get('name2')
            
        if self.request.get('content') is not "":
            item.content = self.request.get('content')
        
        if self.request.get('store_location') is not "":
            item.store_location = self.request.get('store_location')
        
        db.put(item)
 
        
class CategoryHandler(webapp2.RequestHandler):
    @require_permission('query_category')
    @require_gae_login('deny')
    def get(self, category_id):
        """
        GET /categories/{id}
        Queries the category by the ID {id}
        """
        q = Category.get_by_id(category_id)
        self.response.write(as_json(q.get()))
        
    @require_permission('modify_category')
    @require_gae_login('deny')
    def modify(self, category_id):
        """
        MODIFY /categories/{id}
        Modifies the category by the ID {id}
        """
        # TODO: Everything
        pass


class CheckoutListHandler(webapp2.RequestHandler):
    @require_permission('new_checkout')
    @require_gae_login('deny')
    def post(self):
        """
        POST /checkout
        Creates a new checkout transaction
        """
        # TODO: 
        #       - Direct item transfer without explicit 'checkin'
        #           - Clear previous checkout transaction (ie call checkin routines)
        #           - Deny if same user already has it checked out
        #       - Also includes clearing outstanding requests if required
        q = Item.get_by_id(self.request.get('item_id'))
        c = CheckoutTransaction(
                                item=q.get(),
                                holder = users.get_current_user()
                                )
        c.put()
        
    @require_permission('query_checkout_transactions')
    @require_gae_login('deny')
    def get(self):
        """
        GET /checkout
        Query checkout transaction history for a user or item
        """
        # TODO: Everything
        pass

class CheckoutHandler(webapp2.RequestHandler):
    @require_permission('query_checkout')
    @require_gae_login('deny')
    def get(self, checkout_id):
        """
        GET /checkout/{id}
        Query specific checkout transaction details
        """
        q = Checkout.get_by_id(checkout_id)
        self.response.write(as_json(q.get()))
    
    @require_permission('modify_checkout')
    @require_gae_login('deny')
    def modify(self, checkout_id):
        """
        MODIFY /checkout/{id}
        Modify checkout transaction to include a checkin date
        """
        # TODO: I think we need to restrict normal users to only checking in others'
        # items if they are in turn checking the item out
        # ie direct item transfer.
        q = Checkout.get_by_id(checkout_id)
        transaction = q.get()
        transaction.checkin_date = datetime.datetime.now()
        db.put(transaction)


class RequestListHandler(webapp2.RequestHandler):
    @require_permission('new_request')
    @require_gae_login('deny')
    def post(self):
        """
        POST /request
        Add a new request transaction
        """
        pass
    
    @require_permission('query_request_transactions')
    @require_gae_login('deny')
    def get(self):
        """
        GET /request
        Query request transaction history for a user or item
        """
        # TODO: Everything
        pass
    
    
class RequestHandler(webapp2.RequestHandler):
    @require_permission('query_request')
    @require_gae_login('deny')
    def get(self, request_id):
        """
        GET /request/{id}
        Query specific request transaction details
        """
        # TODO: Everything
        pass
        
    @require_permission('modify_request')
    @require_gae_login('deny')
    def modify(self, checkout_id):
        """
        MODIFY /request/{id}
        Modify request transaction to include a resolution date
        """
        # TODO: Everything
        pass
        

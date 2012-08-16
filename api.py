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

## PYTHON STANDARD LIBRARY ##
import json

## THINGPOOL MODULES ##
import dataModels
from security import *

## API REQUEST HANDLERS ########################################################

def as_json(obj):
    assert hasattr(obj, '__api__'), "Cannot serialize {} to JSON.".format(obj)
    return json.dumps(obj.__api__())

class UserHandler(webapp2.RequestHandler):

    @require_permission('query_user')
    @require_gae_login('deny')
    def get(self, user_id):
        """
        GET /users/{id}
        Queries the user given by the ID {id}.
        """
        # TODO: grab the user_id, write appropriate headers.
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
        pass
        
        
class UserListHandler(webapp2.RequestHander):
    @requre_permission('query_users')
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
        # TODO: Add check if currently a user before trying to add, and deny those who are banned 
        p = Person(
                user_account = users.get_current_user(),
                permissions = USER_STATUS_REQUESTED # Set to 'requested' status
                ) 
        p.put()


class ItemListHandler(webapp2.RequestHandler):
    @require_permission('new_item')
    @require_gae_login('deny')
    def post(self):
        """
        POST /items
        Creates a new item as specified by the POST content.
        """
        # TODO: Generate item ID right here, should not be user defined
        item = Item(
                    id_number = self.request.get('id_number'),
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
        # TODO: grab the item_id, write appropriate headers.
        q = Item.get_by_id(user_id)
        self.response.write(as_json(q.get()))
    
    @require_permission('modify_item')
    @require_gae_login('deny')
    def modify(self, item_id):
        """
        MODIFY /items/{id}
        Modifies the item given by ID {id}.
        """
        pass
 
        
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

# TODO: RESTify the other resources below.
        
class checkinItem(webapp2.RequestHandler):
    def post(self):
        # TODO: Handle item checkin process
        
class requestItem(webapp2.RequestHandler):
    def post(self):
        # TODO: Handle item request process
        
class queryCheckoutList(webapp2.RequestHandler):
    def post(self):
        # TODO: Return list of current / historical checkouts a user has performed
        # Admin & manager should be able to do this against other user accounts
        
class queryRequestList(webapp2.RequestHandler):
    def post(self):
        # TODO: Return list of current / historical item requests a user has performed
        # Admin & manager should be able to do this against other user accounts

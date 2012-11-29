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
        
class ServerInfoHandler(webapp2.RequestHandler):
    # No security here, all should be able to get this information
    def get(self):
        """
        GET /info
        Queries basic server information (eg: API version)
        """
        pass

class UserHandler(webapp2.RequestHandler):
    @require_permission('query_user')
    @require_gae_login('deny')
    def get(self, user_id):
        """
        GET /users/{id}
        Queries the user given by the ID {id}.
        """
        try:
            user_id = int(user_id)
            q = Person.get_by_id(user_id)
            self.response.write(as_json(q))
        except ValueError:
            self.error(400)

    # Permissions checking is a little more complicated here, so we
    # don't use @require_permission.
    @require_gae_login('deny')
    def post(self, user_id):
        """
        POST /users/{id}
        Modifies the user given by ID {id}.
        """
        user = users.get_current_user()
        try:
            user_id = int(user_id)
            target_user = Person.get_by_id(user_id)
            new_permission = self.request.get('permissions')
            
            if new_permission is not "":
                new_permission = int(new_permission)
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
        except ValueError:
            self.error(400)
        
        
class UserListHandler(webapp2.RequestHandler):
    @require_permission('query_users')
    @require_gae_login('deny')
    def get(self):
        """
        GET /users
        Returns a list of all users matching a given filter, paginated and
        starting at a given index.
        """
        # TODO: filter on additional query strings
        users = Person.all()
        if self.request.get('permissions') is not "":
            try:
                permissions = int(self.request.get('permissions'))
                users = Person.all().filter('permissions = ', permissions)
            except ValueError:
                self.error(400)
        self.response.write(as_json(users))
    
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
        if self.request.post('name') is not "":
            item = Item(
                        name = self.request.post('name')
                        )
            item.put()
        else:
            self.error(400)
        
    @require_permission('query_items')
    @require_gae_login('deny')
    def get(self):
        """
        GET /items
        Returns a list of all items matching a given filter
        """
        items = Item.all()
        if self.request.get("category") is not "":
            try:
                category = Category.get_by_id( int(self.request.get("category") )
                items = Item.all().filter("category = ", category)
            except ValueError:
                self.error(400)
        self.response.write(as_json(items))         


class ItemHandler(webapp2.RequestHandler):
    @require_permission('query_item')
    @require_gae_login('deny')
    def get(self, item_id):
        """
        GET /items/{id}
        Queries the item given by the ID {id}.
        """
        try:
            item_id = int(item_id)
            q = Item.get_by_id(item_id)
            self.response.write(as_json(q))
        except ValueError:
            self.error(400)
    
    @require_permission('modify_item')
    @require_gae_login('deny')
    def post(self, item_id):
        """
        POST /items/{id}
        Modifies the item given by ID {id}.
        """
        try:
            item_id = int(item_id)
            item = Item.get_by_id(item_id)
            if item is not None:
                if self.request.post('category_id') is not "":
                    new_category = Category.get_by_id(int(self.request.post('category_id')))
                    item.category = new_category
                if self.request.post('name') is not "":
                    item.name = self.request.post('name')
                if self.request.post('name2') is not "":
                    item.name2 = self.request.post('name2')  
                if self.request.post('content') is not "":
                    item.content = self.request.post('content')
                if self.request.post('store_location') is not "":
                    item.store_location = self.request.post('store_location')
                db.put(item)
            else:
                self.error(400)
        except ValueError:
            self.error(400)


class CategoryListHandler(webapp2.RequestHandler):
    @require_permission('query_categories')
    @require_gae_login('deny')
    def get(self):
        """
        GET /categories
        Queries list of categories, filtered by some parent
        If no parent specified, assume root categories
        """
        if self.request.get('parent') is "":
            categories = Category.all().filter("category_parent = ", None)
        else:
            try:
                parent_id = int(self.request.get('parent'))
                category_parent = Category.get_by_id(parent_id)
                categories = Category.all().filter("category_parent = ", category_parent)
            except ValueError:
                self.error(400)
        self.response.write(as_json(categories))
 
        
class CategoryHandler(webapp2.RequestHandler):
    @require_permission('query_category')
    @require_gae_login('deny')
    def get(self, category_id):
        """
        GET /categories/{id}
        Queries the category by the ID {id}
        """
        try:
            category_id = int(category_id)
            q = Category.get_by_id(category_id)
            self.response.write(as_json(q))
        except ValueError:
            self.error(400)
        
    @require_permission('modify_category')
    @require_gae_login('deny')
    def post(self, category_id):
        """
        POST /categories/{id}
        Modifies the category by the ID {id}
        """
        try:
            category_id = int(category_id)
            q = Category.get_by_id(category_id)
            new_parent = self.request.post('parent_id')
            if new_parent is not "":
                new_parent = Category.get_by_id(int(new_parent))
                q.category_parent = new_parent
            new_name = self.request.post('name')
            if new_name is not "":
                q.name = new_name
            db.put(q)
        except ValueError:
            self.error(400)


class CheckoutListHandler(webapp2.RequestHandler):
    @require_permission('new_checkout')
    @require_gae_login('deny')
    def post(self):
        """
        POST /checkout
        Creates a new checkout transaction
        """
        try:
            item = Item.get_by_id(int(self.request.post('item_id')))
            user = Person.get_person()
            if user.permissions is USER_STATUS_KIOSK: # If kiosk account, use provided keycard
                keycard_id = self.request.post('keycard')
                if keycard_id is not "":
                    user = Person.get_person(keycard=keycard_id)
                else:
                    self.error(400)
            if item.is_checked_out(): # Clear previous checkout transaction
                prev_checkout = CheckoutTransaction.all().filter('item =', item).filter('checkin_date =', None)
                prev_checkout = prev_checkout.get()
                prev_checkout.checkin_date = datetime.datetime.now()
                db.put(prev_checkout)
            if item.is_requested(): # If item has an outstanding request transaction for this user
                request = RequestTransaction.all().filter('item =', self).filter('resolved_date =', None).filter('requestor = ', user)
                request = request.get()
                request.resolved_date = datetime.datetime.now()
                db.put(request)
            c = CheckoutTransaction(
                                    item=item,
                                    holder = user
                                    )
            c.put()
        except ValueError:
            self.error(400)
        
    @require_permission('query_checkout_transactions')
    @require_gae_login('deny')
    def get(self):
        """
        GET /checkout
        Query checkout transaction history for a user or item
        """
        # TODO: Consider limiting number of transactions returned
        checkouts = CheckoutTransaction.all()
        if self.request.get("item_id") is not "":
            try:
                item = Item.get_by_id(int(self.requst.get('item_id')))
                checkouts = checkouts.filter("item = ", item)
            except ValueError:
                self.error(400)
        if self.request.get("user_id") is not "":
            try:
                user = Person.get_by_id(int(self.requst.get('user_id')))
                checkouts = checkouts.filter("holder = ", user)
            except ValueError:
                self.error(400)
                
        year_start = self.request.get('year_start')
        month_start = self.request.get('month_start')
        day_start = self.request.get('day_start')
        if (year_start is not "") and (month_start is not "") and (day_start is not ""):
            try:
                year_start = int(year_start)
                month_start = int(month_start)
                day_start = int(day_start)
                start_date = datetime.datetime(year_start,month_start,day_start)
                checkouts = checkouts.filter('checkout_date >= ', start_date)
            except ValueError:
                self.error(400)
                
        year_end = self.request.get('year_end')
        month_end = self.request.get('month_end')
        day_end = self.request.get('day_end')
        if (year_end is not "") and (month_end is not "") and (day_end is not ""):
            try:
                year_end = int(year_end)
                month_end = int(month_end)
                day_end = int(day_end)
                end_date = datetime.datetime(year_end,month_end,day_end)
                checkouts = checkouts.filter('checkout_date <= ', end_date)
            except ValueError:
                self.error(400)
                
        self.response.write(as_json(checkouts))

class CheckoutHandler(webapp2.RequestHandler):
    @require_permission('query_checkout')
    @require_gae_login('deny')
    def get(self, checkout_id):
        """
        GET /checkout/{id}
        Query specific checkout transaction details
        """
        try:
            checkout_id = int(checkout_id)
            q = CheckoutTransaction.get_by_id(category_id)
            self.response.write(as_json(q))
        except ValueError:
            self.error(400)
    
    @require_permission('modify_checkout')
    @require_gae_login('deny')
    def post(self, checkout_id):
        """
        POST /checkout/{id}
        Modify checkout transaction to include a checkin date
        """
        try:
            transaction = CheckoutTransaction.get_by_id(int(checkout_id))
            user = Person.get_person()
            if (transaction.holder is user) or (user.permissions >= USER_STATUS_MANAGER):
                transaction.checkin_date = datetime.datetime.now()
                db.put(transaction)
        except ValueError:
            self.error(400)


class RequestListHandler(webapp2.RequestHandler):
    @require_permission('new_request')
    @require_gae_login('deny')
    def post(self):
        """
        POST /request
        Add a new request transaction
        """
        try:
            item = Item.get_by_id(int(self.request.post('item_id')))
            user = Person.get_person()
            # Check if current user does not already have outstanding request on item
            if not RequestTransaction.all().filter("item = ", item).filter("requestor = ",user).filter("resolved_date = ", None):
                c = RequestTransaction(
                                        item=item,
                                        requestor = user
                                        )
                c.put()
            # else silently fail
        except ValueError:
            self.error(400)
    
    @require_permission('query_request_transactions')
    @require_gae_login('deny')
    def get(self):
        """
        GET /request
        Query request transaction history for a user or item
        """
        # TODO: Consider limiting number of transactions returned
        # also filter on current outstanding requests
        requests = RequestTransaction.all()
        if self.request.get("item_id") is not "":
            try:
                item = Item.get_by_id(int(self.requst.get('item_id')))
                requests = requests.filter("item = ", item)
            except ValueError:
                self.error(400)
        if self.request.get("user_id") is not "":
            try:
                user = Person.get_by_id(int(self.requst.get('user_id')))
                requests = requests.filter("requestor = ", user)
            except ValueError:
                self.error(400)
                
        year_start = self.request.get('year_start')
        month_start = self.request.get('month_start')
        day_start = self.request.get('day_start')
        if (year_start is not "") and (month_start is not "") and (day_start is not ""):
            try:
                year_start = int(year_start)
                month_start = int(month_start)
                day_start = int(day_start)
                start_date = datetime.datetime(year_start,month_start,day_start)
                requests = requests.filter('checkout_date >= ', start_date)
            except ValueError:
                self.error(400)
                
        year_end = self.request.get('year_end')
        month_end = self.request.get('month_end')
        day_end = self.request.get('day_end')
        if (year_end is not "") and (month_end is not "") and (day_end is not ""):
            try:
                year_end = int(year_end)
                month_end = int(month_end)
                day_end = int(day_end)
                end_date = datetime.datetime(year_end,month_end,day_end)
                requests = requests.filter('checkout_date <= ', end_date)
            except ValueError:
                self.error(400)
        self.response.write(as_json(requests))
    
    
class RequestHandler(webapp2.RequestHandler):
    @require_permission('query_request')
    @require_gae_login('deny')
    def get(self, request_id):
        """
        GET /request/{id}
        Query specific request transaction details
        """
        try:
            request_id = int(request_id)
            q = RequestTransaction.get_by_id(category_id)
            self.response.write(as_json(q))
        except ValueError:
            self.error(400)
        
    @require_permission('modify_request')
    @require_gae_login('deny')
    def post(self, request_id):
        """
        POST /request/{id}
        Modify request transaction to include a resolution date
        """
        # TODO: A request should only be cleared by the request-owner
        #
        # Do we need this? These are automatically resolved when the request-owner
        # checks the item out
        try:
            transaction = RequestTransaction.get_by_id(int(request_id))
            transaction.resolved_date = datetime.datetime.now()
            db.put(transaction)
        except ValueError:
            self.error(400)

        

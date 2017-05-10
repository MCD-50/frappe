from __future__ import unicode_literals
import frappe
import os
import json
from frappe import conf
from frappe.utils.kickapp.reply import Reply
from frappe.desk.form.load import get_communications


"""for testing purpose"""
# @frappe.whitelist()
# def get_communication():
# 	issue_list = frappe.get_list('Issue', ["name", "raised_by", "subject", "status", "description", 
# 				"customer_name", "company", "customer", "contact"], limit_start=0, limit_page_length=20)
# 	results = []
# 	for i in issue_list:
# 		results.append(get_communications('Issue', i.name))
# 	return results


@frappe.whitelist()
def get_dev_port():
	"""return dev port and mode"""
	return conf.get("developer_mode"), conf.get('socketio_port')

@frappe.whitelist()
def get_users(obj):
	"""return users in blocks of 20"""
	"""
	 obj.page_count : start_page
	"""
	return get_response_from_method_name("get_users", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def get_user_by_email(obj):
	"""return user info"""
	"""
	 obj.email : email address of user
	"""
	return get_response_from_method_name("get_user_by_email", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def get_users_in_room(obj):
	"""return users in room"""
	"""
	 obj.room : chat room
	"""
	return get_response_from_method_name("get_users_in_room", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def set_users_in_room(obj):
	"""set users in room"""
	"""
	 obj.room : chat room
	 obj.users : list of users
	"""
	return get_response_from_method_name("set_users_in_room", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def remove_user_from_group(obj):
	"""remove user from group"""
	"""
	 obj.room : chat room
	 obj.email : user id, which is to be removed
	"""
	return get_response_from_method_name("remove_user_from_group", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def get_issues_for_room(obj):
	"""remove user from group"""
	"""
	 obj.room : chat room 
	"""
	return get_response_from_method_name("get_issues_for_room", frappe._dict(json.loads(obj)))


@frappe.whitelist()
def get_messages(obj):
	"""get messages at start time when user enter the app"""
	"""
	 obj.room : chat room
	 obj.email : user id, which is to be removed
	"""
	get_response_from_method_name("get_messages", frappe._dict(json.loads(obj)), False)

# @frappe.whitelist()
# def get_issues(obj):
# 	return get_response_from_method_name("get_issues", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def send_message(obj):

	get_response_from_method_name("send_message", frappe._dict(json.loads(obj)), False)


def get_response_from_method_name(method_name, obj, is_return = True):
	"""returns the correct method"""	
	if is_return:
		return getattr(Reply(), method_name)(obj)
	getattr(Reply(), method_name)(obj)

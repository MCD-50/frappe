from __future__ import unicode_literals
import frappe
import os
import json
from frappe import conf
from frappe.utils.kickapp.reply import Reply

@frappe.whitelist()
def get_dev_port():
	return conf.get("developer_mode"), conf.get('socketio_port')

@frappe.whitelist()
def get_users(obj):
	return get_response_from_method_name("get_users", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def get_user_by_email(obj):
	return get_response_from_method_name("get_user_by_email", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def get_users_in_room(obj):
	return get_response_from_method_name("get_users_in_room", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def set_users_in_room(obj):
	return get_response_from_method_name("set_users_in_room", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def remove_user_from_group(obj):
	return get_response_from_method_name("remove_user_from_group", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def get_messages(obj):
	get_response_from_method_name("get_messages", frappe._dict(json.loads(obj)), False)

# @frappe.whitelist()
# def get_issues(obj):
# 	return get_response_from_method_name("get_issues", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def get_issues_for_user(obj):
	return get_response_from_method_name("get_issues_for_user", frappe._dict(json.loads(obj)))

@frappe.whitelist()
def send_message(obj):
	get_response_from_method_name("send_message", frappe._dict(json.loads(obj)), False)


# @frappe.whitelist()
# def load_more(query):
# 	query = frappe._dict(json.loads(query))
# 	return get_response_from_method_name("load_more", query)

# @frappe.whitelist()
# def get_all_bots():
# 	return getattr(Reply(), 'get_all_bots')()

# @frappe.whitelist()
# def get_meta(bot_name):
# 	return frappe.get_meta(str(bot_name).strip())

def get_response_from_method_name(method_name, obj, is_return = True):
	if is_return:
		return getattr(Reply(), method_name)(obj)
	getattr(Reply(), method_name)(obj)

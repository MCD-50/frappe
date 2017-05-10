from __future__ import unicode_literals
import frappe
import os
import json
from frappe import conf


@frappe.whitelist()
def get_dev_port():
	return conf.get("developer_mode"), conf.get('socketio_port')

@frappe.whitelist()
def get_issues(obj):
	# convert to dict
	if obj:
		obj = frappe._dict(obj)
	

	return None

@frappe.whitelist()
def get_opportunities(obj):
	# convert to dict
	if obj:
		obj = frappe._dict(obj)
	

	filters = {}
	return None


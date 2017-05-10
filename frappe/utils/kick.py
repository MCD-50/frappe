from __future__ import unicode_literals
import frappe
import os
import json
from frappe import conf
from frappe.utils import today, getdate, add_to_date
from frappe.desk.form.load import get_communication_data



@frappe.whitelist()
def get_dev_port():
	return conf.get("developer_mode"), conf.get('socketio_port')

@frappe.whitelist()
def get_issues(obj):
	obj = frappe._dict(obj)

	from_last_week = add_to_date(getdate(today()), days=-7, as_string=True)
	issues = frappe.get_list('Issue', fields="*", filters={"modified":(">", from_last_week)})
	return issues

@frappe.whitelist()
def get_opportunities(obj):
	obj = frappe._dict(obj)

	from_last_month = add_to_date(getdate(today()), days=-30, as_string=True)
	opportunity = frappe.get_list('Opportunity', fields="*", filters={"modified":(">", from_last_month)})
	return opportunity

@frappe.whitelist()
def get_communications(obj):
	# self, doctype, name, limit_start, length, communications= [], after = None
	"""get get_communication_data returns only 20 items at a time"""
	obj = frappe._dict(obj)
	
	communications = []
	start = obj.limit_start
	x = get_communication_data(obj.doctype, obj.name, start, 20, obj.after)
	while x is not None:
		for c in x:
			if c.communication_type=="Communication":
				c.attachments = json.dumps(frappe.get_all("File", fields=["file_url", "is_private"],
				filters={"attached_to_doctype": "Communication", "attached_to_name": c.name}))

			elif c.communication_type=="Comment" and c.comment_type=="Comment":
				c.content = frappe.utils.markdown(c.content)
		communications += x
		if len(x) > 19:
			start = start + 20
			x = get_communication_data(obj.doctype, obj.name, start, 20, obj.after)
		else:
			x = None
	return communications

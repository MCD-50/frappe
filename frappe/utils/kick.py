from __future__ import unicode_literals

import frappe
import json
from frappe import _
from frappe.utils import today, getdate, add_to_date
from frappe.desk.form.load import get_communication_data, get_attachments

from html2text import html2text

@frappe.whitelist()
def get_dev_port():
	return frappe.conf.get("developer_mode"), frappe.conf.get('socketio_port')

@frappe.whitelist()
def get_issues(obj):
	# obj = frappe._dict(obj)
	from_last_week = add_to_date(getdate(today()), days=-7, as_string=True)
	issues = []
	for i in frappe.get_list('Issue', fields="*", filters={"modified":(">", from_last_week)}):
		try:
			i.subject = html2text(i.subject)
			i.description = html2text(i.description)
			issues.append(i)
		except HTMLParser.HTMLParseError:
			issues.append(i)
	return issues
	

@frappe.whitelist()
def get_opportunities(obj):
	# obj = frappe._dict(obj)
	from_last_month = add_to_date(getdate(today()), days=-10, as_string=True)
	opportunity = frappe.get_list('Opportunity', fields="*", filters={"modified":(">", from_last_month)})
	return opportunity


@frappe.whitelist()
def get_communications(obj):
	# doctype, name, limit_start, length, communications= [], after = None
	obj = frappe._dict(json.loads(obj))
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
			
			if c.content is not None:
				try:
					c.content = html2text(c.content)
				except HTMLParser.HTMLParseError:
					c.content = c.content
			
		communications += x
		if len(x) > 19:
			start = start + 20
			x = get_communication_data(obj.doctype, obj.name, start, 20, obj.after)
		else:
			x = None
	return communications


@frappe.whitelist()
def send_email(obj):
	obj = frappe._dict(json.loads(obj))
	frappe.sendmail(recipients = [obj.recipients], sender = obj.sender, subject = _("Re: ") + obj.subject, content = obj.content)
from __future__ import unicode_literals
import frappe
import frappe.utils
import json


@frappe.whitelist()
def add_doc(data):
	"""Returns a new document of the given DocType with provided values.

	:param data.doctype: DocType of the new document.
	:param data.info: Dict to facilitate add operation.
	"""
	obj = get_dict_obj(data)
	doctype = obj.get('doctype')
	info = obj.get('info')
	
	print([x for x in frappe.local])
	try:
		x = frappe.new_doc(doctype, info.get('parent_doc'), info.get('parentfield'))
		for key, value in info.items():
			if key == 'parent_doc' or key == 'parentfield':
				continue
			# set all values
			x[key] = value
		return x
	except Exception, e:
		return e


@frappe.whitelist()
def delete_doc(data):
	"""Delete a document..

	:param data.doctype: DocType of document to be delete.
	:param data.info: Dict to facilitate delete operation.
	"""
	obj = get_dict_obj(data)


@frappe.whitelist()
def update_doc(data):
	"""Returns a updated document of the given DocType with provided info.

	:param data.doctype: DocType of document to be update.
	:param data.info: Dict to facilitate update operation.
	"""
	obj = get_dict_obj(data)


@frappe.whitelist()
def get_doc(data):
	"""Returns a document if exists else create new document of the given DocType with provided info.

	:param data.doctype:DocType of the new or existing document.
	:param data.info: Dict to facilitate get operation.
	"""
	obj = get_dict_obj(data)


@frappe.whitelist()
def get_list(data):
	"""Returns list of document of the given DocType.

	:param data.doctype:DocType of documents to be fetched.
	:param data.info: Dict to facilitate list operation.
	"""
	obj = get_dict_obj(data)


@frappe.whitelist()
def get_meta(data):
	"""Returns meta of document of the given DocType.

	:param data.doctype:DocType of document.
	:param data.info: Dict to facilitate meta operation.
	"""
	obj = get_dict_obj(data)


def get_dict_obj(data):
	obj = json.loads(data.decode('string-escape').strip('"'))
	return frappe._dict(obj)

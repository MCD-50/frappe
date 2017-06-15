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
	res = 'Something went wrong.'
	exe = None
	try:
		obj = get_json_obj(data)
		doctype = obj.get('doctype')
		doc = obj.get('info')

		doc['doctype'] = doctype

		if doc.get("parent") and doc.get("parenttype"):
			# inserting a child record
			parent = frappe.get_doc(doc.get("parenttype"), doc.get("parent"))
			parent.append(doc.get("parentfield"), doc)
			parent.save()
			res = parent.as_dict()
		else:
			doc = frappe.get_doc(doc).insert()
			res = doc.as_dict()
	except Exception, e:
		exe = e

	return {
		'res': res,
		'exe': exe
	}


@frappe.whitelist()
def delete_doc(data):
	"""Delete a document..

	:param data.doctype: DocType of document to be delete.
	:param data.info: Dict to facilitate delete operation.
	"""
	res = 'Something went wrong.'
	exe = None
	try:
		obj = get_json_obj(data)
		doctype = obj.get('doctype')
		info = obj.get('info')

		name = info.get('name')
		filters = info.get('filters') or {}
		filters['name'] = name
		items = frappe.get_list(doctype, filters=filters)
		if len(items) > 0:
			res = frappe.get_doc(doctype, name).as_dict()
			frappe.delete_doc(doctype, name)
		else:
			res = 'Item not found.'

	except Exception, e:
		exe = e

	return{
		'res': res,
		'exe': exe
	}


@frappe.whitelist()
def update_doc(data):
	"""Returns a updated document of the given DocType with provided info.

	:param data.doctype: DocType of document to be update.
	:param data.info: Dict to facilitate update operation.
	"""
	res = 'Something went wrong.'
	exe = None
	try:
		obj = get_json_obj(data)
		doctype = obj.get('doctype')
		info = obj.get('info')

		# get name and delete from json
		name = info.get('name')
		del info['name']
		doc = frappe.get_doc(doctype, name)
		doc.update(info)
		doc.save()

		res = doc.as_dict()

	except Exception, e:
		exe = e

	return{
		'res': res,
		'exe': exe
	}


@frappe.whitelist()
def get_doc(data):
	"""Returns a document if exists else create new document of the given DocType with provided info.

	:param data.doctype:DocType of the new or existing document.
	:param data.info: Dict to facilitate get operation.
	"""
	res = 'Something went wrong.'
	exe = None
	try:
		obj = get_json_obj(data)
		doctype = obj.get('doctype')
		info = obj.get('info')

		name = info.get('name')
		filters = info.get('filters')

		if filters and not name:
			name = frappe.db.get_value(doctype, filters)
			if not name:
				res = 'No document found.'
		else:
			doc = frappe.get_doc(doctype, name)
			if not doc.has_permission("read"):
				res = 'No permission to read.'
			else:
				res = frappe.get_doc(doctype, name).as_dict()
	except Exception, e:
		exe = e

	return {
		'res': res,
		'exe': exe
	}


@frappe.whitelist()
def get_list(data):
	"""Returns list of document of the given DocType.

	:param data.doctype:DocType of documents to be fetched.
	:param data.info: Dict to facilitate list operation.
	"""
	res = 'Something went wrong.'
	exe = None
	try:
		obj = get_json_obj(data)
		doctype = obj.get('doctype')
		info = obj.get('info')

		print(info)
		fields = info.get('fields') or ['name']
		filters = info.get('filters') or None
		order_by = info.get('order_by') or None
		limit_start = info.get('start') or info.get('limit_start') or 1
		limit_page_length = info.get(
			'limit_page_length') or info.get('length') or 20
		ignore_permissions = info.get('ignore_permissions') or False

		res = frappe.get_list(doctype, fields=fields, filters=filters, order_by=order_by,
			limit_start=limit_start, limit_page_length=limit_page_length,
			ignore_permissions=ignore_permissions)

	except Exception, e:
		exe = e

	return {
		'res': res,
		'exe': exe
	}


@frappe.whitelist()
def get_meta(data):
	"""Returns meta of document of the given DocType.

	:param data.doctype:DocType of document.
	:param data.info: Dict to facilitate meta operation.
	"""
	res = 'Something went wrong.'
	exe = None
	try:
		obj = get_json_obj(data)
		doctype = obj.get('doctype')
		res = frappe.get_meta(doctype).as_dict()
	except Exception, e:
		exe = e

	return {
		'res': res,
		'exe': exe
	}


def get_json_obj(data):
	return json.loads(data.decode('string-escape').strip('"'))

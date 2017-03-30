from __future__ import unicode_literals
import datetime
import frappe
from frappe.utils.kickapp.helper import Helper
from frappe.utils.kickapp.utils import *
from frappe.utils.kickapp.query import Query


class Base(object):
	def __init__(self, obj):
		self.obj = obj
		self.bot_name = obj.bot_data.bot_name
		self.query = Query(obj.bot_data.bot_name)
		self.helper = Helper()

	def get_message(self, msg="Something went wrong, Please try in a little bit.", bot_data = None):
		obj = self.obj
		obj.created_at = self.get_created_at()
		obj.text = msg
		obj.chat_data = None
		obj.bot_data = self.get_bot_data() if bot_data is None else bot_data
		return obj

	def get_action_by_text(self, text):
		return self.query.get_action_from_text(text)

	def get_list(self, doctype, fields, filters):
		return self.helper.get_list(doctype, fields, 0, 3, filters)

	def get_created_at(self):
		return get_date(str(datetime.datetime.now()))

	def get_bot_data(self, base_action=None, button_text=None, 
		is_interactive_chat=False, is_interactive_list=False, items=[]):
		return {
			"bot_name":self.bot_name,
			"info":{
				"base_action": base_action,
				"button_text": button_text,
				"is_interactive_chat": is_interactive_chat,
				"is_interactive_list": is_interactive_list,
				"items": items
			}
		}

	def get_dummy_list(self, bot_name):
		return self.helper.get_dummy_list(bot_name)
	
	def add_or_update_and_return(self, params, method_name):
		doctype = params.doctype
		obj = params.obj
		item_id = params.item_id
		user_id = obj.meta.user_id
		filters = None
		is_success = False
		message = "Something went wrong, Please try in a little bit."
		try:
			item = obj.bot_data.info["items"][0]
			editables = [key for key in item.keys() if item[key]["is_editable"] == 1]
			if method_name == 'create_':
				note_doc = frappe.get_doc(Helper().get_dict(doctype, editables, item))
				note_doc.owner = user_id
				note_doc.insert()
				filters = {"name": note_doc.name, "owner": user_id}
			else:
				for key in editables:
					frappe.set_value(doctype, item_id, key, item[key]["fieldvalue"])
				filters = {"name": item_id, "owner": user_id}
			frappe.db.commit()
			is_success = True
		except Exception, e:
			print e
			message = '{0}'.format(str(e))
			filters = None
			is_success = False
		return frappe._dict({
			"is_success" : is_success,
			"filters": filters,
			"message": message
		})

class Basic_Bot(Base):
	def __init__(self, obj):
		Base.__init__(self, obj)
		self.bot_name = obj.bot_data.bot_name
		self.fields = self.helper.get_doctype_fields_from_bot_name(self.bot_name)
		self.messages = self.helper.get_messages_from_bot_name(self.bot_name)
		self.doctype = self.helper.get_doctype_name_from_bot_name(self.bot_name)
		self.item_id = obj.meta.item_id

	def get_results(self):
		print self.obj
		method = self.get_method()
		if method == 'error':
			return self.get_message("Something went wrong, please try a diffrent query")
		if method == 'cancel':
			return self.get_message("Last process cancelled")
		else:
			return getattr(self, method)()
	
	# def call_lower_class_methods(self, method_name, params):
	# 	if self.doctype == "Note":
	# 		return getattr(Note(), method_name)(params)
	# 	elif self.doctype == "ToDo":
	# 		return getattr(ToDo(), method_name)(params)
	
	def get_method(self):
		text = self.obj.text.lower()
		base_action = self.obj.bot_data.info.base_action
		if text == 'exit' or text == 'cancel':
			return 'cancel'
		elif base_action == 'create_':
			return 'create_'
		elif base_action is not None and self.item_id is not None:
			return base_action.lower()
		return self.get_action_by_text(text).lower()
	
	def get_params(self):
		return frappe._dict({
			"doctype":self.doctype,
			"obj":self.obj,
			"item_id" : self.item_id
		})
	
	#when user ask for creating new doc, return dummy list with metadata
	def create(self):
		bot_data = self.get_bot_data(base_action='create_', button_text='create',
			is_interactive_chat=True, items=self.get_dummy_list(self.bot_name))
		return self.get_message(self.messages.get('create'), bot_data = bot_data)

	def get(self):
		items = self.get_list(self.doctype, self.fields, filters={"owner": self.obj.meta.user_id})
		bot_data = self.get_bot_data(button_text='load more', is_interactive_list=True, 
			items=self.helper.get_mapped_list(self.bot_name, items))
		return self.get_message(self.messages.get('get'), bot_data = bot_data)
	
	#when base_action is create_ then we actually create new doc in doctype
	def create_(self):
		data =  self.add_or_update_and_return(self.get_params(), 'create_')
		if data.is_success:
			items = self.get_list(self.doctype, self.fields, data.filters)
			bot_data = self.get_bot_data(button_text='view info', is_interactive_chat=True, 
				items=self.helper.get_mapped_list(self.bot_name, items))
			return self.get_message(self.messages.get('create_'), bot_data = bot_data)
		return self.get_message(msg = data.message)

	def update_(self):
		data =  self.add_or_update_and_return(self.get_params(), 'update_')
		if data.is_success:
			items = self.get_list(self.doctype, self.fields, data.filters)
			bot_data = self.get_bot_data(button_text='view info', is_interactive_chat=True, 
				items=self.helper.get_mapped_list(self.bot_name, items))
			return self.get_message(self.messages.get('update_'), bot_data = bot_data)
		return self.get_message(msg = data.message)

	def delete_(self):
		filters = {"name": self.item_id, "owner": self.obj.meta.user_id}
		try:
			items = self.get_list(self.doctype, self.fields, filters)
			if len(items) > 0:
				frappe.delete_doc(self.doctype, self.item_id)
				frappe.db.commit()
				return self.get_message(self.messages.get('delete_'),
				 	bot_data = self.get_bot_data())
			else:
				return self.get_message("Looks like item already deleted from database.")
		except Exception, e:
			print e
			return self.get_message()

from __future__ import unicode_literals
import frappe
import re
import frappe.utils
from frappe import _
from frappe.utils.kick.constant import *


class Query(object):

	def __init__(self, query):
		self.query = query
		self.process_query()
		self.filters = None
		self.sql_where = None

	def starts_with(self, words):
		words = self.convert_words_to_local_lang(words)
		for w in words:
			if self.query.startswith(w):
				return True
		return False
	
	def ends_with(self, words):
		words = self.convert_words_to_local_lang(words)
		for w in words:
			if self.query.endswith(w):
				return True
			return False

	def has(self, words):
		words = self.convert_words_to_local_lang(words)
		for w in words:
			if w in self.query:
				return True
		return False

	def convert_words_to_local_lang(self, words):
		return[_(x) for x in words]

	def strip_words(self, words):
		return (' '.join(filter(lambda x: x.lower() not in words,
								self.query.split()))).strip()

	def process_query(self):
		self.remove_startswith()
		self.remove_endswith()

	def remove_endswith(self):
		self.query = self.query[:-1] if self.query.endswith("?") else self.query
		self.query = self.query[:-1] if self.query.endswith(".") else self.query
		self.query = self.query[:-1] if self.query.endswith(";") else self.query
		self.query = self.query[:-1] if self.query.endswith(":") else self.query
		self.query = self.query[:-1] if self.query.endswith('"') else self.query

	def remove_startswith(self):
		self.query = self.query[:-1] if self.query.startswith("?") else self.query
		self.query = self.query[:-1] if self.query.startswith(".") else self.query
		self.query = self.query[:-1] if self.query.startswith(";") else self.query
		self.query = self.query[:-1] if self.query.startswith(":") else self.query
		self.query = self.query[:-1] if self.query.startswith('"') else self.query

	def get_action_from_text(self, params):
		action = None
		if self.starts_with(['cancel', 'abort', 'dump']):
			action = action.CANCEL
		elif params.info.action == actions.SHOW or self.starts_with(['show', 'open', 'list', 'get', 'find']):
			action = actions.SHOW
		# elif params.info.action == actions.CREATE or self.starts_with(['add', 'create', 'new', 'post']):
		# 	action = actions.CREATE
		# elif params.info.action == actions.DELETE or self.starts_with(['remove', 'trash', 'delete', 'dump']):
		# 	action = actions.DELETE
		# elif params.info.action == actions.UPDATE or self.starts_with(['update', 'put', 'refresh']):
		# 	action = actions.UPDATE
		elif self.starts_with(['hello', 'hi', 'how', 'hey', 'yo', 'goodbye', 'how are you doing', 'whats', "what's", 'bye'
			'how are you', 'who are you', 'what do you do', 'what you can do', 'tell a story']):
			action = actions.BASIC
		elif self.starts_with(['how many', 'count']):
			action = actions.COUNT
		else:
			action = actions.DEFAULT
		return action
	
	def get_filters(self, doctype):
		#prepare filter for text after where
		x = self.query.split('where')
		if len(x) > 1:
			x = x[1]
			#split by [and or && || & | ,]
			filters = self.split_and_get_filtes(x, "and|\&|\&&", "or|\||\,|\||", is_and = True)
			filters = self.split_and_get_filtes(x, "or|\||\,|\||", "and|\&|\&&")

		#key:value
		#get all fields matching query
		# xx = filter(lambda x: x[0] in self.query or x[1] in self.query, 
		# 	[(d.fieldname.lower(), d.fieldtype.lower()) for d in doctype_field_names])
		# #now get value
		# splited_query = self.query.split(',')
		# for y in splited_query:
		# 	z = y.split(':')
		# 	key = z[0].split(' ')
		# 	if len(z) > 1:
		# 		_filter[key[0].trim()] = z[1].trim()
	
	def split_and_get_filtes(self, query, real_regex, dummy_regex, is_and=False):
		#first split using real_regex will remove all none or empty substring
		yy = filter(None, re.split(real_regex, query))
		xx = []
		for y in yy:
			#string at 0 index is our filter
			xx.append(filter(None, re.split(dummy_regex, y))[0])
		
		dict_string = "{ "
		(", ").join(,[x for x in xx]))
		for x in xx:
			x.strip()
			x = x.replace("=", ":")
			x = x.replace("is", ":")
			x = x.replace("equal", ":")
			dict_string += x		
		dict_string += " }"










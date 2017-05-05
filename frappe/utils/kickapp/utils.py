from __future__ import unicode_literals
import frappe
import json
import datetime


def save_message_in_database(chat_room, chat_type, room, obj):
	if chat_room is None:
		chat_room = create_and_save_room_object(room, chat_type)
	return create_and_save_message_object(chat_room, obj)


def create_and_save_room_object(room, chat_type):
	doc = frappe.new_doc('Chat Room')
	doc.room_name = room
	doc.chat_type = chat_type
	doc.save()
	frappe.db.commit()
	return doc.name


def create_and_save_message_object(chat_room, obj):
	doc = frappe.new_doc('Chat Message')
	doc.chat_room = chat_room
	for key, value in obj.items():
		if key == 'meta' or key == 'communication':
			continue
		elif key == 'created_on':
			doc.set('created_at', str(value + '.123456'))
		elif key == 'chat_data':
			doc.set(key, json.dumps(value))
		else:
			doc.set(key, value)
	doc.save()
	frappe.db.commit()
	return [doc]


def create_and_save_user_object(chat_room, user):
	doc = frappe.new_doc('Chat User')
	doc.chat_room = chat_room
	for key, value in user.items():
		doc.set(key, value)
	doc.save()
	frappe.db.commit()

def format_response(chats):
	results = []
	for chat in chats:
		item = {
			"created_on": get_date(chat.created_at),
			"text": chat.text,
			"chat_data": json.loads(chat.chat_data),
			"communication": None,
		}
		results.append(item)
	return results

def format_communication_response(text, created_at, communication):
	return {
		"created_on": get_date(created_at),
		"text": text,
		"chat_data": None,
		"communication": communication
	}

def map_chat(room, chat_type, chats, name=None):
	return {
		"meta": {
			"room": room,
			"chat_type": chat_type,
			"users": get_users(chat_type, name) if name else [],
			"owner": get_owner(chat_type, name) if name else None
		},
		"chat_items":chats
	}

def get_date(created_at):
	created_on = str(created_at)
	return created_on.split('.')[0]

# def dump_to_json(res):
# 		res.chat_data = json.dumps(res.chat_data)
# 		res.communication = json.dumps(None)
# 		return [res]

def get_users(chat_type, name):
	if chat_type == "personal":
		return frappe.get_list('Chat User', ["title", "email"], filters={"chat_room": name})
	return []

def get_owner(chat_type, name):
	if chat_type == "group":
		return frappe.get_doc('Chat Room', name).owner
	return None

def get_room(owner, raised_by):
	if(owner > raised_by):
		return owner + raised_by
	return raised_by + owner




# def get_item_as_dict(fields, item):
# 	obj = {}
# 	fields_list = fields.split(',')
# 	for index in range(len(fields_list)):
# 		value = item[index]
# 		if isinstance(value, datetime.datetime):
# 			value = get_date(value)
# 		obj[fields_list[index].strip()] = value
# 	return obj

# def get_items_from_array(items):
# 	results = []
# 	if items:
# 		for item in items:
# 			results.append(get_object_from_key_value(item.keys(), item))
# 	print results
# 	return results

# def get_object_from_key_value(keys, item):
# 	obj = {}
# 	for key in keys:
# 		if isinstance(item[key], datetime.datetime):
# 			obj[key] = get_date(item[key])
# 		else:
# 			obj[key] = item[key]
# 	return obj

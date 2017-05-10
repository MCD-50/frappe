from __future__ import unicode_literals
import frappe
import json
import datetime


def save_message_in_database(chat_room, chat_type, room, obj):
	if chat_room is None:
		chat_room = create_and_save_room_object(room, chat_type)
	return create_and_save_message_object(chat_room, obj)


def create_and_save_room_object(room, chat_type, for_communication = 0):
	doc = frappe.new_doc('Chat Room')
	doc.room_name = room
	doc.chat_type = chat_type
	doc.for_communication = for_communication
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

def format_communication_response(communications, issue):
	results = []
	for communication in communications:
		item = {
			"issue": json.loads(issue),
			"communications": json.loads(communications)
		}
		results.append(item)
	return results

# def create_communication(sender, sender_full_name, recipients, subject, content, status, attachment, communication_date)

def map_chat(room, chat_type, chats, name=None, users = []):
	return {
		"meta": {
			"room": room,
			"chat_type": chat_type,
			"users": get_users(chat_type, name) if name else users,
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

def set_customer_with_contact_in_room(email):
	contact_list = frappe.db.sql('''select c.email_id, dl.link_name
		from `tabDynamic Link` dl, `tabContact` c 
		where c.name=dl.parent and dl.link_doctype="Customer" and dl.parenttype="Contact"
		''')
	from collections import defaultdict
	__contact_list = defaultdict(list)
	
	for __k, __v in contact_list:
		__contact_list[__k].append(__v)
	
	for __k, __v in __contact_list:
		room =  get_room(email, __k)
		chat_room = frappe.db.exists('Chat Room', {"chat_room":room})
		if chat_room is None:
			chat_room = create_and_save_room_object(room, 'group', for_communication = 1)
			for v in __v:
				user_data = frappe.db.exists("Chat User", {"email": v, "chat_room": chat_room})
				if user_data is None:
					title = frappe.db.sql("""select first_name, last_name 
						from `tabContact` where email_id = %s""", v)
					x = {"email":v, "title": get_title(title[0])}
					create_and_save_user_object(chat_room, x)


def get_users(chat_type, name):
	if chat_type == "personal":
		return frappe.get_list('Chat User', ["title", "email"], filters={"chat_room": name})
	return []

def get_communication_users(email, raised_by):
	users = []
	# user = frappe.get_list('User', ["full_name"], filters={"email": email})
	# raised_by_user = frappe.get_list('Lead', ["lead_name"], filters={"email_id": raised_by})

	# if raised_by_user is None or len(raised_by_user) < 1:
	# 	raised_by_user = frappe.get_doc('Contact', frappe.get_list('Contact', ["name"], filters={"email_id": raised_by_user})[0].name)
	# 	link = filter(lambda x : x.link_doctype == 'Customer', raised_by_user.links)[0]
	# 	raised_by_user = frappe.get_doc('Customer', link.link_name)
	# 	users.append({"title":raised_by_user.customer_name, "email":raised_by})
	# else:
	# 	users.append({"title":raised_by_user[0].lead_name, "email":raised_by})
	
	# if user and len(user) > 0:
	# 	users.append({"title":user[0].full_name, "email":email})
	return users


def get_owner(chat_type, name):
	if chat_type == "group":
		return frappe.get_doc('Chat Room', name).owner
	return None

def get_room(owner, raised_by):
	if(owner > raised_by):
		return owner + raised_by
	return raised_by + owner

def get_title(title_tuple):
	if len(title_tuple) > 1:
		return title_tuple[0] + " " +title_tuple[1]
	return title_tuple[0]

def create_communications():
	pass

def create_issues():
	pass

def merge_issues_communications_for_customer():
	pass

def merge_issues_communications_for_lead():
	pass


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

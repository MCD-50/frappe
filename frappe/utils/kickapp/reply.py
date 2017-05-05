from __future__ import unicode_literals
import frappe
from frappe.utils.kickapp.helper import *
from frappe.utils.kickapp.engine import Engine
from frappe.utils.kickapp.utils import *
from frappe.desk.form.load import get_communications, get_communication_data
import json
import html2text

class Reply(object):
	def __init__(self):
		self.helper = Helper()

	def get_users(self, obj):
		""" return 20 users at a time """
		start = (int(obj.page_count) - 1) * 20
		return frappe.get_list('User', ["name", "email", "full_name", "last_active", "bio"],
			limit_start=start, limit_page_length= 20)

	def get_user_by_email(self, obj):
		""" return single user info based on email"""
		return frappe.get_list('User', ["name", "email", "full_name", "last_active", "bio"],
			filters={"email": str(obj.email)})
	
	def get_users_in_room(self, obj):
		""" return all users in a room"""
		chat_room = frappe.db.exists("Chat Room", {"room_name": str(obj.room)})
		if chat_room:
			return frappe.get_list('Chat User', ["title", "email"], filters={"chat_room": chat_room})
		return []

	def set_users_in_room(self, obj):
		""" set users in room"""
		chat_room = frappe.db.exists("Chat Room", {"room_name": str(obj.room)})
		if chat_room is None:
			chat_room = create_and_save_room_object(str(obj.room), obj.chat_type)

		for user in obj.users:
			#convert to dict
			x = frappe._dict(user)
			user_data = frappe.db.exists("Chat User", {"email": x.email, "chat_room": chat_room})
			if user_data is None:
				create_and_save_user_object(chat_room, x)
		return 'Added Users'
	
	def remove_user_from_group(self, obj):
		""" remove user from group"""
		chat_room = frappe.db.exists("Chat Room", {"room_name": str(obj.room)})
		
		if chat_room:
			user_data = frappe.db.exists("Chat User", {"email": str(obj.email), "chat_room": chat_room})
			"""this is the best way to remove user from group""" 
			if user_data:
				frappe.delete_doc('Chat User', user_data)
				frappe.db.commit()
		return 'Removed Users'
	
	def get_issues_for_user(self, obj):
		""" publish emails when user open the contact"""
		message = []
		issue_list = frappe.get_list('Issue', ["name", "raised_by", "subject", "status", "description", 
			"customer_name", "company", "customer", "contact"], filters= {"raised_by":str(obj.email)})
		
		for issue in issue_list:
			#react native does not support html
			issue.subject =  html2text.html2text(issue.subject)
			issue.description =  html2text.html2text(issue.description)
			
			communications = self.get_communications_recursively('Issue', issue.name, 0, 20, communications= [], after = None)
			
			for c in communications:
				c.subject = html2text.html2text(c.subject) if c.subject else None
				c.content = html2text.html2text(c.content) if c.content else None
			
			if len(communications) > 0:
				message.append(map_chat(format_communication_response(issue.description, communications[len(communications) - 1].creation, 
					communications), str(obj.room), 'personal', 'communication', subject= issue.subject, raised_by=issue.raised_by))
		
		return message
	
	def get_communications_recursively(self, doctype, name, limit_start, length, communications= [], after = None):
		"""get get_communication_data returns only 20 items at a time"""
		x = get_communication_data(doctype, name, limit_start, length, after)
		
		if len(x) > 0:
			for c in x:
				if c.communication_type=="Communication":
					c.attachments = json.dumps(frappe.get_all("File", fields=["file_url", "is_private"],
					filters={"attached_to_doctype": "Communication", "attached_to_name": c.name}))
				
				elif c.communication_type=="Comment" and c.comment_type=="Comment":
					c.content = frappe.utils.markdown(c.content)

			communications += x

			if len(x) > 19:
				return self.get_communications_recursively(doctype, name, limit_start + 20, length, communications, after)
		return communications

	# def load_more(self, query):
	# 	return Engine().load_more(query)

	# def load_items(self, query):
	# 	return Engine().load_items(query)

	# def get_all_bots(self):
	# 	items = self.helper.get_list('Chat Bot', 
	# 		self.helper.get_doctype_fields_from_bot_name('Chat Bot'), get_all=True)
	# 	for item in items:
	# 		item.commands = json.loads(item.commands)
	# 	return items
	
	def get_messages(self, obj):
		""" publish message when user first open the app"""
		self._get_messages([], str(obj.email), obj.rooms, obj.last_message_times, 0, 40)

	def _get_messages(self, message, email, rooms, last_message_times, limit_start, limit_page_length):
		""" publish message in blocks of 40"""
		room_list = frappe.get_list('Chat Room', ["name", "room_name", "chat_type"], limit_start=limit_start, limit_page_length=limit_page_length)
		
		while(room_list is not None):
			for room in room_list:
				user_data = user_data = frappe.db.exists("Chat User", {"email": email, "chat_room": room.name})
				
				if user_data:
					filters = {"chat_room":room.name}
					index = -1
					try:
						index = rooms.index(room.room_name)
					except Exception, e:
						index = -1
					if index > -1:
						last_message_time = last_message_times[index]
						
						if last_message_time:
							last_message_time = str(str(last_message_time) + '.123456')
							filters = {"chat_room":room.name, "created_at":(">", last_message_time)}
					
					items = format_response(frappe.get_list('Chat Message', ["name", "created_at", "text", "chat_data"], filters=filters))
					if len(items) > 0:
						message.append(map_chat(room.room_name, room.chat_type, items, room.name))

			frappe.publish_realtime(event='message_from_server', message=message, room=email)
			
			if len(room_list) > 39:
				limit_start = limit_start + 40
				room_list = frappe.get_list('Chat Room', ["name", "room_name", "chat_type"], limit_start=limit_start, limit_page_length=limit_page_length)
			else:
				room_list = None
		self._get_issues([], email, 0, 40)

	def _get_issues(self, message, email, limit_start, limit_page_length):
		issue_list = frappe.get_list('Issue', ["name", "raised_by", "subject", "status", "description", 
				"customer_name", "company", "customer", "contact"], limit_start=limit_start, limit_page_length=limit_page_length)

		while(issue_list is not None):
			for issue in issue_list:
				#react native does not support html
				issue.subject =  html2text.html2text(issue.subject) if issue.subject else None
				issue.description =  html2text.html2text(issue.description) if issue.description else None

				"""
				reference_owner: creator
				reference_doctype: name of doctype for which communication is created 
				reference_name:name of doctype item for which communication is created 
				reference_user: email id of user who raised the communication
				"""

				communications = self.get_communications_recursively('Issue', issue.name, 0, 20, communications= [], after = None)
				
				for c in communications:
					c.subject = html2text.html2text(c.subject) if c.subject else None
					c.content = html2text.html2text(c.content) if c.content else None

				if len(communications) > 0:
					communication_response = format_communication_response(issue.description, communications[len(communications) - 1].creation, communications)
					message.append(map_chat(communication_response, get_room(email, issue.raised_by), 'personal', 'communication', subject= issue.subject, raised_by=issue.raised_by))
			
			frappe.publish_realtime(event='message_from_server', message=message, room=email)

			if len(issue_list) > 39:
				limit_start = limit_start + 40
				issue_list = frappe.get_list('Issue', ["name", "raised_by", "subject", "status", "description", 
					"customer_name", "company", "customer", "contact"], limit_start=limit_start, limit_page_length=limit_page_length)
			else:
				issue_list = None


	def send_message(self, obj):
		""" publish message"""
		items = []
		chats = []

		chat_room = frappe.db.exists("Chat Room", {"room_name": str(obj.meta.room)})
		
		if chat_room is None:
			chat_room = create_and_save_room_object(str(obj.meta.room), str(obj.meta.chat_type))
		
		if obj.meta.add:
			items = save_message_in_database(chat_room, str(obj.meta.chat_type), 
				str(obj.meta.room), obj)
		
		if str(obj.meta.chat_type) == "communication":
			"""add some function here to send message"""
			"Todo"

		else:
			users = [i for i in frappe.get_list('Chat User', ["email"], filters={"chat_room":chat_room}) if i.email != str(obj.meta.email)]
			for user in users:
				chat_response = format_response(items)
				chats.append(map_chat(str(obj.meta.room), str(obj.meta.chat_type), chat_response, chat_room))
				frappe.publish_realtime(event='message_from_server', message=chats, room= user.email)


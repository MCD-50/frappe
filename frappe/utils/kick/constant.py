from __future__ import unicode_literals
import frappe, re
from random import randint

action_mapper = {"create":"create_doc", "update":"update_doc",
	"delete":"delete_doc", "show":"get_doc", "basic":"basic_replies", 
	"count":"count_docs", "default":"error_message", "cancel":"cancel_message"}

actions = frappe._dict({d.upper():d.lower() for d in action_mapper.keys()}) 

delemiters = {
	"and": ['and', '&', '&&'],
	"or":['or', '||', '|', ',']
}

GREETING_KEYWORDS = ["hello", "hi", "greetings", "sup", "what's up", "good morning", "good evening", "good night"]
BYE_KEYWORDS= ["bye", "goodbye", "bi", "see ya", "see you"]

GREETING_RESPONSES = ["sup bro", "hey", "*nods*", "doing good", "awesome"]
BYE_RESPONSES= ["bye", "goodbye"]




def get_method_name_from_action(action):
	return action_mapper.get(action.lower(), None)






import string
import time
import random
from typing import Text, List, Any, Dict, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, FollowupAction, AllSlotsReset, EventType, UserUttered, ConversationPaused, UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

import json
import requests

#import helpers
from fuzzywuzzy import process
# TODO: Figure out why I cannot import local .py files

def question_db():
    # TODO: Turn this into a external database. Turn this function into DB query
    questions_dict = {
    "2_fractions_halves_mcq_1": ["mcq_match", ['a','b','c','d'], 'b'],
    "3_fractions_halves_frq_1": ["frq_keyword_match", ["equal", "halves", "half", "same", "identical"], None],
    "3_fractions_parts_mcq_1" : ["nrq_fractions", ["1/3", "2/6"]],
    "4_fractions_parts_mcq_2": ["frq_keyword_match", ["more", "greater"], ["less", "fewer"]],
    "2_fractions_parts_nrq_1": ["nrq_numeral", [2]],
    "5_fractions_parts_mcq_3": ["frq_keyword_match", ["less", "fewer"], ["more", "greater", "big", "bigger"]],
    "6_fractions_parts_mcq_4": ["frq_keyword_match", ["more", "greater"], ["less", "fewer"]],
    "1_fractions_wholes_nrq_1": ["nrq_numeral", [4]],
    "2_fractions_wholes_nrq_2": ["nrq_fractions", ["1/3", "2/6"]],
    "3_fractions_wholes_frq_1": ["frq_keyword_match", ["box", "4"], None],
    "4_fractions_wholes_nrq_3": ["nrq_numeral", [1]],
    "5_fractions_wholes_nrq_4": ["nrq_fractions", ["1/4"]],
    "6_fractions_wholes_nrq_5": ["nrq_fractions", ["1/6"]],
    }
    return questions_dict

def slotInDomain(slot_name, domain):
    # Returns a boolean 
    return slot_name in domain.get('slots')

def extractFraction(tracker):
    # Error handle exceptions 
    try:
        for entity_dict in tracker.latest_message.get('entities'):
            if entity_dict.get('entity') == 'number':
                return entity_dict.get('text')
        return None
    except:
        print("AN ERROR in EXTRACT FRACTION OCCURED!")
        return None

def matchOption(user_input, slot_name, cutoff=60):
    # TODO: Turn this into an external database
    resp = user_input.lower()
    options_dict = {
    "1_object_2": ["option_match", ["badams", "biscuits", "grapes", "chocolates"]]
    }
    option_matching_method = options_dict[slot_name][0]
    # Fuzzy match strings and returns closest match result to list of options
    if option_matching_method =="option_match":
        options = options_dict[slot_name][1]
        result = process.extractOne(resp, options, score_cutoff=cutoff)
        if result:
            return result[0]
        else:
            return None 

def hintsExceed(question, tracker):
    hint_name = f'{question}_list'
    print(f"Hint name = {hint_name}")
    hint_list = tracker.get_slot(hint_name)
    return hint_list[0] >= len(hint_list)

def checkQuestion(user_input, question, tracker=None):
    """ 
    Takes in the expected user input, queries DB, 
    and validates the user input against the question
    Returns:
    'CORRECT' : matches the validator for the question type
    'INCORRECT': classified as invalid 
    None if invalid input
    """

    questions_dict = question_db()
    q_list = questions_dict[question]
    question_type = q_list[0]

    if not user_input:
        return None

    if question_type == "nrq_fractions":
        if user_input > 0 and user_input <= 1:
            text_fraction = extractFraction(tracker)
            if text_fraction:
                if text_fraction in q_list[1]:
                    return "CORRECT"                
                else:
                    return "INCORRECT"
        
    if question_type == "nrq_numeral":
        for ans_option in q_list[1]:
            if user_input == ans_option:
                return "CORRECT"
            return "INCORRECT"

    # Returns exact match to options i.e 'A, B, C, D' 
    if question_type=="mcq_match":
        resp = user_input.lower()
        options = q_list[1]
        if resp in options:
            if resp == q_list[2]:
                return "CORRECT"
            else:
                return "INCORRECT"
    # Checks free text input if it contains list 1 and does not contain words for list 2
    if question_type == "frq_keyword_match":
        # Turn this into a seperate method for FRQs
        resp = user_input.lower()
        resp_words = resp.split()
        keywords = q_list[1] 
        if any(word in keywords for word in resp_words):
            not_words = q_list[2]
            if not_words:
                if any(word in not_words for word in resp_words):
                    return None # Included words in both lists
            return "CORRECT"
        else:
            return "INCORRECT"

def respondQuestion(answer, question, slot_value, dispatcher, tracker=None, domain=None):
    slot_dict_input = None
    if answer == "CORRECT":
        dispatcher.utter_message(response="utter_correct")
        slot_dict_input = slot_value
    if answer == "INCORRECT":
        # Checks if a hint slot is there and if there is if it exceeds
        if domain and hintsExceed(question, tracker):
            # Standard case for exceeding hints
            slot_dict_input = 'EXCEEDED'
            dispatcher.utter_message(response ="utter_keep_going")
            dispatcher.utter_message(response =f'utter_{question}_solution')
        else:
            dispatcher.utter_message(response ="utter_incorrect")
            slot_dict_input = None
    if not answer:
        print(f"Failed to extract slot for {question} - Extracted: {slot_value}")
        dispatcher.utter_message("I couldn't understand your input!")
        slot_dict_input = None
    # Automatically search for explanation

    if slot_dict_input:
        explanation_response = f"utter_{question}_explanation"
        dispatcher.utter_message(response = explanation_response)
    return slot_dict_input

def extractFirstElementfromSlot(slot_value):
    if slot_value:
        if isinstance(slot_value, list):
            return slot_value[0]
        else:
            return slot_value
    return None

def extractName(slot_value, tracker):

    """ Take in the slot value extracted using slot mapping 'from_text' 
    extracts name, and if cannot find returns None"""
    name_entity = next(tracker.get_latest_entity_values("name"), None)
    PERSON_entity = next(tracker.get_latest_entity_values("PERSON"), None)
    resp_words = slot_value.split()
    if name_entity:
        return name_entity.capitalize()    
    if PERSON_entity:
        return PERSON_entity.capitalize()
    if len(resp_words) == 1:
        return resp_words[0].capitalize()
    return None

def rocketChatHandoffAPIcall(tracker):
    # Hardcoding the RocketChat LiveChat Link - change for robust handling 
    url = "https://eccechat.me/api/apps/public/646b8e7d-f1e1-419e-9478-10d0f5bc74d9/incoming"
    api_call = {
        "action":"handover",
        "sessionId": tracker.sender_id,
        "actionData": {
        "targetDepartment": "Human-Handoff"
        }
    }
    json_blob = json.dumps(api_call)
    response = requests.post(url, data=json_blob)
    return response.ok

def previousAction(tracker, action_num=1):
    """ Returns a string of the previous action Not NONE, or action_list. 
    Does not consider the action/event from which this function is being called.
    Args: action_num=1 is how far back to look
    """
    counter = 0
    event_list = [] 
    for event in reversed(tracker.events):
        if event.get('name') not in [ 'action_listen', None] and '_form' not in event.get('name'):
            return event.get('name')
        else :
            pass
    return event_list

# Fallback actions 

class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue
    
    Called when core very confused, OR two-stage-fallback final triggered
    """

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        fallback_message = ""
        events = [UserUtteranceReverted()]        
        print(previousAction(tracker))
        if previousAction(tracker) == self.name():
            events.append(FollowupAction(name="action_handoff"))
        else:
            dispatcher.utter_message(text="I'm sorry, I can't understand. Could you please rephrase?")
        return events

class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    async def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # the session should begin with a `session_started` event and an `action_listen`
        # as a user message follows
        return [SessionStarted(), ActionExecuted("action_listen")]

class ActionHandoff(Action):
   def name(self) -> Text:
       return "action_handoff"
 
   async def run(
       self,
       dispatcher: CollectingDispatcher,
       tracker: Tracker,
       domain: Dict[Text, Any],
   ) -> List[EventType]:
        print(f"INPUT CHANNEL: {tracker.get_latest_input_channel()}")
        if not rocketChatHandoffAPIcall(tracker):
            dispatcher.utter_message(text = "Something went wrong. So it is just you an me!")
        return []

class ActionCheckUserStatus(Action):

    def name(self) -> Text:
        return "action_check_user_status"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # TODO: Query Internal Postgres DB for past interaction
        if tracker.get_slot("userName"):
            return [SlotSet("is_new_user", False)]
        else:
            return [SlotSet("is_new_user", True)]

class ActionGoodbye(Action):
    def name(self) -> Text:
        return "action_goodbye"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:  
        if tracker.get_slot("userName"):
            dispatcher.utter_message(response = "utter_goodbye")
        else:
            dispatcher.utter_message(text= "Bye!")
        
        persistent_slots = ["userName", "is_new_user"]
        events = [AllSlotsReset()]
        for key in persistent_slots:
            events.append(SlotSet(key=key, value=tracker.get_slot(key)))
        events.append(FollowupAction("action_listen")) 
        return events

class ActionFailedFirstTimeForm(Action):

    def name(self) -> Text:
        return "action_failed_first_time_form"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("Sorry I didn't get your information right. Lets try this again!")
        return [SlotSet(key = "userName", value = None), SlotSet(key = "age", value = None) ]

class ActionAskPartsObject2(Action):
    def name(self) -> Text:
        return "action_ask_fractions_parts_story_form_1_object_2"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if tracker.get_slot('1_friend_1'):
            dispatcher.utter_message(response="utter_fractions_parts_story_form_1_object_2")
            return []
        else:
            print("IF FLASE")
            dispatcher.utter_message(response="utter_fractions_parts_story_form_1_object_2", friend_1 = "Puja")
            return [SlotSet("1_friend_1", "Puja")]

class ValidateFirstForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_first_form"
    
    def validate_userName(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        name = extractName(slot_value, tracker)
        if name:
            return {"userName":name}
        else:
            dispatcher.utter_message(text="Sorry I missed that! Can you give me just your first name?")
            return {"userName": None}
    
class ValidateFractionHalvesStoryForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fractions_halves_story_form"
    
    # async def required_slots(
    #     self,
    #     slots_mapped_in_domain: List[Text],
    #     dispatcher: "CollectingDispatcher",
    #     tracker: "Tracker",
    #     domain: "DomainDict",
    # ) -> Optional[List[Text]]:
    #     additional_slots = ["3_3_fractions_halves_frq_1"]
        
    #     if tracker.slots.get("2_fractions_mcq_1") == "B":
    #         # If the user wants to sit outside, ask
    #         # if they want to sit in the shade or in the sun.
    #         additional_slots.append("3_3_fractions_halves_frq_1")
    #     else:

    #     return additional_slots + slots_mapped_in_domain
    
    # TODO: Change once you understand how to deal with a non extracted entity
    def validate_1_friend_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        defualt_name = "Puja"
        name = extractName(slot_value, tracker)
        if name:
            return {"1_friend_1":name}
        else:
            dispatcher.utter_message(f"I can't find the name! Lets call your friend {defualt_name} for now!")
            return {"1_friend_1": defualt_name}

    def validate_2_fractions_halves_mcq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name = "2_fractions_halves_mcq_1"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, tracker, domain)     
        return {question_name:slot_dict_input}

    def validate_3_fractions_halves_frq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name = "3_fractions_halves_frq_1"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name: slot_dict_input}

class AskFor2FractionsHalvesMcq1(Action):
    def name(self) -> Text:
        return "action_ask_2_fractions_halves_mcq_1"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        slot_name = "2_fractions_halves_mcq_1"
        hint_name = f"{slot_name}_list"
        hint_list = tracker.get_slot(hint_name) # TODO: add a check if this slot is defined
        print(f"HINT LIST : {hint_list}")
        hint_number = hint_list[0]
        if hint_number < len(hint_list): #No. attemps < No. Hints
            if hint_number == 0:
                # First time being asked the question
                dispatcher.utter_message(response= f'utter_question_{slot_name}')
            else: 
                # TODO: Add a check to see if the slot was a valid answer 
                dispatcher.utter_message(text = hint_list[hint_number])
            hint_list[0] += 1 # Increment hint counter
            return [SlotSet(hint_name, hint_list)]
        else: 
            print("SOMETHING HAS GONE WRONG -  No. Attemps > No. Hints")
            return []

class ValidateFractionPartsStoryForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fractions_parts_story_form"

    def validate_1_object_2(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        match = matchOption(slot_value, "1_object_2")
        if match:
            return{"1_object_2": match}
        else:
            dispatcher.utter_message(response= "utter_wrong_format", err= "That is not an option, choose again!!")
            return{"1_object_2": None}

    def validate_2_fractions_parts_nrq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "2_fractions_parts_nrq_1"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name: slot_dict_input}
    
    def validate_3_fractions_parts_mcq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name = "3_fractions_parts_mcq_1"
        answer = checkQuestion(slot_value, question_name, tracker=tracker)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name: slot_dict_input}


    def validate_4_fractions_parts_mcq_2(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name =  "4_fractions_parts_mcq_2"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name:slot_dict_input}

    def validate_5_fractions_parts_mcq_3(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name =  "5_fractions_parts_mcq_3"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name:slot_dict_input}
    
    def validate_6_fractions_parts_mcq_4(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name =  "6_fractions_parts_mcq_4"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name:slot_dict_input}

class ValidateFractionWholesStoryForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fractions_wholes_story_form"
    
    def validate_1_fractions_wholes_nrq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
         
        question_name = "1_fractions_wholes_nrq_1"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name: slot_dict_input}
    
    def validate_2_fractions_wholes_nrq_2(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "2_fractions_wholes_nrq_2"
        answer = checkQuestion(slot_value, question_name, tracker=tracker)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name: slot_dict_input}
    
    def validate_3_fractions_wholes_frq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "3_fractions_wholes_frq_1"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name: slot_dict_input}    
    
    def validate_4_fractions_wholes_nrq_3(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "4_fractions_wholes_nrq_3"
        answer = checkQuestion(slot_value, question_name, tracker=tracker)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name: slot_dict_input}
    
    def validate_5_fractions_wholes_nrq_4(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "5_fractions_wholes_nrq_4"
        answer = checkQuestion(slot_value, question_name, tracker=tracker)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name: slot_dict_input}
    
    def validate_6_fractions_wholes_nrq_5(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "6_fractions_wholes_nrq_5"
        answer = checkQuestion(slot_value, question_name, tracker=tracker)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        return {question_name: slot_dict_input}


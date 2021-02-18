import string
import time
from typing import Text, List, Any, Dict, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

#import helpers
from fuzzywuzzy import process
# TODO: Figure out why I cannot import local .py files
def question_db():
    # TODO: Turn this into a external database. Turn dict into DB query
    questions_dict = {
    "fractions_halves_mcq_1": ["mcq_match", ['a','b','c','d'], 'b'],
    "fractions_halves_frq_1": ["frq_keyword_match", ["equal", "halves", "half", "same", "identical"], None],
    "fractions_parts_mcq_1" : ["nrq_fractions", ["1/3", "2/6"]],
    "fractions_parts_mcq_2": ["frq_keyword_match", ["more", "greater"],  ],
    "fractions_parts_nrq_1": ["nrq_numeral", [2]],
    "fractions_parts_mcq_3": ["frq_keyword_match", ["less", "fewer"], ["more", "greater", "big", "bigger"]],
    "fractions_parts_mcq_4": ["frq_keyword_match", ["more", "greater"], ["less", "fewer"]],
    "fractions_wholes_nrq_1": ["nrq_numeral", [4]],
    "fractions_wholes_nrq_2": ["nrq_fractions", ["1/3", "2/6"]],
    "fractions_wholes_frq_1": ["frq_keyword_match", ["box", "4"], None],
    "fractions_wholes_nrq_3": ["nrq_numeral", [1]],
    "fractions_wholes_nrq_4": ["nrq_fractions", ["1/4"]],
    "fractions_wholes_nrq_5": ["nrq_fractions", ["1/6"]],
    }
    return questions_dict

class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    async def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        metadata = tracker.get_slot("session_started_metadata")
        # Do something with the metadata
        print(metadata)
        # the session should begin with a `session_started` event and an `action_listen`
        # as a user message follows
        return [SessionStarted(), ActionExecuted("action_listen")]

def extractFraction(tracker):
    # Error handle exceptions 
    print("Extract fractions ran")
    fraction = None
    try:
        fraction = tracker.latest_message.get('entities')[0].get('text').lower()
    except:
        print("AN ERROR in EXTRACT FRACTION OCCURED")
        fraction = None 
    finally:
        return fraction

def matchOption(user_input, slot_name, cutoff=60):
    # TODO: Turn this into an external database
    resp = user_input.lower()
    options_dict = {
    "object_2": ["option_match", ["badams", "biscuits", "grapes", "chocolates"]]
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

def checkQuestion(user_input, question, tracker=None):
    """ 
    Takes in the expected user input, queries DB, 
    and validates the user input against the question type
    Returns -> 'CORRECT', 'INCORRECT' and None 
    """

    questions_dict = question_db()
    q_list = questions_dict[question]
    question_type = q_list[0]
    
    # Exit if not extracted

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

def respondQuestion(answer, question, slot_value, dispatcher, domain):
    slot_dict_input = None
    if answer == "CORRECT":
        dispatcher.utter_message(template="utter_correct")
        slot_dict_input = slot_value
    if answer == "INCORRECT":
        dispatcher.utter_message(template="utter_incorrect")
        slot_dict_input = slot_value
    if not answer:
        print(f"Failed to extract slot for {question} - Extracted: {slot_value}")
        dispatcher.utter_message("I couldn't understand your input!")
        slot_dict_input = None
    
    # Automatically search for explanation

    if slot_dict_input:
        explanation_response = f"utter_{question}_explanation"
        dispatcher.utter_message(template=explanation_response)

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

class ActionPause(Action):

    def name(self) -> Text:
        return "action_pause"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        time.sleep(7) # Add a 7 second delay 
        return [ ]
class ActionCheckUserStatus(Action):

    def name(self) -> Text:
        return "action_check_user_status"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # TODO: Query Internal Postgres DB for past interaction
        print("action_CHECK ran")
        if tracker.get_slot("userName"):
            print(f" Older user of with name {tracker.get_slot('userName')}")
            return [SlotSet("is_new_user", False)]
        else:
            return [SlotSet("is_new_user", True)]

class ActionFailedFirstTimeForm(Action):

    def name(self) -> Text:
        return "action_failed_first_time_form"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message("Sorry I didn't get your information right. Lets try this again!")
        return [SlotSet(key = "userName", value = None), SlotSet(key = "age", value = None) ]

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
            dispatcher.utter_message(text="Sorry I missed your name. Can you just type only your first name for me?")
            return {"userName": None}
    
    def validate_age(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if int(slot_value) > 0:
            return {"age": slot_value}
        else:
            dispatcher.utter_message(template="utter_wrong_format", err="You can't be less than 0  :) !")
            return {"age": None}

class ValidateFractionHalvesStoryForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fractions_halves_story_form"
    
    # TODO: Change once you understand how to deal with a non extracted entity
    def validate_friend_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        defualt_name = "Puja"
        name = extractName(slot_value, tracker)
        if name:
            return {"friend_1":name}
        else:
            dispatcher.utter_message(f"I can't find the name! Lets call your friend {defualt_name} for now!")
            return {"friend_1": defualt_name}

    def validate_fractions_halves_mcq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name = "fractions_halves_mcq_1"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name: slot_dict_input}

    def validate_fractions_halves_frq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name = "fractions_halves_frq_1"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name: slot_dict_input}

class ValidateFractionPartsStoryForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fractions_parts_story_form"

    def validate_object_2(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        match = matchOption(slot_value, "object_2")
        if match:
            return{"object_2": match}
        else:
            dispatcher.utter_message(template= "utter_wrong_format", err= "That is not an option, choose again!!")
            return{"object_2": None}

    def validate_fractions_parts_nrq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "fractions_parts_nrq_1"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name: slot_dict_input}
    
    def validate_fractions_parts_mcq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name = "fractions_parts_mcq_1"
        answer = checkQuestion(slot_value, question_name, tracker=tracker)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name: slot_dict_input}


    def validate_fractions_parts_mcq_2(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name =  "fractions_parts_mcq_2"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name:slot_dict_input}

    def validate_fractions_parts_mcq_3(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name =  "fractions_parts_mcq_3"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name:slot_dict_input}
    
    def validate_fractions_parts_mcq_4(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        question_name =  "fractions_parts_mcq_4"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name:slot_dict_input}

class ValidateFractionWholesStoryForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fractions_wholes_story_form"
    
    def validate_fractions_wholes_nrq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "fractions_wholes_nrq_1"
        answer = checkQuestion(slot_value, question_name)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name: slot_dict_input}
    
    def validate_fractions_wholes_nrq_2(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "fractions_wholes_nrq_2"
        answer = checkQuestion(slot_value, question_name, tracker=tracker)
        print(answer)    
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name: slot_dict_input}
    
    def validate_fractions_wholes_frq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "fractions_wholes_frq_1"
        answer = checkQuestion(slot_value, question_name)
        print(answer)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name: slot_dict_input}    
    
    def validate_fractions_wholes_nrq_3(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "fractions_wholes_nrq_3"
        answer = checkQuestion(slot_value, question_name, tracker=tracker)
        print(answer)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name: slot_dict_input}
    
    def validate_fractions_wholes_nrq_4(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "fractions_wholes_nrq_4"
        answer = checkQuestion(slot_value, question_name, tracker=tracker)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        return {question_name: slot_dict_input}
    
    def validate_fractions_wholes_nrq_5(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:        
        question_name = "fractions_wholes_nrq_5"
        answer = checkQuestion(slot_value, question_name, tracker=tracker)
        print(answer)
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher, domain)
        print(slot_dict_input)
        return {question_name: slot_dict_input}
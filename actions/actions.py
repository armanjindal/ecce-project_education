import string 
from typing import Text, List, Any, Dict

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

#import helpers
from fuzzywuzzy import process
# TODO: Figure out why I cannot import local .py files

def question_db():
    # TODO: Turn this into a external database. Turn dict into DB query
    questions_dict = {
    "fractions_halves_mcq_1": ["mcq_match", ['a','c','d','e'], 'c'],
    "fractions_halves_frq_1": ["frq_keyword_match", ["equal", "halves", "half", "same", "identical"], None],
    "fractions_parts_mcq_1" : ["nrq_fractions", ["1/3", "2/6"]],
    "fractions_parts_mcq_2": ["frq_keyword_match", ["more", "greater"], ["less", "fewer"]],
    "fractions_parts_nrq_1": ["nrq_numeral", [2]],
    "fractions_parts_mcq_3": ["frq_keyword_match", ["more", "greater"], ["less", "fewer"]],
    "fractions_parts_mcq_4": ["frq_keyword_match", ["more", "greater"], ["less", "fewer"]],
    "fractions_wholes_nrq_1": ["nrq_numeral", [4]],
    "fractions_wholes_nrq_2": ["nrq_fractions", ["1/3", "2/6"]],
    "fractions_wholes_frq_1": ["frq_keyword_match", ["box", "4"], None],
    "fractions_wholes_nrq_3": ["nrq_numeral", [1]],
    "fractions_wholes_nrq_4": ["nrq_fractions", ["1/4"]],
    "fractions_wholes_nrq_5": ["nrq_fractions", ["1/6"]],
    }
    return questions_dict

def extractFraction(tracker):
    # Error handle exceptions 
    print(tracker)
    fraction = None
    try:
        fraction = tracker.latest_message.get('entities')[0].get('text').lower()
    except:
        print("AN ERROR in EXTRACT FRACTION OCCURED")
        return None
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
    """ Takes in the expected user input, queries DB, 
    and validates the user input against the question type"""
    questions_dict = question_db()
    q_list = questions_dict[question]
    question_type = q_list[0]
    
    if question_type == "nrq_fractions":
        if user_input > 0 and user_input <= 1:
            text_fraction = extractFraction(tracker)
            if text_fraction:
                if text_fraction in q_list[1]:
                    return "CORRECT"
                else:
                    return "INCORRECT"
        return "WRONG_FORMAT"
    
    if question_type == "nrq_numeral":
        if user_input:
            for ans_option in q_list[1]:
                if user_input == ans_option:
                    return "CORRECT"
            return "INCORRECT"
        else:
            return "WRONG_FORMAT"
    # Returns exact match to options i.e 'A, B, C, D' 
    if question_type=="mcq_match":
        resp = user_input.lower()
        options = q_list[1]
        if resp in options:
            if resp == q_list[2]:
                return "CORRECT"
            else:
                return "INCORRECT"
        else:
            return None
    # Checks free text input if it contains list 1 and does not contain words for list 2
    if question_type == "frq_keyword_match":
        resp = user_input.lower()
        resp_words = resp.split()
        keywords = q_list[1] 
        if any(word in keywords for word in resp_words):
            not_words = q_list[2]
            if not_words:
                if any(word in not_words for word in resp_words):
                    return "AMBIG" # Included words in both lists
            return "CORRECT"
        else:
            return "INCORRECT"

def respondQuestion(answer, question, slot_value, dispatcher):
    slot_dict_input = None
    if answer == "CORRECT":
        dispatcher.utter_message(template="utter_correct")
        slot_dict_input = slot_value
    if answer == "INCORRECT":
        dispatcher.utter_message(template="utter_incorrect")
        # TODO: Add hint counter / progression HERE
        slot_dict_input = slot_value
    if answer == "WRONG_FORMAT":
        dispatcher.utter_message(template="utter_wrong_format", err="Give me a number!")
        slot_dict_input = None
    if answer == "AMBIG":
        dispatcher.utter_message(template="utter_wrong_format", err="That is a confusing answer!")
        slot_dict_input = None
    if slot_dict_input:
        dispatcher.utter_message(template=f"utter_{question}_explanation")
    return slot_dict_input
    
class ValidateFirstTimeForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_first_time_form"
    
    def validate_user_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value:
            if isinstance(slot_value, str):
                return {"user_name": slot_value.capitalize()}
            if isinstance(slot_value, list):
                return {"user_name": slot_value[0].capitalize()}
        else:
            dispatcher.utter_message(text="I can't seem to recognize your name, friend!")
            return {"user_name": "friend"}
    
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
        if slot_value:
            if isinstance(slot_value, str):
                name = slot_value
            if isinstance(slot_value, list):
                name = slot_value[0]
            dispatcher.utter_message(template=f"utter_friend_1_explanation", friend_1=name)
            return {"friend_1": name}
        else:
            dispatcher.utter_message(f"I can't find the name! Lets call your friend {default_name} for now!")
            dispatcher.utter_message(template=f"utter_friend_1_explanation", friend_1=default_name)           
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        print(answer)    
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
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
        slot_dict_input = respondQuestion(answer, question_name, slot_value, dispatcher)
        print(slot_dict_input)
        return {question_name: slot_dict_input}
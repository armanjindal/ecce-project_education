import string 
from typing import Text, List, Any, Dict

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

#import helpers
from fuzzywuzzy import process

def extractFraction(tracker):
    # Error handle exceptions 
    return tracker.latest_message.get('entities')[0].get('text').lower()

def mcq_match(user_input, question, key , method="FuzzyMatch", cutoff=60):
    # Method used to match a single word 
    mcq_options_dict = {
    "action_lesson_options": ["fractions", "multiplication"],
    "validate_fractions_halves_story_form": {
        "fractions_halves_mcq_1": [['a','c','d','e'], 'c']
        },
    "validate_fractions_parts_story_form": {
        "object_2": ["badams", "biscuits", "grapes", "chocolates"],
        "fractions_parts_mcq_2" : ["more", "I get more", "greater"] 
        }
    }
    # Fuzzy match strings and returns closest match result
    if method=="FuzzyMatch":
        resp = user_input.lower()
        options = mcq_options_dict[f"{question}"]
        if key:
            options = options[f"{key}"]
        result = process.extractOne(resp, options, score_cutoff=cutoff)
        if result:
            return result[0]
        else:
            return None 
    
    # Returns exact match to options i.e 'A, B, C, D' 
    if method=="DirectMatch":
        resp = user_input.lower()
        answer_list = mcq_options_dict[f"{question}"][f"{key}"]
        if resp in answer_list[0]:
            if resp == answer_list[1]:
                return ["CORRECT", resp]
            else:
                return ["INCORRECT", resp]
        else:
            return None


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
            name = str(slot_value)
            return {"user_name": name.capitalize()}
        else:
            dispatcher.utter_message(text="I can't seem to recognize your name!")
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
    
class FractionsHalvesIntroduction2(Action):
    def name(self) -> Text:
        return "action_fractions_halves_introduction_2"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        friend_name = next(tracker.get_latest_entity_values("name"), None)
        prev_name = tracker.get_slot(key="friend_1")
        if friend_name:
            dispatcher.utter_message(template="utter_fractions_halves_introduction_2", friend_1=friend_name)
            return [SlotSet(key="friend_1", value=friend_name.capitalize())]
        else:
            dispatcher.utter_message(text=f"I did not quite get the name. Lets call just call your friend {prev_name}!s")
            dispatcher.utter_message(template="utter_fractions_halves_introduction_2")
        return []

class ValidateFractionHalvesStoryForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_fractions_halves_story_form"

    def validate_fractions_halves_mcq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        slot_name = "fractions_halves_mcq_1"
        answer = mcq_match(slot_value, self.name(), slot_name, "DirectMatch") 
        if answer:
            if answer[0] == "CORRECT":
                dispatcher.utter_message(template="utter_correct")
                return {"fractions_halves_mcq_1": answer[1]}
            else:
                dispatcher.utter_message(template="utter_incorrect")
                dispatcher.utter_message(text= "Let try it again!")
                return {"fractions_halves_mcq_1": None}
        else:
            dispatcher.utter_message(template="utter_wrong_format", err="I need a one letter answer like 'A' or 'D' ")
            return {"fractions_halves_mcq_1": None}

    def validate_fractions_halves_frq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        answer_keywords = ["equal", "halves", "half", "same", "identical"]
        response = slot_value.lower()
        if response:
            if any(word in answer_keywords for word in response.split()):
                dispatcher.utter_message(template="utter_correct")
            else:
                dispatcher.utter_message(template="utter_incorrect")
            dispatcher.utter_message(template="utter_fractions_halves_frq_1_explanation")
            return{"fractions_halves_frq_1": response}
        else:
            dispatcher.utter_message(template= "utter_wrong_format", err= "I need a longer answer than that !")
            return{"fractions_halves_frq_1": None}

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
        
        match = mcq_match(slot_value, self.name(), "object_2")
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
        if slot_value and int(slot_value) > 0:
            if int(slot_value) == 2:
                dispatcher.utter_message(template="utter_correct")
            else:
                dispatcher.utter_message(template="utter_incorrect")
            
            dispatcher.utter_message(template="utter_fractions_parts_nrq_1_explanation")
            return {"fractions_parts_nrq_1": slot_value}
        else:
            dispatcher.utter_message(template="utter_wrong_format", err="Give me a number!")
            return {"fractions_parts_nrq_1": None}
    
    def validate_fractions_parts_mcq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value > 0 and slot_value <= 1:
            text_fraction = extractFraction(tracker)
            if text_fraction == '1/3':
                dispatcher.utter_message(template="utter_correct")
                dispatcher.utter_message(template="utter_fractions_parts_mcq_1_explanation")
                return {"fractions_parts_mcq_1": text_fraction}
            else:
                dispatcher.utter_message(template="utter_fractions_parts_mcq_1_options")
                return {"fractions_parts_mcq_1": None}
        else:
            dispatcher.utter_message(template="utter_wrong_format", err="Give me a fraction! For example 1/2 or 1/4")
            return {"fractions_parts_mcq_1": None}          

    def validate_fractions_parts_mcq_2(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        slot_name = "fractions_parts_mcq_2"
        result = mcq_match(slot_value, self.name(), slot_name)
        if result and slot_value.lower() not in ["lower", "less"]:
            dispatcher.utter_message(template="utter_correct")
        else:
            dispatcher.utter_message(template= "utter_incorrect")
        dispatcher.utter_message(template="utter_fractions_parts_mcq_2_explanation")
        
        return{"fractions_parts_mcq_2": result}


""" Temporay helper methods that will be defined correctly 
once basic functionality is established """



# # TODO: Create Q/A database 
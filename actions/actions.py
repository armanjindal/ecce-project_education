import string 
from typing import Text, List, Any, Dict

from fuzzywuzzy import process
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict



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
            dispatcher.utter_message(template="utter_wrong_format", err="You can't be less than 0  :)) !!")
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
            return [SlotSet(key="friend_1", value=friend_name)]
        else:
            dispatcher.utter_message(text=f"I did not quite get the name. Lets call your friend {prev_name} for now!")
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
        # TODO: Turn this coroutine for all MCQs where values loaded dynamically
        # Check if provided in correct format
        if slot_value.lower() in mcq_options_db(): 
            if slot_value.lower() == "c":
                dispatcher.utter_message(template="utter_correct")
                return {"fractions_halves_mcq_1": slot_value}
            else:
                dispatcher.utter_message(template="utter_incorrect")
                dispatcher.utter_message(text= "Let try it again!")
                return {"fractions_halves_mcq_1": None}
        else:
            dispatcher.utter_message(template="utter_wrong_format", err="Try and give me a one letter answer like 'A' or 'D'")
            return {"fractions_halves_mcq_1": None}

    def validate_fractions_halves_frq_1(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        answer_keywords = ["equal", "halves", "half", "same"]
        response = slot_value.lower()
        if response:
            if any(word in answer_keywords for word in response.split()):
                dispatcher.utter_message(template="utter_correct")
            else:
                dispatcher.utter_message(template="utter_incorrect")
            dispatcher.utter_message(template="utter_fractions_halves_frq_1_explanation")
            return{"fractions_halves_frq_1": response}
        else:
            dispatcher.utter_message(template= "utter_wrong_format", err= "I need a longer answer than that!")
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
        # TODO: Turn this coroutine for all MCQs where values loaded dynamically
        # Check if provided in correct format
        answer_keywords = ["badams", "biscuits", "grapes", "chocolates"]
        response = slot_value.lower()
        result = process.extractOne(response, answer_keywords, score_cutoff=80)
        print(result)
        if result:
            return{"object_2": result[0]}
        else:
            dispatcher.utter_message(template= "utter_wrong_format", err= "That is not an option! Choose again")
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
            text_fraction = tracker.latest_message.get('entities')[0].get('text').lower()
            if text_fraction == '1/3':
                dispatcher.utter_message(template="utter_correct")
                dispatcher.utter_message(template="utter_fractions_parts_mcq_1_explanation")
                return {"fractions_parts_mcq_1": text_fraction}
            else:
                dispatcher.utter_message(template="utter_fractions_parts_mcq_1_options")
                return {"fractions_parts_mcq_1": None}
        else:
            dispatcher.utter_message(template="utter_wrong_format", err="Give me a fraction! For example 1/2 which is a half")
            return {"fractions_parts_mcq_1": None}          

    def validate_fractions_parts_mcq_2(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        # need to come up with better validation 
        answer_keywords = ["more", "I get more", "greater"] 
        response = slot_value.lower()
        result = process.extractOne(response, answer_keywords, score_cutoff=80)
        print(result)
        if result and "lower" not in response:
            dispatcher.utter_message(template="utter_correct")
        else:
            dispatcher.utter_message(template= "utter_incorrect")
            response = None
        dispatcher.utter_message(template="utter_fractions_parts_mcq_2_explanation")
        
        return{"fractions_parts_mcq_2": response}


""" Temporay helper methods that will be defined correctly 
once basic functionality is established """

def mcq_options_db(alpha = True, num_options = 4):
    if alpha:
        # Create a list of all English lowercase letters
        alphabet_list = list(string.ascii_lowercase)
        print(alphabet_list)
        return alphabet_list[:num_options]
    else:
        #MCQ indexed by Numbers starting from 1
        return list(range(1, num_options + 1))

# # TODO: Create a database where answers and questions can be changed
# answer_dict = {
#     "fractions_halves_mcq_1" : "c",
#     "fractions_halves_mcq_1" : "b",
#     "fractions_halves_frq_1" : ["equal", "same", "halves"]
# }
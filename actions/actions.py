# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from typing import Dict, Text, Any, List, Union, Optional


class Fractions_Parts_NRQ_1(FormAction):
    """A custom form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "fractions_parts_nrq_1_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["fractions_parts_nrq_1"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
        - an extracted entity
        - intent: value pairs
        - a whole message
        or a list of them, where a first match will be picked"""
        print("SLOT MAPPING RAN")
        return {"fractions_parts_nrq_1": self.from_entity(entity="number")}

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer"""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_fractions_parts_nrq_1(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if self.is_int(value) and int(value) > 0:
            if int(value) == 2:
                dispatcher.utter_message(template="utter_correct")
            else:
                dispatcher.utter_message(template="utter_incorrect")
            return {"fractions_parts_nrq_1": value}
        else:
            dispatcher.utter_message(template="utter_response_wrong_format")
            return {"fractions_parts_nrq_1": None}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
        after all required slots are filled"""
        # COLLECT META DATA ON RESPONSE HERE AND WRITE IT TO THE DATABASE
        dispatcher.utter_message(template="utter_fractions_parts_nrq_1_explanation")
        return []

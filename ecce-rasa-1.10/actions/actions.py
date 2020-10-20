# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/

from typing import Text, List, Any, Dict, Union
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import FormValidationAction
from rasa_sdk.types import DomainDict

class FractionsPartsNRQ1Form(FormValidationAction):
    def name(self) -> Text:
        return "validate_fractions_parts_nrq_1_form"

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
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate student response to question"""

        if self.is_int(value) and int(value) > 0:
            if int(value) == 2:
                dispatcher.utter_message(template="utter_correct")
            else:
                dispatcher.utter_message(template="utter_incorrect")
            return {"fractions_parts_nrq_1": value}
        else:
            dispatcher.utter_message(template="utter_response_wrong_format")
            return {"fractions_parts_nrq_1": None}



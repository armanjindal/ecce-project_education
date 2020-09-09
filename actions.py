# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction


# Slot filling action method
class IntroductionForm(FormAction):
    """Collects basic user information on first interaction"""

    def name(self):
        return "introduction_form"

    @staticmethod
    def required_slots(tracker):
        return [
            "name",
            "age",
            "grade",
            "school",
        ]

    def submit(self, dispatcher: CollectingDispatcher,
               tracker: Tracker, domain: Dict[Text, Any],) -> List[Dict]:
        name = tracker.get_slot("name")
        dispatcher.utter_message("Nice to meet you {}!".format(string(name)))
        return []

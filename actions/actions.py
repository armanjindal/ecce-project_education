from typing import Text, List, Any, Dict


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
        """Validate cuisine value."""

        if slot_value and len(str(slot_value)) > 0:
            return {"user_name": slot_value}
        else:
            dispatcher.utter_message(text="VALIDATE FUNCTION RAN AND FAILED")
            
    def validate_age(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""

        if int(slot_value) > 0:
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"age": slot_value}
        else:
            dispatcher.utter_message(template="utter_wrong_format", err="You can't be less than 0 :) !")
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
            print(f"THIS RAN. Name:{friend_name} Prev_Name: {prev_name}")
            dispatcher.utter_message(template="utter_fractions_halves_introduction_2", friend_1=friend_name)
            return [SlotSet(key="friend_1", value=friend_name)]
        else:
            dispatcher.utter_message(text=f"I did not quite get the name. Lets call your friend {prev_name}")
            dispatcher.utter_message(template="utter_fractions_halves_introduction_2")

        return []

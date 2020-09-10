## happy path - first time user
* greet
  - utter_greet
  - utter_first_time
  - introduction_form
  - form{"name":"introduction_form"}
  - form{"name":null}
  - utter_start
  - utter_slot_values
* affirm
  - utter_lesson_options
* lesson_fraction
  - utter_fraction_begin
  - utter_halves_1
  - utter_halves_q1
* q1_correct
  - utter_correct
  - utter_halves_a1
  - introduction_form
  - form{"name":"introduction_form"}
  - form{"name":null}

## happy path - q1 incorrect
* q1_incorrect
  - utter_incorrect
  - utter_halves_a1

## say goodbye
* goodbye
  - utter_goodbye

## bot challenge
* bot_challenge
  - utter_iamabot

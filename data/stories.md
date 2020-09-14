## happy path - first time user
* greet
  - utter_greet
  - utter_first_time
  - introduction_form
  - form{"name":"introduction_form"}
  - form{"name":null}
  - utter_information
* affirm
  - utter_lesson_options
* lesson_fractions
  - utter_fraction_begin
  - utter_halves_1
  - utter_halves_q1
* correct
  - utter_ask_why
  - utter_correct
  - utter_halves_a1
  - utter_halves_q1-1
* correct
  - utter_correct
  - utter_halves_a1-1
  - utter_conclusion_halves
* affirm
  - utter_parts_introduction_1
  - utter_parts_q1
  - utter_parts_q1-1
* correct
  - utter_parts_q3
* correct
  - utter_parts_story
  - utter_parts_animation

## happy path - q1 incorrect
* incorrect
  - utter_incorrect
  - utter_halves_a1

## say goodbye - turn into rule 2.0 
* goodbye
  - utter_goodbye

## bot challenge - turn into rule 2.0
* bot_challenge
  - utter_iamabot

## Interactive Learning Happy Path

* greet
    - utter_greet
    - utter_first_time
    - introduction_form
    - form{"name":"introduction_form"}
    - slot{"requested_slot":"name"}
* inform{"name":"Mahima"}
    - slot{"name":"Mahima"}
    - slot{"name":"Mahima"}
    - introduction_form
    - slot{"name":"Mahima"}
    - slot{"requested_slot":"age"}
* inform{"age":"10"}
    - slot{"age":"10"}
    - slot{"age":"10"}
    - introduction_form
    - slot{"age":"10"}
    - slot{"requested_slot":"grade"}
* inform{"grade":"7"}
    - slot{"grade":"7"}
    - slot{"grade":"7"}
    - introduction_form
    - slot{"grade":"7"}
    - slot{"requested_slot":"school"}
* inform{"school":"City Massouri"}
    - slot{"school":"City Massouri"}
    - slot{"school":"City Massouri"}
    - introduction_form
    - slot{"school":"City Massouri"}
    - form{"name":null}
    - slot{"requested_slot":null}
    - utter_information
* affirm
    - utter_lesson_options
* lesson_fractions
    - slot{"name":"Mahima"}
    - slot{"age":"10"}
    - slot{"grade":"7"}
    - slot{"school":"City Massouri"}
    - utter_fraction_begin
    - utter_halves_1
  	- utter_halves_q1

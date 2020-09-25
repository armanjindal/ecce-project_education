## happy path - INTRODUCTION - first time user
* greet
  - utter_greet 
  - utter_first_time
  - utter_ask_name
* inform{"name": "Priya"}
  - utter_ask_age
* inform{"age":"9"}
  - utter_nice_meet_you
  - utter_lesson_options

## happy path - FRACTIONS - MCQ Correct 
* lesson_fractions
  - utter_fractions_introduction_1
  - utter_fractions_halves_1
  - utter_fractions_halves_mcq_1
* mcq_correct
  - utter_correct
  - utter_fractions_halves_mcq_1_explanation
  - utter_fractions_halves_mcq_1-1
* mcq_correct
  - utter_correct
  - utter_fractions_halves_mcq_1-1_explanation
  - utter_fractions_halves_conclusion
  - utter_fractions_halves_conclusion_animation
  - utter_start_next
* affirm 
  - utter_fractions_parts_introduction_1
  - utter_fractions_parts_introduction_2
  - fractions_parts_nrq_1_form
  - form{"name":"fractions_parts_nrq_1_form"}
  - form{"name":null}
  - utter_fractions_parts_mcq_1
* mcq_correct
  - utter_correct
  - utter_fractions_parts_mcq_1
* mcq_correct
  - utter_correct
  - utter_fractions_parts_mcq_1_explanation
  - utter_fractions_parts_mcq_2
* mcq_correct
  - utter_correct
  - utter_fractions_parts_mcq_2_explanation
  - utter_fractions_parts_mcq_3
* mcq_correct
  - utter_incorrect
  - utter_fractions_parts_mcq_3_explanation
  - utter_fractions_parts_conclusion_1
  - utter_fractions_parts_conclusion_2
  - utter_fractions_parts_conclusion_3
  - utter_fractions_parts_animation

## happy path - FRACTIONS - INCORRECT
* lesson_fractions
  - utter_fractions_introduction_1
  - utter_fractions_halves_1
  - utter_fractions_halves_mcq_1
* mcq_incorrect
  - utter_incorrect
  - utter_fractions_halves_mcq_1_explanation
  - utter_fractions_halves_mcq_1-1
* mcq_incorrect
  - utter_incorrect
  - utter_fractions_halves_mcq_1-1_explanation
  - utter_fractions_halves_conclusion
  - utter_fractions_halves_conclusion_animation
  - utter_start_next
* affirm 
  - utter_fractions_parts_introduction_1
  - utter_fractions_parts_introduction_2
  - fractions_parts_nrq_1_form
  - form{"name":"fractions_parts_nrq_1_form"}
  - form{"name":null}
  - utter_fractions_parts_mcq_1
* mcq_incorrect
  - utter_incorrect
  - utter_fractions_parts_mcq_1
* mcq_incorrect
  - utter_incorrect
  - utter_fractions_parts_mcq_1_explanation
  - utter_fractions_parts_mcq_2
* mcq_incorrect
  - utter_incorrect
  - utter_fractions_parts_mcq_2_explanation
  - utter_fractions_parts_mcq_3
* mcq_incorrect
  - utter_incorrect
  - utter_fractions_parts_mcq_3_explanation
  - utter_fractions_parts_conclusion_1
  - utter_fractions_parts_conclusion_2
  - utter_fractions_parts_conclusion_3
  - utter_fractions_parts_animation

## correct - turn into rule in 2.0 
* mcq_correct
  - utter_correct

## incorrect - turn into rule in 2.0
* mcq_incorrect
  - utter_incorrect

## say goodbye - turn into rule 2.0 
* goodbye
  - utter_goodbye

## bot challenge - turn into rule 2.0
* bot_challenge
  - utter_iamabot
from fuzzywuzzy import process

mcq_options_dict = {
    "lesson_options": ["fractions", "multiplication"],
    "validate_fractions_parts_story_form": {
        "object_2": ["badams", "biscuits", "grapes", "chocolates"]
        }
}

def mcq_match(user_input, question, key , method="FuzzyWuzzy", cutoff=60):
    # Method used to match a single word 
    if method=="FuzzyWuzzy":
        resp = user_input.lower()
        options = mcq_options_dict[question]
        if key:
            options = options[key]
        return process.extractOne(resp, options, score_cutoff=cutoff)

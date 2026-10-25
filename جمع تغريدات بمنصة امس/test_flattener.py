import json

def recursive_flatten(d, flat_dict):
    """
    Recursively look for target keys and flatten them.
    If the value is a dict, we also flatten its values into a string.
    But we ALSO want to extract any known keys from it.
    Actually, the easiest way is to traverse the JSON. If a key is in our known_keys, we format its value as a string.
    """
    if isinstance(d, dict):
        for k, v in d.items():
            if k in known_keys:
                if isinstance(v, dict):
                    flat_dict[k] = " - ".join([str(val) for val in v.values() if val])
                elif isinstance(v, list):
                    flat_dict[k] = "، ".join([str(val) for val in v if val])
                else:
                    flat_dict[k] = str(v)
            else:
                # keep searching deeper
                recursive_flatten(v, flat_dict)
    elif isinstance(d, list):
        for item in d:
            recursive_flatten(item, flat_dict)

known_keys = {
    "Date", "URL", "Language", "Occasion", "Media_Type", "Likes", "Comments", "Retweets", "Intro_Paragraph",
    "Target_Audience", "Actors", "Geo_Scope", "Comm_Goal", "Regional_Context", "Qualitative_Analysis_Space",
    "Self_Positives_Score", "Self_Positives_Analysis", "Self_Negatives_Score", "Self_Negatives_Analysis",
    "Other_Negatives_Score", "Other_Negatives_Analysis", "Other_Positives_Score", "Other_Positives_Analysis",
    "Official_Info", "Official_Statements", "Intl_Coop", "Diplomatic_Visits", "Stats_Reports",
    "Intl_Sources", "Human_Stories", "National_Success", "State_Superiority", "Solidarity",
    "Political_Values", "Tech_Progress", "Intl_Leadership", "Reliable_Partner", "Correct_Stereotypes", "Intl_Trust", "Cultural_Appeal",
    "Hashtags", "Mentions", "Retweets_Quotes", "Call_to_Action", "Official_Links",
    "Comms_Channels", "Reply_Audience", "Live_Sessions", "Encourage_Proposals", "Polls_Questions",
    "Irony", "Celeb_Quotes", "Disapproval", "Politeness", "Show_Power", "Cultural_Symbols", "National_Praise", "Endearment", "Doubt", "Linguistic_Styles", "Threats", "Victimhood", "Similarities", "Challenge", "Slogans", "Citizen_Opinions", "Categorization", "Positives_Traits", "Other_Negatives_Show", "Superlatives", "Supportive_Power",
    "Examples", "Comparison", "Proof", "Justification", "Stats_Numbers", "Number_Game", "Religious_Frames",
    "Soft_Pol_Power", "Soft_Cult_Power", "Soft_Edu_Power", "Soft_Econ_Power", "Soft_Tech_Power", "Soft_Human_Power", "Soft_Media_Power"
}

# Read log or call mistral once

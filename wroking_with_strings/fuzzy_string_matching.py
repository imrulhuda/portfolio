#!/user/user1/ih2344/.conda/envs/angellist/bin/python

import re
import pandas as pd
from tqdm import tqdm
from collections import Counter
from fuzzywuzzy import fuzz, process
from pandas.io.json import json_normalize


def extract_match(from_keys, target_keys):
    result = list()
    for k in tqdm(from_keys):
        matches = dict()
        matches['key'] = k
        matches["fuzz_ratio"] = process.extractOne(k, target_keys, scorer=fuzz.ratio)
        matches["partial_ratio"] = process.extractOne(k, target_keys, scorer=fuzz.partial_ratio)
        matches["token_sort_ratio"] = process.extractOne(k, target_keys, scorer=fuzz.token_sort_ratio)
        matches["token_set_ratio"] = process.extractOne(k, target_keys, scorer=fuzz.token_set_ratio)
        result.append(matches)
    return result


# reading and preparing data
target_data = pd.read_stata("corptech_name.dta")
target_data = target_data.drop_duplicates()
ac_name = pd.read_stata("acquisition_name.dta")
ac_name = ac_name.drop_duplicates()
ac_name["name"] = ac_name["acquirorname"]
ac_name["cusip"] = ac_name["ac_cusip"]
ac_name["source_file"] = "acquisition_name"
jv_data = pd.read_stata("JV_Alliance_Corptech_Name.dta")
jv_data = jv_data.drop_duplicates()
jv_data["source_file"] = "JV_Alliance_Corptech_Name"
combined_sources = pd.concat([ac_name, jv_data], sort=False)
target_data['name_for_match'] = target_data['Company_name'].apply(lambda x: re.sub(r'[^\w\s]','',x).lower())
combined_sources['name_for_match'] = combined_sources['name'].apply(lambda x: re.sub(r'[^\w\s]','',x).lower())

# initial matching
source_names = set(combined_sources['name_for_match'])
target_data['is_match'] = target_data['name_for_match'].apply(lambda x: x in source_names)
target_data = target_data[target_data['is_match'] == False]

# cleaning common last words
counter_source = Counter([i.split()[-1] for i in combined_sources['name_for_match']])
counter_target = Counter([i.split()[-1] for i in target_data['name_for_match']])
common_words = [i[0] for i in sorted([(k,v) for k,v in counter_target.items()], key = lambda x: x[1], reverse = True)[:10]]
common_words.extend([i[0] for i in sorted([(k,v) for k,v in counter_source.items()], key = lambda x: x[1], reverse = True)[:10]])
common_words = set(common_words)
target_data['name_for_fuzzy_match'] = target_data['name_for_match'].apply(lambda x: " ".join(x.split()[:-1]) if x.split()[-1] in common_words else x)
combined_sources['name_for_fuzzy_match'] = combined_sources['name_for_match'].apply(lambda x: " ".join(x.split()[:-1]) if x.split()[-1] in common_words else x)

# reset index and generating keys for fuzzy matching
target_data.reset_index(drop=True, inplace=True)
combined_sources.reset_index(drop=True, inplace=True)
source_keys = set(combined_sources['name_for_fuzzy_match'])
target_keys = set(combined_sources['name_for_fuzzy_match'])

# fuzzy match and save results
result = extract_match(source_keys, target_keys)
json_normalize(result).to_csv('fuzzywuzzy_output_new.csv', index=False, encoding='utf-8-sig')
import glob
import re
import pandas as pd
from pandas.io.json import json_normalize

# function to find the skills
def find_skills(text):
    with open(text, encoding="utf8") as f:
        data = f.read()
    pattern = re.compile('\nSKILLS\n(.*)', re.IGNORECASE)
    m = pattern.search(data)
    if m:
        return m.group(1)
    else: 
        return None

# resumes
text_files = glob.glob("day*\*", recursive=True)

# extracting the skills
d = dict()
for text in text_files:
    d[text] = find_skills(text)

# Filtering out the null values
full_data = dict()
for k, v in d.items():
    if v is not None:
        full_data[k] = v

# spliting the skills
full_data_2 = dict()
for k, v in full_data.items():
    full_data_2[k] = v.split(',')

# function to separate skills and years
def split_skill_year(list_obj, pattern):
    result = list()
    m = [pattern.search(x) for x in list_obj]
    for i, v in enumerate(m):
        if v is not None:
            result.append((v.group(1).strip(), v.group(2).replace('(', '').replace(')','')))
        else:
            result.append(list_obj[i].strip())
    return result

# spliting the skill and year
pattern = re.compile("(.*)(\(.*\))")
result_dict = dict()
for k, v in full_data_2.items():
    key = k.split('_')[1].replace('.txt','')
    result_dict[key] = split_skill_year(v, pattern)
result_list = list()
for k, v in result_dict.items():
    bit = dict()
    bit['id'] = k
    bit_list = list()
    for i in v:
        info = dict()
        if type(i) == tuple:
            info['skill'] = i[0]
            info['time'] = i[1]
        else:
            info['skill'] = i
            info['time'] = None
        bit_list.append(info)
    bit['skills'] = bit_list
    result_list.append(bit)

# saving the data
df = json_normalize(result_list, 'skills', meta='id')
df = df[['id', 'skill', 'time']]
df.to_csv('resume_parsed.csv', encoding='utf-8-sig', index=False)
#!/user/ih2344/.conda/envs/jupyter_demo/bin/python

import os
import re
import sys
import glob
import gensim
import logging
import pandas as pd
from gensim.test.utils import get_tmpfile
from gensim.models import KeyedVectors


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
which_model = sys.argv[1]
output_folder = which_model.replace("model_","")
which_corpus = output_folder.split("_")[0]

# class DocumentFeeder:
#     def __init__(self, path):
#         self.r = re.compile("[^a-zA-Z]")
#         self.path = path

#     def __iter__(self):
#         for fname in os.listdir(self.path):
#             for line in open(os.path.join(self.path, fname)):
#                 for sentence in line.split("."):
#                     no_punc = self.r.sub(" ",sentence).lower().split()
#                     if no_punc:
#                         yield no_punc

class DocumentFeeder:
    # THIS IS THE REWORKED (in August 2020) version
    def __init__(self, filelist):
        self.r = re.compile("[^a-zA-Z]")
        self.filelist = filelist

    def __iter__(self):
        for fname in self.filelist:
            for line in open(os.path.join("/work/ih2344/word_embedding/august_rework/corpus/", fname)):
                for sentence in line.split("."):
                    # this is where we clean the text
                    no_punc = self.r.sub(" ",sentence).lower().split()
                    if no_punc:
                        yield no_punc


# folders = glob.glob("/work/ih2344/word_embedding/core_models_added/*")
# Reading the metadata
meta = pd.read_csv("meta.csv", parse_dates = ['published_at'])
meta = meta[(meta['year'] > 2008) & (meta['year'] < 2019)]
meta = meta[meta['char_len'] > 2000]
meta['cik'] = meta['cik'].apply(lambda x: str(x).zfill(10))

# reading the focal firms info
match = pd.read_excel("for_imrul.xlsx", 
                      sheet_name = "targets_neat", 
                      skiprows = 1,
                      names = ['type', 'sl', 'target_name', 'cik', 'prop_name_1', 'cik_1', 'prop_name_2', 'cik_2', 'date'],
                      usecols = "B:J",
                      dtype={'cik': object, 'cik_1': object, 'cik_2': object})
ciks = list(match['cik'])
ciks.extend(match['cik_1'])
ciks.extend(match['cik_2'])
cik_date = {}
for i, r in match.iterrows():
    cik_date[r['cik']] = r['date']
    cik_date[r['cik_1']] = r['date']
    cik_date[r['cik_2']] = r['date']

core_models = meta[meta['cik'].isin(set(ciks))]

print(f"shape of core models df before corpus filter is {core_models.shape}")
if which_corpus = "sec":
    core_models = core_models[core_models['is_transcript'] == False]
if which_corpus = "transcripts":
    core_models = core_models[core_models['is_transcript'] == True]

print(f"shape of core models df after corpus filter for {which_corpus} is {core_models.shape}")

for cik in ciks:
    df_before = core_models[(core_models['cik'] == cik) & (core_models['published_at'] < cik_date[cik])]
    df_after = core_models[(core_models['cik'] == cik) & (core_models['published_at'] > cik_date[cik])]
    print(f"for cik {cik} cutoff date is {cik_date[cik]}")
    print(f"for cik {cik} the before shape is {df_before.shape}")
    print(f"for cik {cik} the after shape is {df_after.shape}")
    filelist_before = df_before['filename']
    filelist_after = df_after['filename']
    # pre
    dc_before = DocumentFeeder(filelist_before)
    trained_model = gensim.models.Word2Vec.load(f"{which_model}")
    trained_model.build_vocab(dc_before, update=True)
    trained_model.train(dc_before, total_examples=trained_model.corpus_count, epochs=trained_model.epochs)
    word_vectors = trained_model.wv
    word_vectors.save(f"core_models/{output_folder}/{cik}_pre")
    # post
    dc_after = DocumentFeeder(filelist_after)
    trained_model = gensim.models.Word2Vec.load(f"{which_model}")
    trained_model.build_vocab(dc_after, update=True)
    trained_model.train(dc_after, total_examples=trained_model.corpus_count, epochs=trained_model.epochs)
    word_vectors = trained_model.wv
    word_vectors.save(f"core_models/{output_folder}/{cik}_post")

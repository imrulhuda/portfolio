#!/user/ih2344/.conda/envs/jupyter_demo/bin/python

import sys
import os
import re
import time
import gensim
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# This class will feed the text files to Word2Vec so that we do not have to load all the txt files in memory
class DocumentFeeder:
    # THIS IS THE OLD ONE
    # def __init__(self, path):
    #     self.r = re.compile("[^a-zA-Z]")
    #     self.path = path

    # def __iter__(self):
    #     for fname in os.listdir(self.path):
    #         for line in open(os.path.join(self.path, fname)):
    #             for sentence in line.split("."):
    #                 # this is where we clean the text
    #                 no_punc = self.r.sub(" ",sentence).lower().split()
    #                 if no_punc:
    #                     yield no_punc

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

# THIS IS THE OLD ONE
# dc = DocumentFeeder("/NOBACKUP/scratch/ih2344/word_embedding/training_corpus")

# get the ciks for the focal firms
match = pd.read_excel("for_imrul.xlsx", 
                      sheet_name = "targets_neat", 
                      skiprows = 1,
                      names = ['type', 'sl', 'target_name', 'cik', 'prop_name_1', 'cik_1', 'prop_name_2', 'cik_2', 'date'],
                      usecols = "B:J",
                      dtype={'cik': object, 'cik_1': object, 'cik_2': object})
ciks = list(match['cik'])
ciks.extend(match['cik_1'])
ciks.extend(match['cik_2'])

which_corpus = sys.argv[1]
vector_size = int(sys.argv[2])

# read in the files list and filter
meta = pd.read_csv("meta.csv")
meta['cik'] = meta['cik'].apply(lambda x: str(x).zfill(10))
pre_train = meta[~meta['cik'].isin(set(ciks))]
pre_train = pre_train[pre_train['char_len'] > 2000]
pre_train = pre_train.drop_duplicates(['filename'])

if which_corpus = "both":
    filelist = pre_train['filename']
if which_corpus = "sec":
    pre_train = pre_train[pre_train['is_transcript'] == False]
    filelist = pre_train['filename']
if which_corpus = "transcripts":
    pre_train = pre_train[pre_train['is_transcript'] == True]
    filelist = pre_train['filename']


# THIS IS THE REWORKED (in August 2020) version
dc = DocumentFeeder(filelist)


start = time.time()
model = gensim.models.Word2Vec(dc, size=vector_size, min_count=2, workers=4, iter=10)
duration = time.time() - start
print(f"It took {duration} sec")
model.save('model_{which_corpus}_{sys.argv[2]}')
import cv2
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.utils import Sequence


IMG_SIZE = 224
BATCH_SIZE = 10

class ImageSequence(Sequence):
    def __init__(self, df):
        self.df = df
        self.indices = np.arange(len(df))
        self.batch_size = BATCH_SIZE
        self.img_dir = "wiki_crop/"
        self.img_size = IMG_SIZE
    def __getitem__(self, idx):
        sample_indices = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]
        imgs = []
        ages = []
        for _, row in self.df.iloc[sample_indices].iterrows():
            img = cv2.imread(self.img_dir + row["img_paths"])
            img = cv2.resize(img, (self.img_size, self.img_size))
            imgs.append(img)
            ages.append(row["ages"])
        imgs = np.asarray(imgs)
        ages = np.asarray(ages)
        # Unlike the sequence of the training we only return the images
        return imgs
    def __len__(self):
        return len(self.df) // self.batch_size
    def on_epoch_end(self):
        np.random.shuffle(self.indices)


def get_mae(y_hat,y):
    '''
    returns the mean absolut error of 02 array
    '''
    return np.sum(np.absolute(y_hat - y))/y.size

model = tf.keras.models.load_model("age_vgg16_224.h5")
wiki = pd.read_csv("meta/wiki.csv")
# shuffle
wiki = wiki.sample(frac = 1)
# taking a very small sample
test = wiki.sample(n = 500)
test_gen = ImageSequence(test)
# saving the probability outputs
classes = model.predict(test_gen)
# extracting the age with highest probability
predictions = tf.argmax(input = classes, axis = 1)
print(get_mae(predictions, test['ages']))


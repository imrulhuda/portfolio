#!/user/ih2344/.conda/envs/tensor/bin/python

import multiprocessing
from pathlib import Path
import cv2
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import Sequence

# setting the the hyperparameters and dataset
DB = "imdb"
IMG_SIZE = 224
BATCH_SIZE = 32
FRAC_SIZE = 0.1
EPOCH_NUM = 4

# A generator class to feed in images to the training function.
# it is derieved from the tensorflow Sequence class
class ImageSequence(Sequence):
    def __init__(self, df):
        self.df = df
        self.indices = np.arange(len(df))
        self.batch_size = BATCH_SIZE
        self.img_dir = Path(__file__).resolve().parents[0].joinpath(f"{DB}_crop")
        self.img_size = IMG_SIZE
    def __getitem__(self, idx):
        sample_indices = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]
        imgs = []
        ages = []
        for _, row in self.df.iloc[sample_indices].iterrows():
            # print(row)
            print(str(self.img_dir.joinpath(row["img_paths"])))
            img = cv2.imread(str(self.img_dir.joinpath(row["img_paths"])))
            # try:
            img = cv2.resize(img, (self.img_size, self.img_size))
            # except Exception as e:
            #     print(str(e))
            #     continue
            imgs.append(img)
            ages.append(row["ages"])
        imgs = np.asarray(imgs)
        ages = np.asarray(ages)
        return imgs, ages
    def __len__(self):
        return len(self.df) // self.batch_size
    def on_epoch_end(self):
        np.random.shuffle(self.indices)

def get_model():
    '''
    this function returns a VGG16 model pretrained on imagenet data
    we freeze further training of the weights
    and we add a dense layer with 99 output neurons - one for each age category
    '''
    base_model = tf.keras.applications.VGG16(
        include_top=False, 
        weights='imagenet', 
        input_tensor=None, 
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        pooling="avg")
    base_model.trainable = False
    features = base_model.output
    pred_age = tf.keras.layers.Dense(units=99, activation="softmax", name="pred_age")(features)
    model = tf.keras.models.Model(inputs=base_model.input, outputs=pred_age)
    return model
 

def main():
    # read data
    df = pd.read_csv(f"meta/{DB}.csv")
    # shuffle the data
    df = df.sample(frac=1).reset_index(drop=True)
    print(f"unique age: {len(set(df['ages']))}")
    # take a 10% sample of the data
    df = df.sample(frac=FRAC_SIZE).reset_index(drop=True)
    # train test split
    train, val = train_test_split(df, random_state=42, test_size=0.1)
    print(f"unique age: {len(set(train['ages']))}")
    print(f"train shape: {train.shape}")
    print(f"val shape: {val.shape}")
    # initiate the generators
    train_gen = ImageSequence(train)
    val_gen = ImageSequence(val)
    # get the model
    model = get_model() 
    model.summary()
    # compile the model
    model.compile(optimizer=tf.keras.optimizers.Adam(lr=0.001),
                  loss="sparse_categorical_crossentropy",
                  metrics=['accuracy'])
    # fit the model
    model.fit(train_gen, epochs=EPOCH_NUM, validation_data=val_gen, workers=multiprocessing.cpu_count())
    # save the model
    model.save("age_vgg16_224.h5")

if __name__ == '__main__':
    main()




class ImageSequence(Sequence):
    def __init__(self, df):
        self.df = df
        self.indices = np.arange(len(df))
        self.batch_size = BATCH_SIZE
        self.img_dir = "wiki_crop"
        self.img_size = IMG_SIZE
    def __getitem__(self, idx):
        sample_indices = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]
        imgs = []
        ages = []
        for _, row in self.df.iloc[sample_indices].iterrows():
            # print(row)
            # print(str(self.img_dir.joinpath(row["img_paths"])))
            img = cv2.imread(str(self.img_dir.joinpath(row["img_paths"])))
            # try:
            img = cv2.resize(img, (self.img_size, self.img_size))
            # except Exception as e:
            #     print(str(e))
            #     continue
            imgs.append(img)
            ages.append(row["ages"])
        imgs = np.asarray(imgs)
        ages = np.asarray(ages)
        return imgs
    def __len__(self):
        return len(self.df) // self.batch_size
    def on_epoch_end(self):
        np.random.shuffle(self.indices)
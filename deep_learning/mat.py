# import the necessary packages
import os
import argparse
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.io import loadmat
from tqdm import tqdm


def calc_age(taken, dob):
    '''
    This function coverts the date from matlab serial date number to human readable format
    and calculates the age
    '''
    birth = datetime.fromordinal(max(int(dob) - 366, 1))
    # assume the photo was taken in the middle of the year
    if birth.month < 7:
        return taken - birth.year
    else:
        return taken - birth.year - 1


def get_meta(mat_path, db):
    '''
    This function loads the matlab data file and 
    returns 07 lists of each variables
    '''
    meta = loadmat(mat_path)
    full_path = meta[db][0, 0]["full_path"][0]
    dob = meta[db][0, 0]["dob"][0]  # Matlab serial date number
    gender = meta[db][0, 0]["gender"][0]
    photo_taken = meta[db][0, 0]["photo_taken"][0]  # year
    face_score = meta[db][0, 0]["face_score"][0]
    second_face_score = meta[db][0, 0]["second_face_score"][0]
    age = [calc_age(photo_taken[i], dob[i]) for i in range(len(dob))]
    return full_path, dob, gender, photo_taken, face_score, second_face_score, age


def get_args():
    '''
    Command line argument parser.
    this allows the user to specify a minimum score for face score 
    also allows the user to choose data between imdb or wiki
    '''
    parser = argparse.ArgumentParser(description="This script cleans-up noisy labels "
                                                 "and creates database for training.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--db", type=str, default="imdb",
                        help="dataset; wiki or imdb")
    parser.add_argument("--min_score", type=float, default=1.0,
                        help="minimum face_score")
    args = parser.parse_args()
    return args


def main():
    # parsing command line aruments
    args = get_args()
    db = args.db
    min_score = args.min_score
    # setting the path
    root_dir = Path(__file__).parent
    data_dir = root_dir.joinpath(f"{db}_crop")
    mat_path = data_dir.joinpath(f"{db}.mat")
    # load matlab data
    full_path, dob, gender, photo_taken, face_score, second_face_score, age = get_meta(mat_path, db)
    # process and filter data
    genders = []
    ages = []
    img_paths = []
    sample_num = len(face_score)
    for i in tqdm(range(sample_num)):
        if face_score[i] < min_score:
            continue
        if (~np.isnan(second_face_score[i])) and second_face_score[i] > 0.0:
            continue
        if ~(0 <= age[i] <= 100):
            continue
        if np.isnan(gender[i]):
            continue
        genders.append(int(gender[i]))
        ages.append(age[i])
        img_paths.append(full_path[i][0])
    # generating output dictionary
    outputs = dict(genders=genders, ages=ages, img_paths=img_paths)
    # set output directory and path
    output_dir = root_dir.joinpath("meta")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir.joinpath(f"{db}.csv")
    df = pd.DataFrame(data=outputs)
    # save data in csv format
    df.to_csv(str(output_path), index=False)


if __name__ == '__main__':
    main()
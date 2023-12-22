import pandas as pd
from sklearn.model_selection import train_test_split

def split(csv_file,save_train_file,save_test_file):

    df = pd.read_csv(csv_file)

    # randomize the data
    df = df.sample(frac=1).reset_index(drop=True)

    # split into train and test sets
    train_df, test_df = train_test_split(df, test_size=0.2)

    # save to csv
    train_df.to_csv(save_train_file, index=False)
    test_df.to_csv(save_test_file, index=False)

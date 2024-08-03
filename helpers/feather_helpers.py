import pyarrow.feather as feather
import pandas as pd


def join_feather_df(feather_file, df):
    f_df = feather.read_feather(feather_file)
    joined_df = pd.concat([f_df, df], axis=1)
    joined_df.drop_duplicates(subset="URL", inplace=True)
    joined_df.to_feather(feather_file)
    print(joined_df)
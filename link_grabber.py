import pandas as pd
from s3 import S3
import os

s3 = S3()

file_path = 'linked\Final_01.05.2022_13.18.48.csv'
df = pd.read_csv(file_path)

for ind, row in df.iterrows():

    if row.Status == 'Success':
        key_prefix = "Air India/"
        filename = row.file

        key = os.path.join(key_prefix, filename)
        file_link = s3.get_link(key)

        df.loc[ind, 'S3_URL'] = file_link

    df.to_csv(file_path.replace('.csv', '_Linked.csv'), index=False)
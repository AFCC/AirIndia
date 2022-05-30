import pandas as pd
from glob import glob
import datetime as dt

main_df = pd.DataFrame()

files = glob('pdf_directory\\dump\\*_final.csv')

for file in files:  
    try:
        temp_df = pd.read_csv(file)
        main_df = main_df.append(temp_df, ignore_index=True)
        main_df.drop_duplicates(subset='Primary_Key', keep="last", inplace=True)
    except:
        pass

main_df.to_csv(f'output\\Output2_{dt.datetime.now().strftime("%d.%m.%Y_%H.%M.%S")}.csv', index=False)

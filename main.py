# ==================================================== import custom libraries ====================================================
from logger import *
from config import *
import pandas as pd
from scraper import Scraper
from glob import glob

import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

executor = ThreadPoolExecutor(10)

def scrape(client, *, loop):
    loop.run_in_executor(executor, Scraper, client[0], client[1])

def job(clients):
    loop = asyncio.get_event_loop()

    for client in clients:
        scrape(client, loop=loop)

    loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop)))

# from zoho import Zoho

# ----------------------------------------- fetch Input1 -----------------------------------------
# z = Zoho()
# login_creds = z.get_input1()
# login_creds.drop(login_creds[login_creds.Status != 'Working'].index, inplace=True)

login_creds = pd.read_csv('temp\Input1.csv')

login_creds['ETID_from'] = pd.to_datetime(login_creds['ETID_from'], format='%d-%m-%Y')
login_creds['ETID_to'] = pd.to_datetime(login_creds['ETID_to'], format='%d-%m-%Y')

clients = []

for i in range(0, len(login_creds)):
    client = [{
        'wrkspc': login_creds.loc[i, 'Workspace'],
        'Login': login_creds.loc[i, 'Login'],
        'Password': login_creds.loc[i, 'Password'],
        'ETID_from':login_creds.loc[i, 'ETID_from'],
        'ETID_to': login_creds.loc[i, 'ETID_to']
    }, dd_prefix + f'worker_{i+1}']

    clients.append(client)

job(clients)

main_df = pd.DataFrame()

files = glob('pdf_directory\\dump\\*_final.csv')

for file in files:  
    try:
        temp_df = pd.read_csv(file)
        main_df = main_df.append(temp_df, ignore_index=True)
        main_df.drop_duplicates(subset='Primary_Key', keep="last", inplace=True)
    except:
        pass

main_df.to_csv(f'output\\Output1.csv', index=False)
# ==================================================== import libraries ====================================================
import time, os, copy
from random import randint
import pandas as pd

from config import *
from logger import *
from browser import *

# ==================================================== helper methods ====================================================
def download_wait(path_to_downloads):
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < waiting_time:
        time.sleep(1)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload'):
                dl_wait = True
        seconds += 1
    return seconds

def month_name(num):
    month_dict = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    return month_dict[num]

# ==================================================== scraper ====================================================
def CredChecker(client, download_dir):
    cred_data = {
        'Login': client['Login'],
        'Password': client['Password'],
        'Status': '',
        'PAN': client['PAN'],
        'ETID_from': client['ETID_from'],
        'ETID_to': client['ETID_to'],
        
        'Record Count': ''
    }

    driver = Browser(download_dir).worker()
    driver.get(target_url)

    wait = WebDriverWait(driver, 10)

    try:
        driver.find_element_by_id('userName').send_keys(client['Login'])
        driver.find_element_by_id('password').send_keys(client['Password'])

        driver.find_element_by_id('loginForm_login').click()

        try:
            driver.get(search_url)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ms-choice')))
            driver.find_element_by_class_name('ms-choice').click()
            cred_data['Status'] = 'Working'

        except Exception as e:
            try:
                driver.find_element(by=By.ID, value='sessionConfirmAlertForm_sessionYesButton').click()
                time.sleep(2)
                driver.find_element(by=By.CLASS_NAME, value='fa-window-close').click()

                driver.get(search_url)
                wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'ms-choice')))
                driver.find_element_by_class_name('ms-choice').click()
                cred_data['Status'] = 'Working'
                
            except Exception as e:
                logging.info(f'Error# (Login Error / DropDown Error): {str(e)}')
                cred_data['Status'] = 'Not Working'

        try: 
            not_selected = driver.find_element_by_class_name('placeholder')
        except Exception as e:
            logging.info(f'Error#3 (Checkbox Error): {str(e)}')
            not_selected = None
        
        try:
            if not_selected:
                driver.find_element_by_xpath('//*[@id="searchSection_searchSectionFieldSet"]/div[2]/div[2]/div/div/div/ul/li[1]/label/input').click()

            yearFrom = str(client['ETID_from'].year)
            monthFrom = month_name(client['ETID_from'].month)
            dayFrom = str(client['ETID_from'].day)
            dateFrom = driver.find_element_by_id('issue_date_form')
            dateFrom.click()
            driver.find_element_by_xpath(f'//*[@id="ui-datepicker-div"]/div/div/select[1]/option[text()="{monthFrom}"]').click()
            driver.find_element_by_xpath(f'//*[@id="ui-datepicker-div"]/div/div/select[2]/option[text()="{yearFrom}"]').click()
            driver.find_element(by=By.LINK_TEXT, value=dayFrom).click()

            yearTo = str(client['ETID_to'].year)
            monthTo = month_name(client['ETID_to'].month)
            dayTo = str(client['ETID_to'].day)
            dateTo = driver.find_element_by_id('issue_date_to')
            dateTo.click()
            driver.find_element_by_xpath(f'//*[@id="ui-datepicker-div"]/div/div/select[1]/option[text()="{monthTo}"]').click()
            driver.find_element_by_xpath(f'//*[@id="ui-datepicker-div"]/div/div/select[2]/option[text()="{yearTo}"]').click()
            driver.find_element(by=By.LINK_TEXT, value=dayTo).click()
        except Exception as e:
            logging.info(f'Error#4 (Field Inputs Error): {str(e)}')
    
        try:
            driver.find_element_by_id('Search').click()
            time.sleep(randint(sd_s, sd_e))
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'records')))
            
            records = driver.find_element_by_class_name('records').text.split(' ')[0]
            cred_data['Record Count'] = records
            
        except Exception as e:
            logging.info(f'Error#5 (Search Page Error): {str(e)}')

    except Exception as e:
        logging.info(f'Error# (Full Error): {str(e)}')

    finally:
        try:
            cred_dump.append(copy.deepcopy(cred_data))
            cred_df = pd.DataFrame(copy.deepcopy(cred_dump))

            wk = download_dir.split('\\')[-1]
            cred_df.to_csv(f'{creds}\\{wk}_creds_temp.csv', index=False)
            try:
                driver.find_element_by_class_name('loginUserName').click()
                time.sleep(randint(sd_s, sd_e))
                wait.until(EC.visibility_of_element_located((By.LINK_TEXT, 'Logout')))
                driver.find_element_by_link_text('Logout').click()
            except Exception as e:
                logging.info(f'Error# Log Out: {str(e)}')

            driver.close()
            driver.quit()

        except Exception as e:
            logging.info(f'Error#Finally: {str(e)}')
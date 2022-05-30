# ==================================================== import libraries ====================================================
import time, os, math, subprocess, copy
from random import randint
import datetime as dt
import pandas as pd

from config import *
from logger import *
from browser import *
from s3 import S3

s3 = S3()

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
def Scraper(client, download_dir):
    try:
        file_list = []

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

            except Exception as e:
                logging.info(f'Error# (Login Error / DropDown Error): {str(e)}')

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
                tot_pages = math.floor(int(records)/15)
                pages = math.floor(int(records)/15)
                
                ## =============================================== CODE BEGINS =================================================================
                ## =============================================================================================================================
                file = {
                    "Workspace": client['wrkspc'],
                    "Login": client['Login'],
                    "Password": client['Password'],
                    "Status": "",
                    "Remark": "",

                    "GSTIN Number": "",
                    "E-Ticket Number": "",
                    "E-Ticket Issue Date": "",
                    "Ticket Upload Date": "",
                    "Invoice Details": "",

                    "Ticket Number": "",
                    "Invoice Issue Date": "",
                    "Invoice Number": "",

                    "file": "",
                    "S3_URL": "",
                    "timestamp": "",

                    "Primary_Key": ""
                }
                exception_tickets = []
                while pages >= 0:
                    temp_file_list = []
                    # if pages >= math.floor(int(records)/15)-1:
                    #     driver.find_element_by_class_name('fa-step-forward').click()
                    #     time.sleep(randint(sd_s, sd_e))
                    #     pages -= 1
                    #     continue

                    try:
                        wait.until(EC.visibility_of_element_located((By.ID, 'TicketDetailListSection_body')))
                        rows_raw = driver.find_element(by=By.ID, value='TicketDetailListSection_body').find_elements(by=By.TAG_NAME, value='tr')
                        
                        rows = []
                        for row_raw in rows_raw:
                            popup_link = row_raw.find_elements(by=By.TAG_NAME , value='td')[-1]

                            if popup_link.text == 'Click to View Invoice':
                                rows.append(row_raw)

                            else:
                                file["GSTIN Number"] = row_raw.find_elements(by=By.TAG_NAME , value='td')[1].text
                                file["E-Ticket Number"] = row_raw.find_elements(by=By.TAG_NAME , value='td')[2].text
                                file["E-Ticket Issue Date"] = row_raw.find_elements(by=By.TAG_NAME , value='td')[3].text
                                file["Ticket Upload Date"] = row_raw.find_elements(by=By.TAG_NAME , value='td')[4].text
                                file["Invoice Details"] = row_raw.find_elements(by=By.TAG_NAME , value='td')[5].text
                                file["Status"] = "Failed"
                                file["Remark"] = popup_link.text

                                temp_file_list.append(copy.deepcopy(file))
                                logging.info(f'##NoPopupLink')


                    except Exception as e:
                        logging.info(f'Error# (Main Table Error): {str(e)}')

                    # temp_file_list = []
                    try:
                        ISE_excp = False
                        for row in rows:
                            file = {
                                "Workspace": client['wrkspc'],
                                "Login": client['Login'],
                                "Password": client['Password'],
                                "Status": "",
                                "Remark": "",

                                "GSTIN Number": "",
                                "E-Ticket Number": "",
                                "E-Ticket Issue Date": "",
                                "Ticket Upload Date": "",
                                "Invoice Details": "",

                                "Ticket Number": "",
                                "Invoice Issue Date": "",
                                "Invoice Number": "",

                                "file": "",
                                "S3_URL": "",
                                "timestamp": "",

                                "Primary_Key": ""
                            }

                            file["GSTIN Number"] = row.find_elements(by=By.TAG_NAME , value='td')[1].text
                            file["E-Ticket Number"] = row.find_elements(by=By.TAG_NAME , value='td')[2].text
                            file["E-Ticket Issue Date"] = row.find_elements(by=By.TAG_NAME , value='td')[3].text
                            file["Ticket Upload Date"] = row.find_elements(by=By.TAG_NAME , value='td')[4].text
                            file["Invoice Details"] = row.find_elements(by=By.TAG_NAME , value='td')[5].text
                            
                            # try:
                            #     popup_link = row.find_elements(by=By.TAG_NAME , value='td')[-1]

                            #     if popup_link.text == 'Not Generated':
                            #         file["Status"] = "Failed"
                            #         file["Remark"] = "Not Generated"

                            #         temp_file_list.append(copy.deepcopy(file))
                            #         logging.info(f'##NotGenerated')
                            #         continue # skip row - Not Generated

                            # except Exception as e:
                            #     logging.info(f'Error# (Not Generated): {str(e)}')

                            try:
                                popup_link = row.find_elements(by=By.TAG_NAME , value='td')[-1]
                                popup_link.click()
                                wait.until(EC.visibility_of_element_located((By.ID, 'invoiceDialog')))
                                ticket_rows = driver.find_element_by_id('invoiceListSection_body').find_elements(by=By.TAG_NAME, value='tr')
                            except Exception as e:
                                logging.info(f'Error# (Popup Table Error): {str(e)}')

                            for ticket_row in ticket_rows:
                                timestamp = dt.datetime.now().strftime("%d.%m.%Y_%H.%M.%S")
                                
                                file["Ticket Number"] = ticket_row.find_elements(by=By.TAG_NAME , value='td')[0].text     
                                file["Invoice Issue Date"] = ticket_row.find_elements(by=By.TAG_NAME , value='td')[1].text
                                file["Invoice Number"] = ticket_row.find_elements(by=By.TAG_NAME , value='td')[2].text

                                primary_key = f'{file["GSTIN Number"]}_{file["Invoice Number"]}_{file["Ticket Number"]}'

                                file["Primary_Key"] = primary_key

                                if primary_key in exception_tickets:
                                    file["Status"] = "Failed"
                                    file["Remark"] = "Air India - Internal Server Error"
                                    temp_file_list.append(copy.deepcopy(file))
                                    continue

                                try:     
                                    ticket_download = ticket_row.find_elements(by=By.TAG_NAME , value='td')[3]
                                    ticket_download.click()
        
                                    download_wait(download_dir)
                                    time.sleep(randint(sd_s, sd_e))

                                    default_file = max([download_dir + '\\' + f for f in os.listdir(download_dir)], key=os.path.getctime)

                                    local_filename = f'{primary_key}_{timestamp}.pdf'
                                    local_filepath = os.path.join(dump, local_filename)
                                    
                                    subprocess.call('move ' + default_file + ' ' + local_filepath, shell=True)
                                    time.sleep(randint(sd_s, sd_e))

                                    s3.upload(local_filepath, s3_creds["folder"] + local_filename)

                                    file["Status"] = "Success"
                                    file["Remark"] = ""
                                    file["S3_URL"] = s3.get_link(s3_creds["folder"] + local_filename)
                                    file["file"] = local_filename
                                    file["timestamp"] = timestamp

                                    temp_file_list.append(copy.deepcopy(file))
          
                                except Exception as e:
                                    try:
                                        logging.info(f'Error# Exception s3 upload block: {str(e)}')
                                        driver.find_element(by=By.CLASS_NAME, value='btn-danger').click()
                                        driver.get(search_url)
                                        exception_tickets.append(primary_key)

                                        ISE_excp = True

                                        break #break ticket popup loop

                                    except Exception as e:
                                        logging.info(f'Error# (Popup Rows Error): {str(e)}')
                                        file["Status"] = "Failed"
                                        file["Remark"] = "Popup Row Error"

                                        temp_file_list.append(copy.deepcopy(file))

                            try:
                                driver.find_element_by_xpath('/html/body/div[5]/div[1]/button').click()
                                time.sleep(randint(sd_s, sd_e))
                            except Exception as e:
                                logging.info(f'Error# (Popup Close Error): {str(e)}')

                            if ISE_excp:
                                break #break main record row loop
                                     
                        if ISE_excp:
                            continue # skip click next page

                    except Exception as e:
                        logging.info(f'Error# (Main Rows Error): {str(e)}')

                    try:
                        driver.find_element_by_class_name('fa-step-forward').click()
                        time.sleep(randint(sd_s, sd_e))
                        pages -= 1

                        temp_file_df = pd.DataFrame(copy.deepcopy(temp_file_list))

                        wk = download_dir.split('\\')[-1]
                        temp_file_df.to_csv(f'{dump}\\{wk}_temp_{tot_pages-pages}.csv', index=False)
                        file_list.extend(copy.deepcopy(temp_file_list))
                    except Exception as e:
                        logging.info(f'Error# (Next Page Error): {str(e)}')
                
            except Exception as e:
                logging.info(f'Error#5 (Search Page Error): {str(e)}')

        except Exception as e:
            logging.info(f'Error# (Full Error): {str(e)}')
        
        finally:
            try:
                driver.find_element_by_class_name('loginUserName').click()
                time.sleep(randint(sd_s, sd_e))
                wait.until(EC.visibility_of_element_located((By.LINK_TEXT, 'Logout')))
                driver.find_element_by_link_text('Logout').click()

                file_df = pd.DataFrame(copy.deepcopy(file_list))

                wk = download_dir.split('\\')[-1]
                file_df.to_csv(f'{dump}\\{wk}_final.csv', index=False)

                driver.close()
                driver.quit()

            except Exception as e:
                logging.info(f'Error#Finally: {str(e)}')

    except Exception as e:
        logging.info(f'Error# (Main Scraper Error): {str(e)}')
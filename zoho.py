from __future__ import with_statement
from AnalyticsClient import AnalyticsClient
import pandas as pd

class Zoho:
    def __init__(self) -> None:
        self.CLIENTID = '1000.TOB9YU8ZDKR5HBYFHWEGQUO92ARGWN'
        self.CLIENTSECRET = '661ea92c64c5f1daa816c33a893abf46ebacf167e7'
        self.REFRESHTOKEN = '1000.7d29fb8ca61362db4edc5cfbea0d9648.2f6edfa4ba447d2459e2750e23336749'

        self.ORGID = "60000460986"
        self.WORKSPACEID = "103074000002015532"

        self.VIEWID_AirIndiaInput1 = "103074000004199104"

        self.VIEWID_AirIndiaOutput1 = "103074000014476528"
        self.VIEWID_AirIndiaOutput2 = "103074000014249442"

        self.ac = AnalyticsClient(self.CLIENTID, self.CLIENTSECRET, self.REFRESHTOKEN)
    
    def get_input1(self):
        response_format = "csv"
        file_path = "temp/Input1.csv"
        bulk = self.ac.get_bulk_instance(self.ORGID, self.WORKSPACEID)
        bulk.export_data(self.VIEWID_AirIndiaInput1, response_format, file_path)
        df = pd.read_csv(file_path)
        return df


    def send_output1(self):
        import_type = "updateadd"
        file_type = "csv"
        auto_identify = "true"
        file_path = "output/Output1.csv"
        matchingColumns = ["Primary_Key"]
        bulk = self.ac.get_bulk_instance(self.ORGID, self.WORKSPACEID)
        result = bulk.import_data(self.VIEWID_AirIndiaOutput1, import_type, file_type, auto_identify, file_path, config = {'matchingColumns':matchingColumns})        
        return result

    def send_output2(self):
        import_type = "updateadd"
        file_type = "csv"
        auto_identify = "true"
        file_path = "output/Output2.csv"
        matchingColumns = ["Login"]
        bulk = self.ac.get_bulk_instance(self.ORGID, self.WORKSPACEID)
        result = bulk.import_data(self.VIEWID_AirIndiaOutput2, import_type, file_type, auto_identify, file_path, config = {'matchingColumns':matchingColumns})        
        return result
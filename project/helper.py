import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

KEY_SHEET = os.getenv("KEY_SHEET")
ASISTENCIAS_SHEET = 'asistencias'
CHAT_SHEET = 'chat'

# CREDS_JSON = 'access-key.json'
CREDS_JSON = 'nosayudamostelegram-93e32801e0a5.json'


class gsheet_helper:
    def __init__(self):
        scope = ["https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive.file",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            CREDS_JSON,
            scope
        )

        self.client = gspread.authorize(creds)
        self.gsheet = self.client.open_by_key(KEY_SHEET)

    def get_chat(self):
        items = self.get_sheet(CHAT_SHEET)
        output = []
        for index, row in items.iterrows():
            output.append(row)
        return output
    
    def get_asistencia(self, category, city=None):
        items = self.get_sheet(ASISTENCIAS_SHEET)
        if city != None:
            items = items.loc[(items['CATEGORY'] == category) & (items['CITY'].str.contains(city))]
        else:
            items = items.loc[items['CATEGORY'] == category]
        items = items.drop(columns=['ID', 'CATEGORY'])
        return items

    def get_cities(self):
        items = self.get_sheet(ASISTENCIAS_SHEET)
        items = items[['CITY']]
        output = set()
        for index, row in items.iterrows():
            item = row['CITY'].split(",")
            for i in item:
                if i not in output and i != '': 
                    output.add(i)
        return output

    def get_sheet(self, sheet_name):
        sheet = self.gsheet.worksheet(sheet_name)
        items = pd.DataFrame(sheet.get_all_records())
        return items


if __name__ == "__main__":
    print(gsheet_helper().get_chat())
    items = gsheet_helper().get_chat()
    print(type(items))
    print(items[0])
    